import datetime

from requests.exceptions import HTTPError

from django import forms

from core.helpers import decode_saml_response


class CheckIsCompanyOfficerForm(forms.Form):
    INVALID_SAML = 'Invalid SAML'

    SAMLResponse = forms.CharField()

    # these are extracted from SAMLResponse in `clean`
    first_name = forms.CharField(required=False)
    surname = forms.CharField(required=False)
    birth_date = forms.DateField(required=False)

    def __init__(self, request_id, *args, **kwargs):
        self.request_id = request_id
        super().__init__(*args, **kwargs)

    def clean_SAMLResponse(self):
        try:
            message = decode_saml_response(
                saml=self.cleaned_data['SAMLResponse'],
                request_id=self.request_id
            )
        except HTTPError:
            raise forms.ValidationError(self.INVALID_SAML)
        else:
            return message

    def clean(self):
        cleaned_data = super().clean()
        if 'SAMLResponse' in cleaned_data:
            attributes = cleaned_data['SAMLResponse']['attributes']
            cleaned_data.update({
                'first_name': attributes['firstName']['value'],
                'surname': attributes['surname']['value'],
                'birth_date': datetime.datetime.strptime(
                    attributes['dateOfBirth']['value'], '%Y-%m-%d'
                ),
            })
        return cleaned_data
