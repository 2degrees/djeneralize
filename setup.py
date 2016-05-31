##############################################################################
#
# Copyright (c) 2011-2016, 2degrees Limited <2degrees-floss@googlegroups.com>.
# All Rights Reserved.
#
# This file is part of djeneralize <https://github.com/2degrees/djeneralize>,
# which is subject to the provisions of the BSD at
# <http://dev.2degreesnetwork.com/p/2degrees-license.html>. A copy of the
# license should accompany this distribution. THIS SOFTWARE IS PROVIDED "AS IS"
# AND ANY AND ALL EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST
# INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from setuptools import find_packages
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README")).read()
version = open(os.path.join(here, "VERSION")).readline().rstrip()

setup(
    name="djeneralize",
    version=version,
    description="Generalizations of specialized models for Django",
    long_description=README,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    keywords="django generalization specialization model",
    author="2degrees Limited",
    author_email="2degrees-floss@googlegroups.com",
    url="https://github.com/2degrees/djeneralize",
    license="BSD (http://dev.2degreesnetwork.com/p/2degrees-license.html)",
    packages=find_packages(),
    py_modules=[],
    zip_safe=False,
    install_requires=[
        "Django >= 1.6, <1.9dev",
    ],
    extras_require={
        'nose': ["nose >= 0.11"],
    },
    test_suite="nose.collector",
)
