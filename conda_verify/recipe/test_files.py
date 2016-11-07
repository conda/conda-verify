import os
from os.path import join, isfile, basename, getsize
from conda_verify.utils import iter_cfgs, get_field
from conda_verify.exceptions import RecipeError


def dir_size(dir_path):
    return sum(sum(getsize(join(root, fn)) for fn in files)
               for root, unused_dirs, files in os.walk(dir_path))


def check_dir_content(recipe_dir):
    disallowed_extensions = (
        '.tar', '.tar.gz', '.tar.bz2', '.tar.xz',
        '.so', '.dylib', '.la', '.a', '.dll', '.pyd',
    )
    for root, unused_dirs, files in os.walk(recipe_dir):
        for fn in files:
            fn_lower = fn.lower()
            if fn_lower.endswith(disallowed_extensions):
                raise RecipeError("found: %s" % fn)
            path = join(root, fn)
            # only allow small archives for testing
            if  (fn_lower.endswith(('.bz2', '.gz')) and
                         getsize(path) > 512):
                raise RecipeError("found: %s (too large)" % fn)

    if basename(recipe_dir) == 'icu':
        return

    # check total size od recipe directory (recursively)
    kb_size = dir_size(recipe_dir) / 1024
    kb_limit = 512
    if  kb_size > kb_limit:
        raise RecipeError("recipe too large: %d KB (limit %d KB)" %
                          (kb_size, kb_limit))


def validate_files(recipe_dir, meta):
    for field in 'test/files', 'source/patches':
        flst = get_field(meta, field)
        if not flst:
            continue
        for fn in flst:
            if fn.startswith('..'):
                raise RecipeError("path outsite recipe: %s" % fn)
            path = join(recipe_dir, fn)
            if isfile(path):
               continue
            raise RecipeError("no such file '%s'" % path)


def verify(rendered_meta=None, recipe_dir=None, **kwargs):
    meta_path = join(recipe_dir, 'meta.yaml')
    for cfg in iter_cfgs():
        validate_files(recipe_dir, rendered_meta)
