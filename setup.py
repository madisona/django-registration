
from setuptools import setup

setup(
    name="django-registration",
    version="0.1",
    description="Django registration app using buildout",
    author="Aaron Madison",
    zip_safe = True,
    package_dir={'': 'src'},
    packages=('registration',),
    include_package_data=True,
    install_requires = (
        'django==1.3-alpha-1',
        'unittest2',        # for tests
        'mock',              # for tests
    ),
    dependency_links = ('http://www.djangoproject.com/download/1.3-alpha-1/tarball/#egg=django-1.3-alpha-1',),
)
