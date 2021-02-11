#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import io
from setuptools import setup, find_packages


def readme():
    with io.open('README.md', encoding='utf-8') as f:
        return f.read()


def requirements(filename):
    reqs = list()
    with io.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            reqs.append(line.strip())
    return reqs


setup(
    name='deepint',
    version='0.1',
    packages=find_packages(),
    url='https://deepint.net/',
    download_url='AAAAAAAAAAAAAAAA',
    license='AAAAAAAAAAAAAA',
    author='AAAAAAAAAAAA',
    author_email='AAAAAAAAAA',
    description='AAAAAAAAAAAA',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=requirements(filename='requirements.txt'),
    include_package_data=True,
    classifiers=[
        "AAAAAAAAAAAAAA"
    ],
    python_requires='>=3',
    extras_require={
        "tests": requirements(filename='tests/requirements.txt'),
        "docs": requirements(filename='docs/requirements.txt')
    },
    keywords=', '.join([
        'AAAAAAAAAAAAA'
    ]),
    project_urls={
        'Bug Reports': 'AAAAAAAAAA',
        'Source': 'AAAAAAAAAAA',
        'Documentation': 'AAAAAAAAAAAAAAAAAAAA'
    },
)
