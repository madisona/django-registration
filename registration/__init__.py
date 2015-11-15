
VERSION = (0, 3, 1)


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    return version


def get_site(request):
    from django.contrib.sites import models as site_models
    return site_models.RequestSite(request)
