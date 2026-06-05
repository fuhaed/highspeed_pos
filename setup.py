# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in highspeed_pos/__init__.py
from highspeed_pos import __version__ as version

setup(
    name="highspeed_pos",
    version=version,
    description="HIGHSPEED POS",
    author="Yousef Restom",
    author_email="info@highspeed.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
