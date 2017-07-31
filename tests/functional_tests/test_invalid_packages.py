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


def test_invalid_package_sequence(package_dir, verifier):
    package = os.path.join(package_dir, 'test_-file.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ('PackageError: '
            'Found invalid sequence "_-" '
            'in package in info/index.json' in str(excinfo))


def test_invalid_package_extension(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile.zip')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            'Found package with invalid extension ".zip"' in str(excinfo))


def test_duplicate_members(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.1-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "duplicate members" in str(excinfo))


def test_index_unicode(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.2-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "non-ASCII in: info/index.json" in str(excinfo))


def test_info_in_files_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.3-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "Did not expect 'info/index.json' in info/files" in str(excinfo))


def test_duplicates_in_files_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.4-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "info/files: duplicates" in str(excinfo))


def test_not_in_files_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.5-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert ("PackageError: "
            "info/files" in str(excinfo))

    assert "'lib/testfile.txt' not in info/files" in str(output)


def test_not_in_tarball(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.6-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert ("PackageError: "
            "info/files" in str(excinfo))

    assert "'testfile.txt' not in tarball" in str(output)


def test_not_allowed_files(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.7-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "directory or filename not allowed: "
            "info/testfile~" in str(excinfo))


def test_file_not_allowed(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.8-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "file not allowed: info/link.json" in str(excinfo))


def test_invalid_package_name(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.9-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "info/index.json for name: " in str(excinfo))


def test_invalid_build_number(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.10-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "info/index.json: invalid build_number: 1" in str(excinfo))


def test_duplicates_in_bin(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.11-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "Both .bat and .exe files:" in str(excinfo))


def test_win_package_warning(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.12-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert ("PackageError: "
            "info/has_prefix: target 'bin/testfile' "
            "not in package" in str(excinfo))

    assert 'WARNING: info/has_prefix' in str(output)


def test_win_package_binary_warning(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.13-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "binary placeholder not allowed on Windows" in str(excinfo))


def test_package_placeholder_warning(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.14-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("info/has_prefix: binary placeholder not 255 bytes, "
            "but: 329" in str(excinfo))


def test_invalid_prefix_mode(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.15-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "info/has_prefix: invalid mode" in str(excinfo))


def test_unicode_prefix(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.16-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "non-ASCII in: info/has_prefix" in str(excinfo))


def test_invalid_script_name(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.17-py36_0.tar.bz2')

    verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert "WARNING: bin/test-pre-unlink.bat" in str(output)


def test_invalid_setuptools(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.18-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "file 'bin/easy_install.pth' not allowed" in str(excinfo))


def test_invalid_eggfile(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.19-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "file 'bin/test.egg' not allowed" in str(excinfo))


def test_invalid_script_header(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.20-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "easy install script found: bin/test-script.py" in str(excinfo))


def test_invalid_namespace_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.21-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "found namespace .pth file 'bin/test-nspkg.pth'" in str(excinfo))


def test_invalid_pyo_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.22-py36_0.tar.bz2')

    verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert "WARNING: .pyo file: bin/test.pyo" in str(output)


def test_invalid_pyc_and_so_files(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.23-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            ".pyc found in stdlib: bin/test.pyc" in str(excinfo))

    output, error = capfd.readouterr()

    assert "WARNING: .pyc next to: bin/test.so" in str(output)


def test_invalid_pickle_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.24-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "found lib2to3 .pickle: lib/lib2to3/test.pickle" in str(excinfo))


def test_missing_pyc_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.25-py27_0.tar.bz2')

    verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert ("WARNING: pyc missing for:" in str(output))


def test_invalid_windows_architecture(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.26-py27_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "Unrecognized Windows architecture: x84" in str(excinfo))


def test_invalid_windows_dll(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.27-py27_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "File bin/testfile.dll has object type None, "
            "but info/index.json arch is x86_64" in str(excinfo))


def test_invalid_package_in_name(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.28-py27_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    output, error = capfd.readouterr()

    assert ("PackageError: "
            "found numpy" in str(excinfo))

    assert 'numpy' in str(output)


def test_invalid_package_in_bin(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.29-py27_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "found setuptools" in str(excinfo))


def test_invalid_easy_install_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.31-py27_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "easy-install.pth file not allowed" in str(excinfo))


def test_empty_tar(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.38-py36_0.tar')

    with pytest.raises(KeyError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert "not found" in str(excinfo)


def test_non_ascii_path(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.39-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert "PackageError: non-ASCII path" in str(excinfo)


def test_ascii_in_files_file(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.40-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert "PackageError: non-ASCII in: info/files" in str(excinfo)


def test_missing_depends_key(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.41-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: "
            "info/index.json: key 'depends' missing" in str(excinfo))


def test_invalid_license_family(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile-0.0.42-py36_0.tar.bz2')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package)

    assert ("PackageError: wrong license family: FAKELICENSE" in str(excinfo))
