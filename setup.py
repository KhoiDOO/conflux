# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="conflux",
    version="0.0.6",
    description="A simple crawler to download papers from major computer vision conferences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    author="KhoiDOO",
    author_email="khoido8899@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["conflux"],
    include_package_data=True,
    install_requires=[
        "beautifulsoup4==4.14.2",
        "requests==2.32.5",
        "alive-progress==3.1.5"
        ]
)