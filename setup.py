# (c) 2017 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
import sys

from setuptools import setup

import versioneer

requirements = ['click >= 6.7', 'future >= 0.12.0', 'jinja2 >= 2.9', 'pyyaml >= 3.12', 'six']
if sys.version_info.major == 2:
    requirements.append('backports.functools_lru_cache >= 1.4')


setup(
    name="conda-verify",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Anaconda, Inc.",
    author_email="conda@anaconda.com",
    url="https://github.com/conda/conda-verify",
    license="BSD",
    description="A tool for validating conda recipes and conda packages",
    long_description=open('README.md').read(),
    packages=['conda_verify'],
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        conda-verify=conda_verify.cli:cli
        ''',
)
