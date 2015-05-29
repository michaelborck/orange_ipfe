#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(

    name='orange_ipfe',
    version='0.1.0',
    description="An addon to the Orange data mining canvas to process images.",
    long_description=readme + '\n\n' + history,
    author="Michael Borck",
    author_email='michael@borck.me',
    url='https://github.com/michaelborck/orange_ipfe',
    packages=[
        'orange_ipfe',
    ],
    package_dir={'orange_ipfe':
                 'orange_ipfe'},
    package_data={'orange_ipfe':['icons/*']},
    # Declare orangedemo package to contain widgets for the "Demo" category
    entry_points={"orange.widgets": ("orange_ipfe = orange_ipfe")},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='orange_ipfe',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
