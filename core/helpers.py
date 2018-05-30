import json
from urllib.parse import urljoin, urlencode

import requests
from directory_api_client.client import DirectoryAPIClient
from directory_ch_client.client import DirectoryCHClient

from django.conf import settings

from core import constants, helpers


companies_house_client = DirectoryCHClient(
    base_url=settings.INTERNAL_CH_BASE_URL,
    api_key=settings.INTERNAL_CH_API_KEY
)

api_client = DirectoryAPIClient(
    base_url=settings.API_CLIENT_BASE_URL,
    api_key=settings.API_SIGNATURE_SECRET,
)


def generate_gov_verify_saml_request():
    response = requests.post(
        urljoin(settings.VERIFY_SERVICE_PROVIDER_URL, 'generate-request'),
        json.dumps({'levelOfAssurance': constants.ASSURANCE_LEVEL_TWO}),
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    return response.json()


def decode_saml_response(saml, request_id):
    data = json.dumps({
        'samlResponse': saml,
        'levelOfAssurance': constants.ASSURANCE_LEVEL_TWO,
        'requestId': request_id
    })
    response = requests.post(
        urljoin(settings.VERIFY_SERVICE_PROVIDER_URL, 'translate-response'),
        data,
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    return response.json()


def generate_gov_verify_compliance_test_suite():
    configure_compliance_tool_response()

    verify_provider_response = helpers.generate_gov_verify_saml_request()
    querystring = '?' + urlencode({
        'SAMLRequest': verify_provider_response['samlRequest']
    })
    response = requests.post(
        settings.COMPLIANCE_TOOL_SSO_URL + querystring,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    response.raise_for_status()
    url = response.json()['responseGeneratorLocation']
    return verify_provider_response['requestId'], url


def configure_compliance_tool_response():
    data = {
        'serviceEntityId': settings.COMPLIANCE_TOOL_CONSUMER_SERVICE_URL,
        'assertionConsumerServiceUrl': (
            settings.COMPLIANCE_TOOL_CONSUMER_SERVICE_URL
        ),
        'signingCertificate': settings.COMPLIANCE_TOOL_SIGNING_CERTIFICATE,
        'encryptionCertificate': (
            settings.COMPLIANCE_TOOL_ENCRYPTION_CERTIFICATE
        ),
        'expectedPID': '123',
        'matchingServiceEntityId': (
            settings.COMPLIANCE_TOOL_MATCHING_SERVICE_ENTITY_ID
        ),
        'matchingServiceSigningPrivateKey': (
            settings.VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY
        ),
        'userAccountCreationAttributes': [
            'FIRST_NAME',
            'FIRST_NAME_VERIFIED',
            'SURNAME',
            'SURNAME_VERIFIED',
            'DATE_OF_BIRTH',
            'DATE_OF_BIRTH_VERIFIED'
        ]
    }
    response = requests.post(
        settings.COMPLIANCE_TOOL_SET_TEST_DATA_URL,
        json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()


def get_session_request_id(request):
    return request.session[constants.SAML_REQUEST_ID_KEY]
