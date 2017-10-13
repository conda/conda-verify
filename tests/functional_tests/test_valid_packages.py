import os

import pytest

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
    except SystemExit as error:
        pytest.fail(error)


def test_valid_empty_directory(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.33-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except SystemExit as error:
        pytest.fail(error)


def test_valid_python_package(package_dir, verifier):
    package = os.path.join(package_dir, 'python-0.0.1-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except SystemExit as error:
        pytest.fail(error)


def test_valid_pyd_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.34-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except SystemExit as error:
        pytest.fail(error)


def test_valid_script_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.35-py27_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except SystemExit as error:
        pytest.fail(error)


def test_valid_noarch_link(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.36-noarch.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except SystemExit as error:
        pytest.fail(error)


def test_valid_preferred_env(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.37-py36_0.tar.bz2')

    try:
        verifier.verify_package(path_to_package=package)
    except SystemExit as error:
        pytest.fail(error)


def test_passing_legacy_arguments_to_package_shows_warning(package_dir, verifier, caplog):
    package = os.path.join(package_dir, 'testfile-0.0.37-py36_0.tar.bz2')

    verifier.verify_package(path_to_package=package, run_scripts=None, ignore_scripts=None)
    assert caplog.text.count('Ignoring legacy ignore_scripts or run_scripts.') == 0
    verifier.verify_package(path_to_package=package, run_scripts='abc.py')
    assert caplog.text.count('Ignoring legacy ignore_scripts or run_scripts.') == 1
    verifier.verify_package(path_to_package=package, ignore_scripts='abc.py')
    # actually only one more, but we still have the earlier one in the pipe, too.
    assert caplog.text.count('Ignoring legacy ignore_scripts or run_scripts.') == 2
