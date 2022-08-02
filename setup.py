import codecs
import os
from setuptools import setup, find_packages


"""
:authors: Yurii Abramenko
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2022 SolveMeSolutions
"""

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.rst"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.2'
DESCRIPTION = 'Backend automation framework. Automation is easy.'
LONG_DESCRIPTION = 'A package helps Automation QA creates automation' \
                   'project and setup tests without additional infrastructure '\
                   'and time wasting.' \
                   'All base structure has been written and prepared for you.'

# Setting up
setup(
    name="pycamel",
    version=VERSION,
    author="Yurii Abramenko",
    author_email="<yura.abramenko1@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    url='https://github.com/canyoupleasecreateanaccount/pycamel',
    license='Apache License, Version 2.0, see LICENSE file',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pydantic', 'requests'],
    keywords=['python', 'automation', 'testing', 'tests', 'backend automation',
              'pytests', 'pydantic'],
    project_urls={
        'Source': 'https://github.com/canyoupleasecreateanaccount/pycamel/',
        'Tracker': 'https://github.com/canyoupleasecreateanaccount/pycamel/issues',
        'Changelog': 'https://github.com/canyoupleasecreateanaccount/pycamel/releases',
    },
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
    ]
)
