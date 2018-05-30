from django.views.generic.base import TemplateView

from core import constants, helpers


class CheckIsCompanyDirectorView(TemplateView):
    def post(self, request, **kwargs):
        request_id = self.request.session[constants.SAML_REQUEST_ID_KEY]
        helpers.decode_saml_response(
            saml=request.POST['SAMLResponse'],
            request_id=request_id
        )
        raise NotImplementedError()
