from core import context_processors


def test_feature_flags_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'core.context_processors.feature_flags' in processors


def test_feature_returns_expected_features(settings):
    settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED = True
    settings.FEATURE_NEW_SHARED_HEADER_ENABLED = False

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
        }
    }


def test_analytics_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'directory_components.context_processors.analytics' in processors
