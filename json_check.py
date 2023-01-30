"""Check that files contains valid JSON."""
import os
import fnmatch
import json


DEFAULTS = {
    'files': '*.json',
}


def check(file_staged_for_commit, options):
    basename = os.path.basename(file_staged_for_commit.path)
    if not fnmatch.fnmatch(basename, options.json_files):
        return True
    try:
        json.loads(file_staged_for_commit.contents)
    except ValueError:
        return False
    else:
        return True
