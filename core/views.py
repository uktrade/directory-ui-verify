from django.conf import settings
from django.contrib import sitemaps
from django.http import Http404
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.urls import reverse

from core import constants, helpers
from sso.utils import SSOLoginRequiredMixin


class LandingPageView(TemplateView):
    template_name = 'core/landing-page.html'


class RobotsView(TemplateView):
    template_name = 'core/robots.txt'
    content_type = 'text/plain'


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = 'daily'

    def items(self):
        return [
            'landing-page'
        ]

    def location(self, item):
        return reverse(item)


class ComplianceTool(SSOLoginRequiredMixin, RedirectView):

    def dispatch(self, *args, **kwargs):
        if not settings.FEATURE_GOV_VERIFY_COMPLIANCE_TOOL_ENABLED:
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def get_redirect_url(self):
        request_id, url = helpers.generate_gov_verify_compliance_test_suite()
        self.request.session[constants.SAML_REQUEST_ID_KEY] = request_id
        return url
        return helpers.get_create_account_level_two_compliance_test(url)
