#! /usr/bin/env python3

from distutils.core import setup

setup(
    name = "mfcdiff",
    version = "0.1",
    packages = ["mfcdiff"],
    scripts = ["bin/mfcdiff"],
    description = "Utility for diffing Mifare Classic card dumps",
    author = "Josef Gajdusek",
    author_email = "atx@atx.name",
    url = "https://github.com/atalax/mfcdiff",
    keywords = ["mifare", "nfc", "diff"],
    license = "MIT",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        ]
    )
