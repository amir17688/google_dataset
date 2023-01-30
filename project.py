# -*- coding: utf-8 -*-
"""
gate.project
~~~~~~~~~~~~

This module defines the Project class. This class represents the
current project, from the user perspective.
"""

from os import listdir, walk
from collections import defaultdict
from os.path import basename, dirname, join, sep, exists

from gate.utils import v
from gate.utils import settings
from gate.utils.misc import fnmatch


class Ignored(dict):
    """For each file, cache the result of matching its file name against
    'g:gate_ignore' patterns."""

    def __init__(self):
        self.patterns = settings.get("ignore")

    def __missing__(self, fpath):
        self[fpath] = fnmatch(fpath, self.patterns)
        return self[fpath]

_ignored = Ignored()


class Profile(defaultdict):
    """For each file, cache the profile it belongs to."""

    def __init__(self):
        super(Profile, self).__init__(list)
        self.profiles = settings.get("profiles").items()

    def __missing__(self, fpath):
        super(Profile, self).__missing__(fpath)
        for profile, patterns in self.profiles:
            if fnmatch(fpath, patterns):
                self[fpath].append(profile)
        return self.get(fpath, [])

_profile = Profile()


class Project:

    def __init__(self):
        self.project_root = ""
        self.project_files = defaultdict(list)
        self.last_profile = None
        self._setup_cache_rules()

    def _setup_cache_rules(self):
        """To set up rules for when the cache needs to be updated."""
        v.exe("augroup gate_project")
        v.exe("au!")
        v.exe("au BufEnter * py _gate.project._reset_cache_if_project_changed()")
        v.exe("au BufWritePre * py _gate.project._reset_cache_if_file_created()")
        v.exe("augroup END")

    def _reset_cache_if_project_changed(self):
        """To reset the cache if the current project has changed."""
        buf = v.bufname()
        if not v.opt("bt") and not buf.startswith(self.project_root + sep):
            self.project_root = ""
            self.project_files = defaultdict(list)

    def _reset_cache_if_file_created(self):
        """To reset the cache if a new file is created in the current project."""
        buf = v.bufname()
        if not exists(buf) and buf.startswith(self.project_root + sep):
            self.project_files = defaultdict(list)

    def get_files(self, profile, curr_buf):
        """To return all files for the given profile."""
        if not self.get_root():
            return []
        if not self.project_files:
            self._load_files()
        notvisible = lambda f: f != curr_buf
        return filter(notvisible, self.project_files.get(profile, []))

    def _load_files(self):
        """To load all files of the current project."""
        for fpath in self._files():
            for profile in _profile[fpath]:
                self.project_files[profile].append(fpath)

    def _files(self):
        """To get all files of the current project.

        Hidden files and files that match glob patterns in `gate_ignore` are
        ignored.
        """
        hidden = lambda f: f.startswith(".")
        for root, dirs, files in walk(self.project_root):
            dirs[:] = [d for d in dirs if not hidden(d) and not _ignored[join(root, d)+sep]]
            for fname in files:
                if not hidden(fname) and not _ignored[join(root, fname)]:
                    yield join(root, fname)

    def get_root(self):
        """To return the current project root."""
        if not self.project_root:
            self._update_root()
        return self.project_root

    def _update_root(self):
        """To update the current project root."""
        markers = settings.get("root_markers")
        self.project_root = self._find_root(v.cwd(), markers)

    def _find_root(self, path, root_markers):
        """To find the the root of the current project.

        `root_markers` is a list of file names the can be found in
        a project root directory.
        """
        if path == "/" or path.endswith(":\\"):
            return u""
        elif any(m in listdir(path) for m in root_markers):
            return path
        else:
            return self._find_root(dirname(path), root_markers)
