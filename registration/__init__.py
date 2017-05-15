VERSION = (0, 5, 0)


def get_version():
    return ".".join(str(v) for v in VERSION)


def get_site(request):
    from django.contrib.sites.requests import RequestSite
    return RequestSite(request)
