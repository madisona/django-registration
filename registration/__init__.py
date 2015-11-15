
VERSION = (0, 3, 4)


def get_version():
    return ".".join(str(v) for v in VERSION)


def get_site(request):
    from django.contrib.sites import models as site_models
    return site_models.RequestSite(request)
