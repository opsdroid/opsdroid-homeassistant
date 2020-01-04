#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import os

import versioneer

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.md"), "r", encoding="utf8") as fh:
    README = fh.read()
with open(os.path.join(HERE, "requirements.txt"), "r") as fh:
    REQUIRES = [line.strip() for line in fh]

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Jacob Tomlinson",
    author_email="jacob@tomlinson.email",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Home Assistant support for opsdroid",
    install_requires=REQUIRES,
    license="Apache Software License 2.0",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="Opsdroid Home Assistant",
    name="opsdroid-homeassistant",
    packages=["opsdroid_homeassistant"],
    entry_points={
        "opsdroid_connectors": ["homeassistant = opsdroid_homeassistant.connector"]
    },
    url="https://github.com/opsdroid/opsdroid-homeassistant",
    zip_safe=False,
)
