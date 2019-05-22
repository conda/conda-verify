import re
import sys
from os import environ, getcwd, listdir, makedirs, rename, rmdir, unlink
from os.path import abspath, basename, dirname, exists, isdir, isfile, join, normpath, split, islink, lexists
from subprocess import check_output, CalledProcessError, STDOUT
import shutil

import jinja2
import yaml
from six import string_types
from concurrent.futures import Future, Executor
from threading import Lock

import future.builtins

from conda_verify.constants import MAGIC_HEADERS, DLL_TYPES

try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache


@lru_cache(maxsize=32)
def yamlize(data):
    res = yaml.load(data)
    # ensure the result is a dict
    if res is None:
        res = {}
    return res


def ns_cfg(cfg):
    plat = "-".join((cfg["platform"], cfg["arch"]))
    py = int("".join(cfg["python"].split(".")))
    np = int("".join(cfg["numpy"].split(".")))

    return dict(
        nomkl=False,
        debug=False,
        linux=plat.startswith("linux-"),
        linux32=bool(plat == "linux-32"),
        linux64=bool(plat == "linux-64"),
        armv7l=bool(plat == "linux-armv7l"),
        arm=bool(plat == "linux-armv7l"),
        ppc64le=bool(plat == "linux-ppc64le"),
        osx=plat.startswith("osx-"),
        unix=plat.startswith(("linux-", "osx-")),
        win=plat.startswith("win-"),
        win32=bool(plat == "win-32"),
        win64=bool(plat == "win-64"),
        x86=plat.endswith(("-32", "-64")),
        x86_64=plat.endswith("-64"),
        py=py,
        py3k=bool(30 <= py < 40),
        py2k=bool(20 <= py < 30),
        py26=bool(py == 26),
        py27=bool(py == 27),
        py33=bool(py == 33),
        py34=bool(py == 34),
        py35=bool(py == 35),
        py36=bool(py == 36),
        np=np,
    )


sel_pat = re.compile(r"(.+?)\s*\[(.+)\]$")


def select_lines(data, namespace):
    lines = []
    for line in data.splitlines():
        line = line.rstrip()
        m = sel_pat.match(line)
        if m:
            cond = m.group(2)
            if eval(cond, namespace, {}):
                lines.append(m.group(1))
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def parse(data, cfg):
    if cfg is not None:
        data = select_lines(data, ns_cfg(cfg))
    # ensure we create new object, because yamlize is memoized
    return dict(yamlize(data))


def render_jinja2(recipe_dir):
    loaders = [jinja2.FileSystemLoader(recipe_dir)]
    env = jinja2.Environment(loader=jinja2.ChoiceLoader(loaders))
    template = env.get_or_select_template("meta.yaml")
    return template.render(environment=env)


try:
    # circular dependency.  We only try this import so that conda-build is an optional
    #      conda-verify dep
    from conda_build import api

    def render_metadata(recipe_dir, cfg):
        m = api.render(
            recipe_dir, finalize=False, bypass_env_check=True, **(cfg if cfg else {})
        )[0][0]
        return m.get_rendered_recipe_text()


except ImportError:

    def render_metadata(recipe_dir, cfg):
        data = render_jinja2(recipe_dir)
        return parse(data, cfg)


def iter_cfgs():
    for py in "27", "34", "35":
        for plat in "linux-64", "linux-32", "osx-64", "win-32", "win-64":
            platform, arch = plat.split("-")
            yield dict(platform=platform, arch=arch, python=py, numpy="1.11")


def get_object_type(data):
    head = data[:4]
    if head not in MAGIC_HEADERS:
        return None
    lookup = MAGIC_HEADERS.get(head)
    if lookup == "DLL":
        pos = data.find(b"PE\0\0")
        if pos < 0:
            return "<no PE header found>"
        data = future.builtins.bytes(data)
        i = data[pos + 4] + 256 * data[pos + 5]
        return "DLL " + DLL_TYPES.get(i)
    elif lookup.startswith("MachO"):
        return lookup
    elif lookup == "ELF":
        return "ELF" + {"\x01": "32", "\x02": "64"}.get(data[4])


def get_bad_seq(s):
    for seq in ("--", "-.", "-_", ".-", "..", "._", "_-", "_."):  # but '__' is fine
        if seq in s:
            return seq
    return None


def all_ascii(data, allow_CR=False):
    newline = [10]  # LF
    if allow_CR:
        newline.append(13)  # CR
    for c in data:
        n = ord(c) if sys.version_info[0] == 2 else c
        if not (n in newline or 32 <= n < 127):
            return False
    return True


def ensure_list(argument):
    if isinstance(argument, list):
        return argument
    elif isinstance(argument, string_types):
        return argument.split(",")
    return [argument]


def fullmatch(regex, string, flags=0):
    """Emulate python-3.4 re.fullmatch().

    Credit: https://stackoverflow.com/questions/30212413/
    """
    return re.match("(?:" + regex + r")\Z", string, flags=flags)


