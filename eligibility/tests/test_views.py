from datetime import datetime
from unittest.mock import call, Mock, patch

import pytest
from requests.exceptions import HTTPError

from django.urls import reverse

from eligibility import views
from sso.utils import SSOUser


@pytest.fixture
def logged_in_client(client):
    def process_request(self, request):
        request.sso_user = sso_user()

    stub = patch(
        'sso.middleware.SSOUserMiddleware.process_request', process_request
    )
    stub.start()
    yield client
    stub.stop()


@pytest.fixture
def sso_user():
    return SSOUser(
        id=1,
        email='jim@example.com',
        session_id='213'
    )


@pytest.fixture(autouse=True)
def mock_get_session_request_id():
    stub = patch(
        'eligibility.views.get_session_request_id', Mock(return_value='789')
    )
    stub.start()
    yield stub
    stub.stop()


@pytest.fixture(autouse=True)
def mock_get_company_details():
    stub = patch(
        'eligibility.views.CheckIsCompanyOfficerView.get_company_details',
        Mock(return_value={'number': '12345678'})
    )
    stub.start()
    yield stub
    stub.stop()


def test_test_is_company_officer_anon_user(client):
    url = reverse('eligibility-check')
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == (
        'http://sso.trade.great:8004/accounts/login/'
        '?next=http%3A//testserver/eligibility-check/'
    )


def test_is_company_officer_unsupported_methods(logged_in_client):
    url = reverse('eligibility-check')
    response = logged_in_client.get(url)

    assert response.status_code == 405


def test_is_company_officer_missing_saml(logged_in_client):
    url = reverse('eligibility-check')
    response = logged_in_client.post(url)

    assert response.status_code == 200
    assert response.context['form'].is_valid() is False
    assert response.template_name == (
        views.CheckIsCompanyOfficerView.failure_template_name
    )


@patch('eligibility.forms.decode_saml_response', Mock(side_effect=HTTPError()))
def test_is_company_officer_invalid_saml(logged_in_client):
    url = reverse('eligibility-check')
    response = logged_in_client.post(url, {'SAMLResponse': '123'})

    assert response.status_code == 200
    assert response.context['form'].is_valid() is False
    assert response.template_name == (
        views.CheckIsCompanyOfficerView.failure_template_name
    )


@pytest.mark.parametrize('is_probably_company_officer,expected_template', (
    (False, views.CheckIsCompanyOfficerView.failure_template_name),
    (True, views.CheckIsCompanyOfficerView.success_template_name),
))
@patch('eligibility.helpers.is_probably_company_officer')
@patch('eligibility.forms.decode_saml_response')
def test_is_company_officer_valid_body_not_officer(
    mock_decode_saml_response, mock_is_probably_company_officer,
    logged_in_client, is_probably_company_officer, expected_template
):
    mock_decode_saml_response.return_value = {
        'attributes':  {
            'firstName': {'value': 'Jim'},
            'surname': {'value': 'Example'},
            'dateOfBirth': {'value': '1908-05-27'},
        }
    }
    mock_is_probably_company_officer.return_value = is_probably_company_officer

    url = reverse('eligibility-check')
    response = logged_in_client.post(url, {'SAMLResponse': '123'})

    assert mock_decode_saml_response.call_count == 1
    assert mock_decode_saml_response.call_args == call(
        saml='123', request_id='789'
    )

    assert mock_is_probably_company_officer.call_count == 1
    assert mock_is_probably_company_officer.call_args == call(
        first_name='Jim',
        surname='Example',
        birth_date=datetime(1908, 5, 27),
        company_number='12345678',
    )

    assert response.status_code == 200
    assert response.template_name == expected_template
