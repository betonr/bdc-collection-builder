#!/usr/bin/env python

import os
from setuptools import find_packages, setup


tests_require = []


extras_require = {
    "docs": [
        'bdc-readthedocs-theme @ git+git://github.com/brazil-data-cube/bdc-readthedocs-theme.git#egg=bdc-readthedocs-theme',
        'Sphinx>=2.1.2',
    ],
    "tests": tests_require
}

g = {}
with open(os.path.join('bdc_scripts', 'manifest.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['version']

setup(
    name='bdc-scripts',
    version=version,
    description='Brazilian Data Cube Scripts for Cube Generation',
    author='Admin',
    author_email='admin@admin.com',
    url='https://github.com/brazil-data-cube/bdc-scripts.git',
    packages=find_packages(),
    install_requires=[
        'alembic>=1.0.10',
        'GeoAlchemy2>=0.6.3',
        'Flask>=1.1.1',
        'Flask-Cors>=3.0.8',
        'flask-restplus>=0.13.0',
        'flask_bcrypt>=0.7.1',
        'bdc-core @ git+git://github.com/brazil-data-cube/bdc-core.git#egg=bdc-core',
        # TODO: Temporary workaround since kombu setting fixed version
        'celery[librabbitmq]==4.3.0',
        'librabbitmq==2.0.0',
        'vine==1.3.0',
        'amqp==2.5.1',
    ],
    extras_require=extras_require,
    tests_require=tests_require,
    include_package_data=True,
)