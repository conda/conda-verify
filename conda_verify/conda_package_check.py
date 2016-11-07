import json
import tarfile
import shlex
import re
from os.path import basename
from conda_verify.utils import get_bad_seq, all_ascii, get_object_type
from conda_verify.exceptions import PackageError


def dist_fn(fn):
    seq = get_bad_seq(fn)
    if seq:
        raise PackageError("'%s' not allowed in file name '%s'" % (seq, fn))
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
        self.win_pkg = bool(self.info['platform'] == 'win')
        if not all_ascii(raw, self.win_pkg):
            raise PackageError("non-ASCII in: info/index.json")

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

    def no_hardlinks(self):
        for m in self.t.getmembers():
            if m.islnk():
                raise PackageError('hardlink found: %s' % m.path)

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

    def _check_has_prefix_line(self, line, pedantic=True):
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
            if self.win_pkg:
                print("WARNING: info/has_prefix: binary replace mode "
                      "on Windows")
                return
            if len(placeholder) != 255:
                msg = ("info/has_prefix: binary placeholder not "
                       "255 bytes, but: %d" % len(placeholder))
                if pedantic:
                    raise PackageError(msg)
                else:
                    print("Warning: %s" % msg)
        elif mode == 'text':
            pass
        else:
            raise PackageError("info/has_prefix: invalid mode")

    def has_prefix(self, pedantic=True):
        for m in self.t.getmembers():
            if m.path != 'info/has_prefix':
                continue
            if self.win_pkg:
                print("WARNING: %s" % m.path)
            data = self.t.extractfile(m.path).read()
            if not all_ascii(data, self.win_pkg):
                raise PackageError("non-ASCII in: info/has_prefix")
            for line in data.decode('utf-8').splitlines():
                self._check_has_prefix_line(line, pedantic=pedantic)

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

    def no_easy_install_script(self, pedantic=True):
        if not pedantic:
            return
        for m in self.t.getmembers():
            if not m.name.startswith(('bin/', 'Scripts/')):
                continue
            if not m.isfile():
                continue
            data = self.t.extractfile(m.path).read(1024)
            if b'EASY-INSTALL-SCRIPT' in data:
                raise PackageError("easy install script found: %s" % m.name)

    def no_pth(self, pedantic=True):
        for p in self.paths:
            if pedantic and p.endswith('-nspkg.pth'):
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
        if self.name in {'python', 'scons', 'conda-build'}:
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
                         'phantomjs', 'qt', 'graphviz', 'nsis', 'swig'):
            return
        if not self.win_pkg:
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
