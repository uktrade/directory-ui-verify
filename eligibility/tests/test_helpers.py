import datetime
from unittest.mock import patch

import pytest

from core.tests.helpers import create_response
from eligibility import helpers


@pytest.mark.parametrize('status_code', [400, 404, 500])
@patch('core.helpers.companies_house_client.company.list_officers')
def test_is_probably_company_officer_no_company(
    mock_list_officers, status_code
):
    mock_list_officers.return_value = create_response(status_code=status_code)

    actual = helpers.is_probably_company_officer(
        first_name='Jim',
        surname='Example',
        birth_date=datetime.date(1990, 1, 1),
        company_number=12345678
    )

    assert actual is False


@patch('core.helpers.companies_house_client.company.list_officers')
def test_is_probably_company_officer_date_match(mock_list_officers, caplog):
    mock_list_officers.return_value = create_response(json_body={
        'items': [
            {
                'name': 'FOOD, Fred',
                'date_of_birth': {
                    'month': 1,
                    'year': 1990
                 },
            }
        ]
    })

    actual = helpers.is_probably_company_officer(
        first_name='Jim',
        surname='Example',
        birth_date=datetime.date(1990, 1, 1),
        company_number=12345678
    )

    assert actual is False

    log = caplog.records[-1]
    assert log.levelname == 'WARNING'
    assert log.msg == 'No matches for Jim Example in 12345678'


@patch('core.helpers.companies_house_client.company.list_officers')
def test_is_probably_company_officer_name_match(mock_list_officers, caplog):
    mock_list_officers.return_value = create_response(json_body={
        'items': [
            {
                'name': 'EXAMPLE, Jim',
                'date_of_birth': {
                    'month': 1,
                    'year': 1991
                 },
            }
        ]
    })

    actual = helpers.is_probably_company_officer(
        first_name='Jim',
        surname='Example',
        birth_date=datetime.date(1990, 1, 1),
        company_number=12345678
    )

    assert actual is False

    log = caplog.records[-1]
    assert log.levelname == 'WARNING'
    assert log.msg == 'No matches for Jim Example in 12345678'


@patch('core.helpers.companies_house_client.company.list_officers')
def test_is_probably_company_officer_match(mock_list_officers, caplog):
    mock_list_officers.return_value = create_response(json_body={
        'items': [
            {
                'name': 'EXAMPLE, Jim',
                'date_of_birth': {
                    'month': 1,
                    'year': 1990
                 },
            }
        ]
    })

    actual = helpers.is_probably_company_officer(
        first_name='Jim',
        surname='Example',
        birth_date=datetime.date(1990, 1, 1),
        company_number=12345678
    )

    assert actual is True

    log = caplog.records[-1]
    assert log.levelname == 'INFO'
    assert log.msg == 'Jim Example match found for 12345678. Scores: 100 100'


@patch('core.helpers.companies_house_client.company.list_officers')
def test_is_probably_company_officer_name_fuzzy(mock_list_officers, caplog):
    mock_list_officers.return_value = create_response(json_body={
        'items': [
            {
                'name': 'MACDONALD, Jim',
                'date_of_birth': {
                    'month': 1,
                    'year': 1990
                 },
            }
        ]
    })

    actual = helpers.is_probably_company_officer(
        first_name='jim',
        surname='MCDONALD',
        birth_date=datetime.date(1990, 1, 1),
        company_number=12345678
    )

    assert actual is True

    log = caplog.records[-1]
    assert log.levelname == 'INFO'
    assert log.msg == 'jim MCDONALD match found for 12345678. Scores: 100 94'


@patch('core.helpers.companies_house_client.company.list_officers')
def test_is_probably_company_officer_multiple(mock_list_officers, caplog):
    mock_list_officers.return_value = create_response(json_body={
        'items': [
            {
                'name': 'EXAMPLE, Jim',
                'date_of_birth': {
                    'month': 1,
                    'year': 1990
                 },
            },
            {
                'name': 'EXAMPLE, Jim',
                'date_of_birth': {
                    'month': 1,
                    'year': 1990
                 },
            }
        ]
    })

    actual = helpers.is_probably_company_officer(
        first_name='Jim',
        surname='Example',
        birth_date=datetime.date(1990, 1, 1),
        company_number=12345678
    )

    assert actual is False

    log = caplog.records[-1]
    assert log.levelname == 'WARNING'
    assert log.msg == 'Multiple matches for Jim Example in 12345678'


@pytest.mark.parametrize('company_number,expected', (
    ('1234567', True),
    ('1234568', False)
))
def test_force_match(settings, company_number, expected, caplog):
    settings.FEATURE_FORCE_MATCH_ENABLED = True
    settings.FORCE_MATCH_COMPANY_NUMBER = '1234567'

    actual = helpers.is_probably_company_officer(
        first_name='Jim',
        surname='Example',
        birth_date=datetime.date(1990, 1, 1),
        company_number=company_number
    )

    assert actual is expected

    log = caplog.records[-1]
    assert log.levelname == 'WARNING'
    assert log.msg == 'Force match enabled'
