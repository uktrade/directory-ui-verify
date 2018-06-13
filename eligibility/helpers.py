import logging

from fuzzywuzzy import fuzz
from requests.exceptions import HTTPError

from django.conf import settings
from django.core.cache import cache

from core.helpers import companies_house_client


logger = logging.getLogger(__name__)
csv_logger = logging.getLogger('csv_match_logger')


class MatchError(ValueError):
    pass


class Officer:
    name_delimiter = ', '

    def __init__(self, companies_house_data):
        self.companies_house_data = companies_house_data

    @property
    def name(self):
        return self.companies_house_data['name'].lower()

    @property
    def first_name(self):
        if self.name_delimiter in self.name:
            return self.name.split(self.name_delimiter)[1]

    @property
    def surname(self):
        if self.name_delimiter in self.name:
            return self.name.split(self.name_delimiter)[0]

    @property
    def birth_date(self):
        # date of birth is optional field in the API
        return self.companies_house_data.get('date_of_birth')

    @property
    def birth_year(self):
        return self.birth_date['year'] if self.birth_date else None

    @property
    def birth_month(self):
        return self.birth_date['month'] if self.birth_date else None

    @property
    def is_active(self):
        # `resigned_on` is only present if the officer has left their post
        resigned_date = self.companies_house_data.get('resigned_on')
        return not bool(resigned_date)

    def is_born_on(self, birth_date):
        return (
            self.birth_year == birth_date.year and
            self.birth_month == birth_date.month
        )

    def get_first_name_score(self, first_name):
        score = fuzz.token_sort_ratio(self.first_name, first_name)
        logger.info(f'Score {score} for {self.first_name} and {first_name}.')
        csv_logger.info(f'FIRST_NAME|{self.first_name}|{first_name}|{score}')
        return score

    def get_surname_score(self, surname):
        score = fuzz.token_sort_ratio(self.surname, surname)
        logger.info(f'Score {score} for {self.surname} and {surname}.')
        csv_logger.info(f'SURNAME|{self.surname}|{surname}|{score}')
        return score


class OfficerCollection(list):

    def exclude_inactive_officers(self):
        return OfficerCollection(
            [officer for officer in self if officer.is_active]
        )

    def filter_birth_date(self, birth_date):
        return OfficerCollection(
            [officer for officer in self if officer.is_born_on(birth_date)]
        )

    def filter_name(self, first_name, surname):
        min_first_name_score = settings.FUZZY_MATCH_MINIMUM_FIRST_NAME_SCORE
        min_surname_score = settings.FUZZY_MATCH_MINIMUM_SURNAME_SCORE
        return OfficerCollection([
            item for item in self
            if item.get_surname_score(surname) >= min_surname_score
            and item.get_first_name_score(first_name) >= min_first_name_score
        ])

    def first(self):
        if len(self) == 0:
            raise MatchError('No matches')
        return self[0]

    def get(self):
        if len(self) == 0:
            raise MatchError('No matches')
        elif len(self) > 1:
            raise MatchError('Multiple matches')
        else:
            return self.first()


class OfficerDataSource:

    @classmethod
    def get_officers(cls, company_number):
        if settings.FEATURE_OFFICER_CACHE_ENABLED:
            officers = cls.get_officers_from_cache_or_source(company_number)
        else:
            officers = cls.get_officers_from_source(company_number)
        return OfficerCollection(map(Officer, officers))

    @classmethod
    def get_officers_from_cache_or_source(cls, company_number):
        cache_key = str(company_number)
        officers = cache.get(cache_key)
        if not officers:
            officers = cls.get_officers_from_source(company_number)
            cache.set(cache_key, officers, None)
        return officers

    @staticmethod
    def get_officers_from_source(company_number):
        response = companies_house_client.company.list_officers(company_number)
        try:
            response.raise_for_status()
        except HTTPError:
            csv_logger.info(f'COMPANY_MISS|{company_number}')
            officers = []
        else:
            officers = response.json()['items']
        return officers


def is_probably_company_officer(
    first_name, surname, birth_date, company_number
):
    #  For use during verify demo. To be removed post-demo
    if settings.FEATURE_FORCE_MATCH_ENABLED:
        logger.warning('Force match enabled')
        return company_number == settings.FORCE_MATCH_COMPANY_NUMBER

    officers = (
        OfficerDataSource
        .get_officers(company_number)
        .exclude_inactive_officers()
        .filter_birth_date(birth_date)
        .filter_name(first_name=first_name, surname=surname)
    )
    name = f'{first_name} {surname}'
    try:
        officer = officers.get()
    except MatchError as error:
        csv_logger.info(f'NO_COMPANY_MATCH|{name}|{company_number}|{error}')
        logger.warning(f'{error} for {name} in {company_number}')
        return False
    else:
        first_name_score = officer.get_first_name_score(first_name)
        surname_score = officer.get_surname_score(surname)
        logger.info(
            f'{name} match found for {company_number}. '
            f'Scores: {first_name_score} {surname_score}'
        )
        csv_logger.info(
            f'COMPANY_MATCH|{name}|{company_number}|'
            '{first_name_score}|{surname_score}'
        )
        return True
