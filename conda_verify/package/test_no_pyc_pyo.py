from conda_verify.conda_package_check import CondaPackageCheck


def verify(path_to_package=None, verbose=True, **kwargs):
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.warn_pyo()
    package_check.pyc_files()
    package_check.no_py_next_so()
    package_check.no_pyc_in_stdlib()
    package_check.t.close()
