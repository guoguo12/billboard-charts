#!/usr/bin/env python

from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="billboard.py",
    version="7.0.2",  # Don't forget to update CHANGELOG.md!
    description="Python API for downloading Billboard charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Allen Guo",
    author_email="guoguo12@gmail.com",
    url="https://github.com/guoguo12/billboard-charts",
    py_modules=["billboard"],
    license="MIT License",
    install_requires=["beautifulsoup4 >= 4.4.1", "requests >= 2.2.1"],
)
