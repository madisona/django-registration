
from setuptools import setup

setup(
    name="django-registration",
    version="0.0.2",
    description="Django registration app",
    author="Aaron Madison",
    #zip_safe = True,
    package_dir={'': 'registration'},
    #packages=('registration',),
    include_package_data=True,
)
