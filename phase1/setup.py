#!/usr/bin/env python3

from setuptools import setup


setup(
    name='telemetrix',
    packages=['telemetrix'],
    install_requires=['pyserial'],

    version='0.01',
    description="telemetrix phase1 client and server",

    author='Alan Yorinks',
    author_email='MisterYsLab@gmail.com',
    url='https://github.com/MrYsLab/telemetrix',
    download_url='https://github.com/MrYsLab/telemetrix',
    keywords=['telemetrix', 'Arduino', 'Protocol', 'Python'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

