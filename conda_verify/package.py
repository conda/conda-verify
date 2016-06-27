from __future__ import print_function, division, absolute_import

import re
import sys
import json
import tarfile
from os.path import basename

from utils import get_object_type



def dist_fn(fn):
    if fn.endswith('.tar.bz2'):
        return fn[:-8]
    sys.exit("Error: did not expect filename: %s" % fn)


class TarCheck(object):
    def __init__(self, path, verbose=False):
        self.verbose = verbose
        self.t = tarfile.open(path)
        self.dist = dist_fn(basename(path))
        self.name, self.version, self.build = self.dist.rsplit('-', 2)
        paths = [m.path for m in self.t.getmembers()]
        self.paths = set(paths)
        if len(paths) != len(self.paths):
            sys.exit('Error: duplicate members')

    def info_files(self):
        lista = [p.decode('utf-8').strip() for p in
                 self.t.extractfile('info/files').readlines()]
        for p in lista:
            if p.startswith('info/'):
                sys.exit("Did not expect '%s' in info/files" % p)

        seta = set(lista)
        if len(lista) != len(seta):
            sys.exit('info/files: duplicates')

        listb = [m.path for m in self.t.getmembers()
                 if not (m.path.startswith('info/') or m.isdir())]
        setb = set(listb)
        if len(listb) != len(setb):
            sys.exit('info_files: duplicate members')

        if seta == setb:
            return
        for p in sorted(seta | setb):
            if p not in seta:
                print('%r not in info/files' % p)
            if p not in setb:
                print('%r not in tarball' % p)
        sys.exit('info/files')

    def not_allowed_files(self):
        not_allowed = {'conda-meta', 'conda-bld',
                       'pkgs', 'pkgs32', 'envs'}
        if self.name == '_cache':
            not_allowed.remove('pkgs')
        not_allowed_dirs = tuple(x + '/' for x in not_allowed)
        for p in self.paths:
            assert not p.startswith(not_allowed_dirs), p
            assert not p in not_allowed, p
            assert not p.endswith('/.DS_Store'), p

    def info_misc(self):
        pass

    def index_json(self):
        info = json.load(self.t.extractfile('info/index.json'))
        for varname in 'name', 'version', 'build':
            if info[varname] != getattr(self, varname):
                sys.exit('Error: %s: %r != %r' % (varname, info[varname],
                                                  getattr(self,varname)))
        assert isinstance(info['build_number'], int)

    def no_bat_and_exe(self):
        bats = {p[:-4] for p in self.paths if p.endswith('.bat')}
        exes = {p[:-4] for p in self.paths if p.endswith('.exe')}
        both = bats & exes
        if both:
            sys.exit('Error: Both .bat and .exe files: %s' % ', '.join(both))

    def no_setuptools(self):
        for p in self.paths:
            assert not p.endswith('easy-install.pth')

        if self.name not in ('setuptools', 'distribute'):
            for p in self.paths:
                if p.endswith('MyPyPa-0.1.0-py2.5.egg'):
                    continue
                assert not p.endswith('.egg'), p
                assert 'site-packages/pkg_resources' not in p, p
                assert 'site-packages/__pycache__/pkg_resources' not in p, p
                assert not p.startswith('bin/easy_install'), p
                assert not p.startswith('Scripts/easy_install'), p

    def no_pth(self):
        for p in self.paths:
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
                    print("WARNING: %-4s next to: %s" % (ext, p))

    def no_pyc_in_stdlib(self):
        if self.name in {'python', 'scons'}:
            return
        for p in self.paths:
            assert not p.endswith('.pyc') or 'site-packages' in p, p

    def no_2to3_pickle(self):
        if self.name == 'python':
            return
        for p in self.paths:
            assert not ('lib2to3' in p and p.endswith('.pickle')), p

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
        info = json.load(self.t.extractfile('info/index.json'))
        if info['platform'] != 'win':
            return
        arch = info['arch']
        assert arch in ('x86', 'x86_64'), arch
        for m in self.t.getmembers():
            if not m.name.lower().endswith(('.exe', '.dll')):
                continue
            data = self.t.extractfile(m.path).read(4096)
            tp = get_object_type(data)
            if arch == 'x86':
                assert tp == 'DLL I386', m.name
            if arch == 'x86_64':
                assert tp == 'DLL AMD64', m.name

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
        for x in res:
            print('    %s' % x)
        if self.name == 'deshaw':
            return
        for pkg_name in 'numpy', 'scipy':
            if self.name != pkg_name:
                assert pkg_name not in res, pkg_name
        if self.name not in ('setuptools', 'distribute', 'python'):
            for x in ('pkg_resources.py', 'setuptools.pth', 'easy_install.py',
                      'site.py', 'setuptools'):
                assert x not in res, res


def validate_package(path, verbose=False):
    x = TarCheck(path, verbose)
    x.info_files()
    x.not_allowed_files()
    x.info_misc()
    x.index_json()
    x.no_bat_and_exe()
    x.no_setuptools()
    x.no_pth()
    x.warn_pyo()
    x.no_py_next_so()
    x.no_pyc_in_stdlib()
    x.no_2to3_pickle()
    x.pyc_files()
    x.check_windows_arch()
    x.list_packages()
    x.t.close()