# use this for debugging, because ProcessPoolExecutor isn't pdb/ipdb friendly
class DummyExecutor(Executor):
    def __init__(self):
        self._shutdown = False
        self._shutdownLock = Lock()

    def submit(self, fn, *args, **kwargs):
        with self._shutdownLock:
            if self._shutdown:
                raise RuntimeError("cannot schedule new futures after shutdown")

            f = Future()
            try:
                result = fn(*args, **kwargs)
            except BaseException as e:
                f.set_exception(e)
            else:
                f.set_result(result)

            return f

    def shutdown(self, wait=True):
        with self._shutdownLock:
            self._shutdown = True


#  Copied from conda because it is much faster and less deadlock-prone, but we don't want to include conda as a dep.

def which(executable):
    from distutils.spawn import find_executable
    return find_executable(executable)


def rmtree(path, *args, **kwargs):
    # subprocessing to delete large folders can be quite a bit faster
    path = normpath(path)
    if sys.platform == "win32":
        try:
            # the fastest way seems to be using DEL to recursively delete files
            # https://www.ghacks.net/2017/07/18/how-to-delete-large-folders-in-windows-super-fast/
            # However, this is not entirely safe, as it can end up following symlinks to folders
            # https://superuser.com/a/306618/184799
            # so, we stick with the slower, but hopefully safer way.  Maybe if we figured out how
            #    to scan for any possible symlinks, we could do the faster way.
            # out = check_output('DEL /F/Q/S *.* > NUL 2> NUL'.format(path), shell=True,
            #                    stderr=STDOUT, cwd=path)

            out = check_output('RD /S /Q "{}" > NUL 2> NUL'.format(path), shell=True,
                               stderr=STDOUT)
        except:
            try:
                # Try to delete in Unicode
                name = None
                from conda._vendor.auxlib.compat import Utf8NamedTemporaryFile
                from conda.utils import quote_for_shell

                with Utf8NamedTemporaryFile(mode="w", suffix=".bat", delete=False) as batch_file:
                    batch_file.write('RD /S {}\n'.format(quote_for_shell([path])))
                    batch_file.write('chcp 65001\n')
                    batch_file.write('RD /S {}\n'.format(quote_for_shell([path])))
                    batch_file.write('EXIT 0\n')
                    name = batch_file.name
                # If the above is bugged we can end up deleting hard-drives, so we check
                # that 'path' appears in it. This is not bulletproof but it could save you (me).
                with open(name, 'r') as contents:
                    content = contents.read()
                    assert path in content
                comspec = environ['COMSPEC']
                CREATE_NO_WINDOW = 0x08000000
                # It is essential that we `pass stdout=None, stderr=None, stdin=None` here because
                # if we do not, then the standard console handles get attached and chcp affects the
                # parent process (and any which share those console handles!)
                out = check_output([comspec, '/d', '/c', name], shell=False,
                                   stdout=None, stderr=None, stdin=None,
                                   creationflags=CREATE_NO_WINDOW)

            except CalledProcessError as e:
                pass
    else:
        try:
            makedirs('.empty')
        except:
            pass
        # yes, this looks strange.  See
        #    https://unix.stackexchange.com/a/79656/34459
        #    https://web.archive.org/web/20130929001850/http://linuxnote.net/jianingy/en/linux/a-fast-way-to-remove-huge-number-of-files.html  # NOQA
        rsync = which('rsync')
        if rsync and isdir('.empty'):
            try:
                out = check_output(
                    [rsync, '-a', '--delete', join(getcwd(), '.empty') + "/", path + "/"],
                    stderr=STDOUT)
            except CalledProcessError:
                pass
            shutil.rmtree('.empty')
    shutil.rmtree(path)


def unlink_or_rename_to_trash(path):
    """If files are in use, especially on windows, we can't remove them.
    The fallback path is to rename them (but keep their folder the same),
    which maintains the file handle validity.  See comments at:
    https://serverfault.com/a/503769
    """
    try:
        unlink(path)
    except EnvironmentError:
        try:
            rename(path, path + ".conda_trash")
        except EnvironmentError:
            pass


def remove_empty_parent_paths(path):
    # recurse to clean up empty folders that were created to have a nested hierarchy
    parent_path = dirname(path)
    while(isdir(parent_path) and not listdir(parent_path)):
        rmdir(parent_path)
        parent_path = dirname(parent_path)


def rm_rf(path, max_retries=5, trash=True, clean_empty_parents=False, *args, **kw):
    """
    Completely delete path
    max_retries is the number of times to retry on failure. The default is 5. This only applies
    to deleting a directory.
    If removing path fails and trash is True, files will be moved to the trash directory.
    """
    try:
        path = abspath(path)
        if isdir(path) and not islink(path):
            rmtree(path)
        elif lexists(path):
            unlink_or_rename_to_trash(path)
    finally:
        if lexists(path):
            return False
    if clean_empty_parents:
        remove_empty_parent_paths(path)
        return True
