
import os
from setuptools import setup

TEST_REQUIREMENTS = [
    'django>=1.8',
]

README = os.path.join(os.path.dirname(__file__), 'README')
setup(
    name="django-registration-gv",
    version="0.3.0",
    author="Aaron Madison",
    description="Django registration app",
    url="https://github.com/madisona/django-registration",
    test_suite='runtests.runtests',
    packages=('registration',),
    include_package_data=True,
    tests_require=TEST_REQUIREMENTS,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    zip_safe=False,
)
