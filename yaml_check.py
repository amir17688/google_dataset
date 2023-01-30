"""Check that files contains valid YAML."""
import os
import fnmatch
import yaml


DEFAULTS = {
    'files': '*.yaml',
}


def check(file_staged_for_commit, options):
    basename = os.path.basename(file_staged_for_commit.path)
    if not fnmatch.fnmatch(basename, options.yaml_files):
        return True
    try:
        yaml.load(file_staged_for_commit.contents)
    except yaml.error.YAMLError as e:
        print(e)
        return False
    else:
        return True
