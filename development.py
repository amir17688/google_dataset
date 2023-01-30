"""
Add any additional URLs that should only be available when using the the
settings.development configuration.

See ``urls.defaults`` for a list of all URLs available across both
configurations.
"""
from .defaults import *

urlpatterns += patterns('',

    # Examples:
    # url(r'^$', '{{ project_name }}.views.debug', name='debug'),
    # url(r'^{{ project_name }}/', include('{{ project_name }}.debug.urls')),
)
ile if using sqlite3.
        'USER': '',                       # Not used with sqlite3.
        'PASSWORD': '',                   # Not used with sqlite3.
        'HOST': '',                       # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                       # Set to empty string for default. Not used with sqlite3.
    }
}

# URL configuration to use in development mode
ROOT_URLCONF = 'urls.development'


# Attempt to load any settings from settings.local_development, but ignore any
# errors complaining about them not being present.
try:
    from settings.local_development import *
except ImportError, e:
    pass
