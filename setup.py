from setuptools import setup
import codecs
import os


"""
:authors: Yurii Abramenko
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2022 SolveMeSolutions
"""

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
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
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/canyoupleasecreateanaccount/pycamel',
    license='Apache License, Version 2.0, see LICENSE file',
    packages=['pycamel'],
    install_requires=['pydantic', 'requests'],
    keywords=['python', 'automation', 'testing', 'tests', 'backend automation',
              'pytests', 'pydantic'],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
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
