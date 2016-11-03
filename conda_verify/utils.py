import sys
import collections
from os.path import join
import yaml
import re
from conda_verify.const import MAGIC_HEADERS, DLL_TYPES


class memoized(object):
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value


@memoized
def yamlize(data):
    res = yaml.load(data)
    # ensure the result is a dict
    if res is None:
        res = {}
    return res


def ns_cfg(cfg):
    plat = cfg['plat']
    py = cfg['PY']
    np = cfg['NPY']
    for x in py, np:
        assert isinstance(x, int), x
    return dict(
        nomkl = False,
        debug = False,
        linux = plat.startswith('linux-'),
        linux32 = bool(plat == 'linux-32'),
        linux64 = bool(plat == 'linux-64'),
        armv7l = False,
        arm = False,
        ppc64le = False,
        osx = plat.startswith('osx-'),
        unix = plat.startswith(('linux-', 'osx-')),
        win = plat.startswith('win-'),
        win32 = bool(plat == 'win-32'),
        win64 = bool(plat == 'win-64'),
        x86 = plat.endswith(('-32', '-64')),
        x86_64 = plat.endswith('-64'),
        py = py,
        py3k = bool(30 <= py < 40),
        py2k = bool(20 <= py < 30),
        py26 = bool(py == 26),
        py27 = bool(py == 27),
        py33 = bool(py == 33),
        py34 = bool(py == 34),
        py35 = bool(py == 35),
        np = np,
    )


sel_pat = re.compile(r'(.+?)\s*\[(.+)\]$')
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
    return '\n'.join(lines) + '\n'


def parse(data, cfg):
    if cfg is not None:
        data = select_lines(data, ns_cfg(cfg))
    # ensure we create new object, because yamlize is memoized
    return dict(yamlize(data))


def render_jinja2(recipe_dir):
    import jinja2

    loaders = [jinja2.FileSystemLoader(recipe_dir)]
    env = jinja2.Environment(loader=jinja2.ChoiceLoader(loaders))
    template = env.get_or_select_template('meta.yaml')
    return template.render(environment=env)


def render_metadata(recipe_dir, cfg):
    meta_path = join(recipe_dir, 'meta.yaml')
    with open(meta_path, 'rb') as fi:
        data = fi.read()
    if b'{{' in data:
        data = render_jinja2(recipe_dir)
    else:
        data = data.decode('utf-8')

    return parse(data, cfg)


def get_field(meta, field, default=None):
    section, key = field.split('/')
    submeta = meta.get(section)
    if submeta is None:
        submeta = {}
    res = submeta.get(key)
    if res is None:
        res = default
    return res


def iter_cfgs():
    for py in 27, 34, 35:
        for plat in 'linux-64', 'linux-32', 'osx-64', 'win-32', 'win-64':
            yield dict(plat=plat, PY=py, NPY=111)


def get_object_type(data):
    head = data[:4]
    if head not in MAGIC_HEADERS:
        return None
    lookup = MAGIC_HEADERS.get(head)
    if lookup == 'DLL':
        pos = data.find('PE\0\0')
        if pos < 0:
            return "<no PE header found>"
        i = ord(data[pos + 4]) + 256 * ord(data[pos + 5])
        return "DLL " + DLL_TYPES.get(i)
    elif lookup.startswith('MachO'):
        return lookup
    elif lookup == 'ELF':
        return "ELF" + {'\x01': '32', '\x02': '64'}.get(data[4])


def get_bad_seq(s):
    for seq in ('--', '-.', '-_',
                '.-', '..', '._',
                '_-', '_.'):  # but '__' is fine
        if seq in s:
            return seq
    return None


def all_ascii(data, allow_CR=False):
    newline = [10] # LF
    if allow_CR:
        newline.append(13) # CF
    for c in data:
        n = ord(c) if sys.version_info[0] == 2 else c
        if not (n in newline or 32 <= n < 127):
            return False
    return True


if __name__ == '__main__':
    print(sys.version)
    print(all_ascii(b'Hello\x00'), all_ascii(b"Hello World!"))
