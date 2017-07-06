from conda_verify.conda_package_check import CondaPackageCheck


def verify_package_files(path_to_package=None, verbose=True, **kwargs):
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.check_members()
    package_check.info_files()
    package_check.no_hardlinks()
    package_check.not_allowed_files(pedantic=pedantic)
    package_check.index_json()
    package_check.no_bat_and_exe()
    package_check.list_packages()
    package_check.has_prefix(pedantic=pedantic)
    package_check.menu_names(pedantic=pedantic)

    package_check.t.close()


def verify_2to3(path_to_package=None, verbose=True, **kwargs):
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.no_2to3_pickle()
    package_check.t.close()


def verify_post_link(path_to_package=None, verbose=True, **kwargs):
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.warn_post_link()
    package_check.t.close()


def verify_pyc(path_to_package=None, verbose=True, **kwargs):
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.warn_pyo()
    package_check.pyc_files()
    package_check.no_py_next_so()
    package_check.no_pyc_in_stdlib()
    package_check.t.close()


def verify_setup_files(path_to_package=None, verbose=True, **kwargs):
    pedantic = kwargs.get("pedantic") if "pedantic" in kwargs.keys() else True
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.no_setuptools()
    package_check.no_easy_install_script(pedantic)
    package_check.no_pth(pedantic)
    package_check.t.close()


def verify_arch(path_to_package=None, verbose=True, **kwargs):
    package_check = CondaPackageCheck(path_to_package, verbose)
    package_check.check_windows_arch()
    package_check.t.close()