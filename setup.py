#!/usr/bin/env python

from distutils.core import setup

setup(
    name='nbgrader',
    version="0.0.1",
    description='Autograder for IPython notebooks',
    author='Jessica B. Hamrick',
    author_email='jhamrick@berkeley.edu',
    url='https://github.com/jhamrick/nbgrader',
    packages=['nbgrader'],
    keywords='ipython notebook grading homework',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Database :: Front-Ends",
        "Topic :: Utilities",
    ]
)
