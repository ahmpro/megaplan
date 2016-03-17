import re

from setuptools import setup

readme = open('README.rst', 'r').read()
description = readme.split('--')[1].strip()
long_description = readme + "HISTORY\n=======\n\n" + open('HISTORY.rst', 'r').read()
requires = open('requirements.txt', 'r').read().split("\n")


setup(
    name='megaplan',
    version='1.0a0',
    packages=['megaplan', 'megaplan.methods'],
    url='https://github.com/derfenix/megaplan/',
    license='LGPLv3',
    author='Sergey Kostyuchenko',
    author_email='derfenix@gmail.com',
    description=description,
    long_description=long_description,
    install_requires=requires,
    requires=[re.sub('(\w+).*', '\\1', r) for r in requires]
)
