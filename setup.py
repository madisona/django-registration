
import os
from setuptools import setup, find_packages

from registration import get_version

TEST_REQUIREMENTS = [
    'django>=1.8',
]

README = os.path.join(os.path.dirname(__file__), 'README')
setup(
    name="django-registration-gv",
    version=get_version(),
    author="Aaron Madison",
    description="Django registration app",
    url="https://github.com/madisona/django-registration",
    test_suite='runtests.runtests',
    packages=find_packages(exclude=["example"]),
    include_package_data=True,
    tests_require=TEST_REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    zip_safe=False,
)
