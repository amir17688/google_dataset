from __future__ import unicode_literals
import sublime
import os
import traceback
import functools
import sys
from functools import partial as bind
from . import sexp
from .sexp import key, sym
from .paths import *
from .sbt import *


def locations(window):
    """Intelligently guess the appropriate .ensime file locations for the
    given window. Return: list of possible locations."""
    return [(f + os.sep + ".ensime") for f in window.folders() if os.path.exists(f + os.sep + ".ensime")]


def exists(window):
    """Determines whether a .ensime file exists in one of the locations
    expected by `load`."""
    return len(locations(window)) != 0


def load(window):
    """Intelligently guess the appropriate .ensime file location for the
    given window. Load the .ensime and parse as s-expression.
    Return: (inferred project root directory, config sexp)
    """
    for f in locations(window):
        root = encode_path(os.path.dirname(f))
        with open(f) as open_file:
            src = open_file.read()
        try:
            conf = sexp.read_relaxed(src)
            m = sexp.sexp_to_key_map(conf)
            if m.get(":root-dir"):
                root = m[":root-dir"]
            else:
                conf = conf + [key(":root-dir"), root]
            return (root, conf, None)
        except:
            return (None, None, bind(error_bad_config, window, f, sys.exc_info()))
    return (None, None, bind(error_no_config, window))


def error_no_config(window):
    message = "Ensime has failed to find a .ensime file within this project\n"
    message += "Create a .ensime file by running 'sbt gen-ensime' or equivalent for your build tool and rerun "
    message += "Ensime: Startup"
    sublime.error_message(message)


def error_bad_config(window, f, ex):
    exc_type, exc_value, exc_tb = ex
    detailed_info = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(detailed_info)
    message = "Ensime has failed to parse the .ensime configuration file at " + str(
        f) + " because of the following error: "
    message += "\n\n"
    message += (str(exc_type) + ": " + str(exc_value))
    message += ("\n" + "(for detailed info refer to Sublime console)")
    message += "\n\n"
    message += "Sublime will now open the offending configuration file for you to fix. Do you wish to proceed?"
    if sublime.ok_cancel_dialog(message):
        edit(window)


def edit(window):
    window.open_file(locations(window)[0])
