#!/usr/bin/env python
from setuptools import setup, find_packages
from os import getenv

VERSION = getenv("PKGVERSION")


requires = [
    'boto3',
    'requests'
]


setup(
    name='scalesec-gcp-workload-identity',
    version=VERSION,
    description='This package enables AWS->GCP federation with two lines of code',
    author='ScaleSec',
    author_email = 'info@scalesec.com',
    url='https://github.com/ScaleSec/gcp-workload-identity-federation',
    scripts=[],
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    license="Apache License 2.0",
    python_requires=">= 3.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
