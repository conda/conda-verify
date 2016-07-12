from __future__ import print_function, division, absolute_import

import re
import json
import shlex
import tarfile
from os.path import basename

from anaconda_verify.utils import get_object_type


class PackageError(Exception):
    pass


def dist_fn(fn):
    if fn.endswith('.tar.bz2'):
        return fn[:-8]
    if fn.endswith('.tar'):
        return fn[:-4]
    raise PackageError("did not expect filename: %s" % fn)


class CondaPackageCheck(object):
    def __init__(self, path, verbose=False):
        self.verbose = verbose
        self.t = tarfile.open(path)
        self.dist = dist_fn(basename(path))
        self.name, self.version, self.build = self.dist.rsplit('-', 2)
        paths = [m.path for m in self.t.getmembers()]
        self.paths = set(paths)
        if len(paths) != len(self.paths):
            raise PackageError("duplicate members")
        raw = self.t.extractfile('info/index.json').read()
        self.info = json.loads(raw.decode('utf-8'))

    def info_files(self):
        lista = [p.decode('utf-8').strip() for p in
                 self.t.extractfile('info/files').readlines()]
        for p in lista:
            if p.startswith('info/'):
                raise PackageError("Did not expect '%s' in info/files" % p)

        seta = set(lista)
        if len(lista) != len(seta):
            raise PackageError('info/files: duplicates')

        listb = [m.path for m in self.t.getmembers()
                 if not (m.path.startswith('info/') or m.isdir())]
        setb = set(listb)
        if len(listb) != len(setb):
            raise PackageError("info_files: duplicate members")

        if seta == setb:
            return
        for p in sorted(seta | setb):
            if p not in seta:
                print('%r not in info/files' % p)
            if p not in setb:
                print('%r not in tarball' % p)
        raise PackageError("info/files")

    def not_allowed_files(self):
        not_allowed = {'conda-meta', 'conda-bld',
                       'pkgs', 'pkgs32', 'envs'}
        not_allowed_dirs = tuple(x + '/' for x in not_allowed)
        for p in self.paths:
            if (p.startswith(not_allowed_dirs) or
                    p in not_allowed or
                    p.endswith('/.DS_Store')):
                raise PackageError("directory or filename not allowed: "
                                   "%s" % p)

    def index_json(self):
        for varname in 'name', 'version', 'build':
            if self.info[varname] != getattr(self, varname):
                raise PackageError("info/index.json for %s: %r != %r" %
                                   (varname, self.info[varname],
                                    getattr(self, varname)))
        bn = self.info['build_number']
        if not isinstance(bn, int):
            raise PackageError("info/index.json: invalid build_number: %s" %
                               bn)

    def no_bat_and_exe(self):
        bats = {p[:-4] for p in self.paths if p.endswith('.bat')}
        exes = {p[:-4] for p in self.paths if p.endswith('.exe')}
        both = bats & exes
        if both:
            raise PackageError("Both .bat and .exe files: %s" % both)


    def _check_has_prefix_line(self, line):
        line = line.strip()
        try:
            placeholder, mode, f = [x.strip('"\'') for x in
                                    shlex.split(line, posix=False)]
        except ValueError:
            placeholder, mode, f = '/<dummy>/<placeholder>', 'text', line

        if f not in self.paths:
            raise PackageError("info/has_prefix: target '%s' not in "
                               "package" % f)

        if mode == 'binary':
            if self.info['platform'] == 'win':
                raise PackageError("info/has_prefix: binary replace mode "
                                   "not allowed on Windows")
            if len(placeholder) != 255:
                raise PackageError("info/has_prefix: binary placeholder not "
                                   "255 bytes, but: %d" % len(placeholder))
        elif mode == 'text':
            pass
        else:
            raise PackageError("info/has_prefix: invalid mode")


    def has_prefix(self):
        for m in self.t.getmembers():
            if m.path != 'info/has_prefix':
                continue
            if self.info['platform'] == 'win':
                print("WARNING: %s" % m.path)
            data = self.t.extractfile(m.path).read()
            for line in data.splitlines():
                self._check_has_prefix_line(line)


    def warn_post_link(self):
        for p in self.paths:
            if p.endswith((
                    '-post-link.sh',  '-pre-link.sh',  '-pre-unlink.sh',
                    '-post-link.bat', '-pre-link.bat', '-pre-unlink.bat',
                    )):
                print("WARNING: %s" % p)

    def no_setuptools(self):
        for p in self.paths:
            if p.endswith('easy-install.pth'):
                raise PackageError("easy-install.pth file not allowed")

        if self.name in ('setuptools', 'distribute'):
            return
        for p in self.paths:
            if p.endswith('MyPyPa-0.1.0-py2.5.egg'):
                continue
            if (p.endswith('.egg') or
                    'site-packages/pkg_resources' in p or
                    'site-packages/__pycache__/pkg_resources' in p or
                    p.startswith('bin/easy_install') or
                    p.startswith('Scripts/easy_install')):
                raise PackageError("file '%s' not allowed" % p)

    def no_easy_install_script(self):
        for m in self.t.getmembers():
            if not m.name.startswith(('bin/', 'Scripts/')):
                continue
            data = self.t.extractfile(m.path).read(1024)
            if b'EASY-INSTALL-SCRIPT' in data:
                raise PackageError("easy install script found: %s" % m.name)

    def no_pth(self):
        for p in self.paths:
            if p.endswith('-nspkg.pth'):
                raise PackageError("found namespace .pth file '%s'" % p)
            if p.endswith('.pth'):
                print("WARNING: .pth file: %s" % p)

    def warn_pyo(self):
        if self.name == 'python':
            return
        for p in self.paths:
            if p.endswith('.pyo'):
                print("WARNING: .pyo file: %s" % p)

    def no_py_next_so(self):
        for p in self.paths:
            if p.endswith('.so'):
                root = p[:-3]
            elif p.endswith('.pyd'):
                root = p[:-4]
            else:
                continue
            for ext in '.py', '.pyc':
                if root + ext in self.paths:
                    print("WARNING: %s next to: %s" % (ext, p))

    def no_pyc_in_stdlib(self):
        if self.name in {'python', 'scons'}:
            return
        for p in self.paths:
            if p.endswith('.pyc') and not 'site-packages' in p:
                raise PackageError(".pyc found in stdlib: %s" % p)

    def no_2to3_pickle(self):
        if self.name == 'python':
            return
        for p in self.paths:
            if ('lib2to3' in p and p.endswith('.pickle')):
                raise PackageError("found lib2to3 .pickle: %s" % p)

    def pyc_files(self):
        if 'py3' in self.build:
            return
        for p in self.paths:
            if ('/site-packages/' not in p) or ('/port_v3/' in p):
                continue
            if p.endswith('.py') and (p + 'c') not in self.paths:
                print("WARNING: pyc missing for:", p)
                if not self.verbose:
                    return

    def check_windows_arch(self):
        if self.name in ('python', 'conda-build', 'pip', 'xlwings',
                         'phantomjs', 'qt'):
            return
        if self.info['platform'] != 'win':
            return
        arch = self.info['arch']
        if arch not in ('x86', 'x86_64'):
            raise PackageError("Unrecognized Windows architecture: %s" %
                               arch)
        for m in self.t.getmembers():
            if not m.name.lower().endswith(('.exe', '.dll')):
                continue
            data = self.t.extractfile(m.path).read(4096)
            tp = get_object_type(data)
            if ((arch == 'x86' and tp != 'DLL I386') or
                (arch == 'x86_64' and tp != 'DLL AMD64')):
                raise PackageError("File %s has object type %s, but info/"
                                   "index.json arch is %s" %
                                   (m.name, tp, arch))

    def list_packages(self):
        pat = re.compile(r'site-packages/([^/]+)')
        res = set()
        for p in self.paths:
            m = pat.search(p)
            if m is None:
                continue
            fn = m.group(1)
            if '-' in fn or fn.endswith('.pyc'):
                continue
            res.add(fn)
        if self.verbose:
            for x in res:
                print('    %s' % x)
        for pkg_name in 'numpy', 'scipy':
            if self.name != pkg_name and pkg_name in res:
                raise PackageError("found %s" % pkg_name)
        if self.name not in ('setuptools', 'distribute', 'python'):
            for x in ('pkg_resources.py', 'setuptools.pth', 'easy_install.py',
                      'setuptools'):
                if x in res:
                    raise PackageError("found %s" % x)


def validate_package(path, verbose=True):
    x = CondaPackageCheck(path, verbose)
    x.info_files()
    x.not_allowed_files()
    x.index_json()
    x.no_bat_and_exe()
    x.has_prefix()
    x.warn_post_link()
    x.no_setuptools()
    x.no_easy_install_script()
    x.no_pth()
    x.warn_pyo()
    x.no_py_next_so()
    x.no_pyc_in_stdlib()
    x.no_2to3_pickle()
    x.pyc_files()
    x.check_windows_arch()
    x.list_packages()
    x.t.close()
