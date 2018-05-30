from django.template.response import TemplateResponse
from django.views.generic.edit import FormView

from core.helpers import api_client, get_session_request_id
from eligibility import forms, helpers
from sso.utils import SSOLoginRequiredMixin


class CheckIsCompanyOfficerView(SSOLoginRequiredMixin, FormView):
    http_method_names = ['post']
    form_class = forms.CheckIsCompanyOfficerForm
    success_template_name = 'eligibility/gov-verify-success.html'
    failure_template_name = 'eligibility/gov-verify-failure.html'

    def get_template_name(self, is_success):
        if is_success:
            return self.success_template_name
        return self.failure_template_name

    def form_invalid(self, form):
        company_details = self.get_company_details()
        return TemplateResponse(
            request=self.request,
            template=self.get_template_name(is_success=False),
            context=self.get_context_data(company_details=company_details),
        )

    def form_valid(self, form):
        company_details = self.get_company_details()
        is_success = helpers.is_probably_company_officer(
            first_name=form.cleaned_data['first_name'],
            surname=form.cleaned_data['surname'],
            birth_date=form.cleaned_data['birth_date'],
            company_number=company_details['number'],
        )
        return TemplateResponse(
            request=self.request,
            template=self.get_template_name(is_success=is_success),
            context=self.get_context_data(company_details=company_details),
        )

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs['request_id'] = get_session_request_id(self.request)
        return form_kwargs

    def get_company_details(self):
        response = api_client.company.retrieve_private_profile(
            sso_session_id=self.request.sso_user.session_id,
        )
        response.raise_for_status()
        return response.json()
