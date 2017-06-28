from conda_verify.conda_package_check import CondaPackageCheck


def verify_2to3(path_to_package=None, verbose=True, **kwargs):
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.no_2to3_pickle()
    package_check.t.close()
