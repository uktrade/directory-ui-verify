from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap

import core.views
import healthcheck.views
import identity.views
import eligibility.views


sitemaps = {
    'static': core.views.StaticViewSitemap,
}


urlpatterns = [
    url(
        r"^robots\.txt$",
        core.views.RobotsView.as_view(),
        name='robots'
    ),
    url(
        r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps},
        name='sitemap'
    ),
    url(
        r"^$",
        core.views.LandingPageView.as_view(),
        name='landing-page',
    ),
    url(
        r"^compliance-tool/$",
        core.views.ComplianceTool.as_view(),
        name='compliance-tool',
    ),
    url(
        r'^healthcheck/single-sign-on/$',
        healthcheck.views.SingleSignOnAPIView.as_view(),
        name='healthcheck-single-sign-on'
    ),
    url(
        r'^identity-verify/$',
        identity.views.IdentityVerificationAPIView.as_view(),
        name='local-matching-service'
    ),

    url(
        r'^eligibility-check/$',
        eligibility.views.CheckIsCompanyDirectorView.as_view()
    ),


]
