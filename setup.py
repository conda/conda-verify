# (c) 2016 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
import re
from os.path import join

from distutils.core import setup


# read version from anaconda_verify/__init__.py
pat = re.compile(r'__version__\s*=\s*(\S+)', re.M)
data = open(join('anaconda_verify', '__init__.py')).read()
version = eval(pat.search(data).group(1))

setup(
    name = "anaconda-verify",
    version = version,
    author = "Ilan Schnell",
    author_email = "ilan@continuum.io",
    url = "https://github.com/ContinuumIO/anaconda-verify",
    license = "BSD",
    description = "tool for validating conda recipes and conda packages",
    long_description = open('README.md').read(),
    packages = ['anaconda_verify'],
)
