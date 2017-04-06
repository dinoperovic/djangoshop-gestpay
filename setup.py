#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import shop_gestpay

from setuptools import find_packages, setup

try:
    from pypandoc import convert
except ImportError:
    import io

    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()


CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]

setup(
    author='Dino Perovic',
    author_email='dino.perovic@gmail.com',
    name='djangoshop-gestpay',
    version=shop_gestpay.__version__,
    description='GestPay Payment integration for djangoSHOP.',
    long_description=convert('README.md', 'rst'),
    url='https://github.com/dinoperovic/djangoshop-gestpay',
    license='BSD',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-shop>=0.9.3',
        'gestpypay>=1.0.0',
    ],
    setup_requires=['setuptools-markdown'],
)
