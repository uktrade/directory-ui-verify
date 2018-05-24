from django.core.urlresolvers import reverse

from core import views


def test_landing_page(client, settings):
    url = reverse('landing-page')

    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [views.LandingPageView.template_name]


def test_robots(client):
    url = reverse('robots')

    response = client.get(url)

    assert response.status_code == 200
