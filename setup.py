#!/bin/env python
from setuptools import setup
import subprocess
import os
import sys

# Setuptools bug workaround issue #10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

cmd = "git describe --tags --abbrev=0 HEAD"
result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
try:
    git_tag = result.stdout.readlines()[0].strip().decode('ASCII')
    version_num = git_tag.lstrip('v')
except:
    version_num = '1.0.0'

setup(
    name='tuber',
    packages=['tuber', 'tuber.models', 'tuber.api'],
    version=version_num,
    description="It's a potato.",
    long_description="""Track shifts, sell badges, and more.""",
    license="GPLv3",
    author='Mark Murnane',
    author_email='mark@hackafe.net',
    url='https://github.com/magfest/tuber',
    keywords=[
        'events',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[
        'requests',
        'Flask-SQLAlchemy',
        'Flask-Migrate',
        'passlib',
        'flask',
    ],
    entry_points={
        'console_scripts': [
            'tuber=tuber.__main__:main',
        ]
    },
)
