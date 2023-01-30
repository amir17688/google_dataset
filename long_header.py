# This file helps to compute a version number in source trees obtained from
# git-archive tarball (such as those provided by githubs download-from-tag
# feature). Distribution tarballs (built by setup.py sdist) and build
# directories (produced by setup.py build) will contain a much shorter file
# that just contains the computed version number.

# This file is released into the public domain. Generated by
# versioneer-@VERSIONEER-VERSION@ (https://github.com/warner/python-versioneer)

"""Git implementation of _version.py."""

import errno
import os
import re
import subprocess
import sys


def get_keywords():
    """Get the keywords needed to look up the version information."""
    # these strings will be replaced by git during git-archive.
    # setup.py/versioneer.py will grep for the variable names, so they must
    # each be defined on a line of their own. _version.py will just call
    # get_keywords().
    git_refnames = "%(DOLLAR)sFormat:%%d%(DOLLAR)s"
    git_full = "%(DOLLAR)sFormat:%%H%(DOLLAR)s"
    keywords = {"refnames": git_refnames, "full": git_full}
    return keywords


class VersioneerConfig:
    """Container for Versioneer configuration parameters."""


def get_config():
    """Create, populate and return the VersioneerConfig() object."""
    # these strings are filled in when 'setup.py versioneer' creates
    # _version.py
    cfg = VersioneerConfig()
    cfg.VCS = "git"
    cfg.style = "%(STYLE)s"
    cfg.tag_prefix = "%(TAG_PREFIX)s"
    cfg.parentdir_prefix = "%(PARENTDIR_PREFIX)s"
    cfg.versionfile_source = "%(VERSIONFILE_SOURCE)s"
    cfg.verbose = False
    return cfg


class NotThisMethod(Exception):
    """Exception raised if a method is not valid for the current scenario."""


LONG_VERSION_PY = {}
HANDLERS = {}


def register_vcs_handler(vcs, method):  # decorator
    """Decorator to mark a method as the handler for a particular VCS."""
    def decorate(f):
        """Store f in HANDLERS[vcs][method]."""
        if vcs not in HANDLERS:
            HANDLERS[vcs] = {}
        HANDLERS[vcs][method] = f
        return f
    return decorate
