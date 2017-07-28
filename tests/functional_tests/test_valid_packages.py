import os

import pytest

from conda_verify.errors import PackageError
from conda_verify.verify import Verify


@pytest.fixture
def package_dir():
    return os.path.join(os.path.dirname(__file__), 'test_packages')


@pytest.fixture
def verifier():
    package_verifier = Verify()
    return package_verifier


def test_valid_package(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.30-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_setuptools_package(package_dir, verifier):
    package = os.path.join(package_dir, 'distribute-0.0.1-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_empty_directory(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.33-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_python_package(package_dir, verifier):
    package = os.path.join(package_dir, 'python-0.0.1-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_pyd_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.34-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_script_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.35-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_noarch_link(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.36-noarch.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)


def test_valid_preferred_env(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.37-py36_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except PackageError as error:
        pytest.fail(error)
