# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from functools import partial
import hashlib
import json
from logging import getLogger
from os.path import getsize, join
from textwrap import dedent

from conda_verify.exceptions import PackageError

log = getLogger(__name__)


def verify(extracted_package_dir, verbose=True, **kwargs):
    with open(join(extracted_package_dir, 'info', 'paths.json')) as fh:
        paths_data = json.loads(fh.read())

    hash_mismatches = []
    ok_count = 0
    for path_data in paths_data['paths']:
        path = path_data['_path']
        recorded_sha256 = path_data['sha256']
        recorded_size_in_bytes = path_data['size_in_bytes']
        actual_sha256 = compute_sha256sum(join(extracted_package_dir, path))
        actual_size_in_bytes = getsize(join(extracted_package_dir, path))
        if recorded_sha256 != actual_sha256 or recorded_size_in_bytes != actual_size_in_bytes:
            hash_mismatches.append(
                (path, recorded_sha256, actual_sha256, recorded_size_in_bytes,
                 actual_size_in_bytes)
            )
        else:
            ok_count += 1

    if hash_mismatches:
        builder = []
        for mismatch in hash_mismatches:
            builder.append(dedent("""\
                  error for path: %s
                    recorded sha256: %s
                    actual sha256:   %s
                    recorded size:   %s
                    actual size:     %s
                  """) % mismatch)
        raise PackageError('\n'.join(builder))


def _digest_path(algo, path):
    hasher = hashlib.new(algo)
    with open(path, "rb") as fh:
        for chunk in iter(partial(fh.read, 8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_sha256sum(file_full_path):
    return _digest_path('sha256', file_full_path)
