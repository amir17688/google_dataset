"""Check that file size less than limit."""
import fnmatch
import os.path


DEFAULTS = {
    'files': '*',
    'limit': str(10 * 1024 * 1024),
}


def check(file_staged_for_commit, options):
    basename = os.path.basename(file_staged_for_commit.path)
    if not fnmatch.fnmatch(basename, options.file_size_files):
        return True
    if file_staged_for_commit.size > int(options.file_size_limit):
        return False
    else:
        return True
