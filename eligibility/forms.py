from requests.exceptions import HTTPError

from django import forms

from core.constants import ASSURANCE_LEVEL_TWO
from core.helpers import decode_saml_response
from eligibility import constants


class SAMLResponseForm(forms.Form):
    INVALID_SAML = 'Invalid SAML'
    UNSUPPORTED_SCENARIO = 'This scenario is not supported'
    UNSUPPORTED_LEVEL = 'This level is not supported'

    SAMLResponse = forms.CharField()

    def __init__(self, request_id, *args, **kwargs):
        self.request_id = request_id
        super().__init__(*args, **kwargs)

    def clean_SAMLResponse(self):
        try:
            message = decode_saml_response(
                saml=self.cleaned_data['SAMLResponse'],
                request_id=self.request_id,
            )
        except HTTPError:
            raise forms.ValidationError(self.INVALID_SAML)
        else:
            if message['scenario'] != constants.ACCOUNT_CREATION:
                raise forms.ValidationError(self.UNSUPPORTED_SCENARIO)
            if message['levelOfAssurance'] != ASSURANCE_LEVEL_TWO:
                raise forms.ValidationError(self.UNSUPPORTED_LEVEL)
        return message

    def get_user_attributes(self):
        assert 'SAMLResponse' in self.cleaned_data
        message = self.cleaned_data['SAMLResponse']
        form = CheckIsCompanyOfficerForm(data={
            'first_name': message['attributes']['firstName']['value'],
            'surname': message['attributes']['surname']['value'],
            'birth_date': message['attributes']['dateOfBirth']['value'],
            'pid': message['pid'],
        })
        assert form.is_valid()
        return form.cleaned_data


class CheckIsCompanyOfficerForm(forms.Form):
    first_name = forms.CharField()
    surname = forms.CharField()
    birth_date = forms.DateField()
    pid = forms.CharField()
