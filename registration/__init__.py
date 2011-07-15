
from django.contrib.sites import models as site_models

VERSION = (0, 1, 0)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    return version

def get_site(request):
    if site_models.Site._meta.installed:
        site = site_models.Site.objects.get_current()
    else:
        site = site_models.RequestSite(request)
    return site