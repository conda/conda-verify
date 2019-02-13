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
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    assert ('PackageError: '
            'Found invalid sequence "_-" '
            'in package in info/index.json' in str(excinfo))


def test_invalid_package_extension(package_dir, verifier):
    package = os.path.join(package_dir, 'testfile.zip')

    with pytest.raises(PackageError) as excinfo:
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    assert ("PackageError: "
            'Found package with invalid extension ".zip"' in str(excinfo))


def test_index_unicode(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.2-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1116 Found non-ascii characters inside info/index.json' in error


def test_info_in_files_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.3-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1120 Found filenames in info/files that start with "info"' in error


def test_duplicates_in_files_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.4-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1121 Found duplicate filenames in info/files' in error


def test_not_in_files_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.5-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1123 Found filename in tar archive missing from info/files: lib{}testfile.txt'.format(os.path.sep) in error


def test_not_in_tarball(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.6-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1122 Found filename in info/files missing from tar archive: testfile.txt' in error


def test_not_allowed_files(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.7-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1125 Found unallowed file in tar archive: info{}testfile~'.format(os.path.sep) in error


def test_file_not_allowed(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.8-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1126 Found info{}link.json however package is not a noarch package'.format(os.path.sep) in error


def test_invalid_package_name(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.9-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1102 Found package name in info/index.json "test-file" does not match filename "testfile"' in error


def test_invalid_build_number(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.10-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1108 Build number in info/index.json must be an integer' in error


def test_duplicates_in_bin(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.11-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1127 Found both .bat and .exe files with same basename in same folder' in error


def test_win_package_warning(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.12-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1129 Found filename "bin/testfile" in info/has_prefix not included in archive' in error


def test_win_package_binary_warning(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.13-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1132 Binary placeholder found in info/has_prefix not allowed in Windows package' in error


def test_package_placeholder_warning(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.14-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1133 Binary placeholder' in error
    assert 'found in info/has_prefix does not have a length of 255 bytes' in error


def test_invalid_prefix_mode(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.15-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1130 Found invalid mode "wrong_mode" in info/has_prefix' in error


def test_unicode_prefix(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.16-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1128 Found non-ascii characters in info/has_prefix' in error


def test_invalid_script_name(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.17-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1134 Found pre/post link file "bin{}test-pre-unlink.bat" in archive'.format(os.path.sep) in error


def test_invalid_setuptools(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.18-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1136 Found easy_install script "bin{}easy_install" in archive'.format(os.path.sep) in error
    assert 'C1137 Found namespace file "bin{}easy_install.pth" in archive'.format(os.path.sep) in error


def test_invalid_eggfile(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.19-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1135 Found egg file "bin{}test.egg" in archive'.format(os.path.sep) in error


def test_invalid_namespace_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.21-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1137 Found namespace file "bin{}test-nspkg.pth" in archive'.format(os.path.sep) in error


def test_invalid_pyo_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.22-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1138 Found pyo file "bin{}test.pyo" in archive'.format(os.path.sep) in error


def test_invalid_pyc_and_so_files(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.23-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1138 Found pyo file "bin{}test.pyo" in archive'.format(os.path.sep) in error
    assert 'C1139 Found pyc file "bin{}test.pyc" in invalid directory'.format(os.path.sep) in error


def test_invalid_pickle_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.24-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1140 Found lib2to3 .pickle file "lib{0}lib2to3{0}test.pickle"'.format(os.path.sep) in error


def test_missing_pyc_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.25-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert  'C1141 Found python file "lib{0}site-packages{0}python2.7{0}test.py" without a corresponding pyc file'.format(os.path.sep) in error


def test_invalid_windows_architecture(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.26-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1144 Found unrecognized Windows architecture "x84"' in error


def test_invalid_windows_dll(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.27-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1145 Found file "bin{}testfile.dll" with object type "None" but with arch "x86_64"'.format(os.path.sep) in error


def test_invalid_easy_install_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.31-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1137 Found namespace file "bin{}easy-install.pth" in archive'.format(os.path.sep) in error


def test_non_ascii_path(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.39-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1118 Found archive member names containing non-ascii characters' in error


def test_ascii_in_files_file(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.40-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1119' in error


def test_missing_depends_key(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.41-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1112 Missing "depends" field in info/index.json' in error


def test_invalid_license_family(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.42-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'Found invalid license "FAKELICENSE" in info/index.json' in error


def test_invalid_file_hash(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.43-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1146 Found file "lib{0}python3.6{0}site-packages{0}test{0}__main__.py" with sha256 hash different than listed in paths.json'.format(os.path.sep) in error


def test_invalid_file_size(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.44-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1147 Found file "lib{0}python3.6{0}site-packages{0}test{0}__main__.py" with filesize different than listed in paths.json'.format(os.path.sep) in error


def test_duplicate_menu_json(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.45-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()
    assert 'C1143 Found more than one Menu json file' in error


def test_invalid_menu_json(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.46-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1142 Found invalid Menu json file "Menu{}wrongname.json"'.format(os.path.sep) in error


def test_python_binary_warning(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'python-0.0.1-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1131 Binary placeholder found in info/has_prefix not allowed when building Python' in error


def test_invalid_package_placeholder(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.47-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1129 Found filename "/opt/anaconda1anaconda2anaconda3 text testfile testfile" in info/has_prefix not included in archive' in error


def test_invalid_dependency_specs(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.48-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1114 Found invalid dependency "python 3.6@**&*&(&@!" in info/index.json' in error


def test_empty_dependencies(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.49-py27_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1113 Found empty dependencies in info/index.json' in error


def test_invalid_build_string(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.50-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1110 Found invalid build string "py36_0!" in info/index.json' in error


def test_invalid_build_number_negative(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.51-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1109 Build number in info/index.json cannot be a negative integer' in error


def test_invalid_version_suffix(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.52-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert "C1107 Package version in info/index.json cannot start or end with '_' or '.'" in error


def test_invalid_version(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.53-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert "C1105 Found invalid version number in info/index.json" in error


def test_missing_version(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.54-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert "C1104 Missing package version in info/index.json" in error


def test_invalid_package_name_pattern(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.55-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert "C1103 Found invalid package name in info/index.json" in error


def test_missing_package_name(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.56-py36_0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert "C1101 Missing package name in info/index.json" in error


def test_invalid_noarch_files(package_dir, verifier, capfd):
    package = os.path.join(package_dir, 'testfile-0.0.57-0.tar.bz2')

    with pytest.raises(PackageError):
        verifier.verify_package(path_to_package=package, exit_on_error=True)

    output, error = capfd.readouterr()

    assert 'C1148 Found architecture specific file "bin{}testfile.dll" in package.'.format(os.path.sep) in error
