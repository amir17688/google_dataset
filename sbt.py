import sublime
import os
from functools import partial as bind


def _sbt_binary():
    return sublime.load_settings("Ensime.sublime-settings").get("sbt_binary", "sbt")


def _sbt_binary_exists():
    def check_file(fullpath):
        try:
            os.stat(fullpath)
            return True
        except os.error:
            pass

    if check_file(_sbt_binary()):
        return True
    for pathdir in os.environ["PATH"].split(os.pathsep):
        fname = os.path.join(pathdir, _sbt_binary())
        if check_file(fname):
            return True


def _sbt_flags():
    return sublime.load_settings("Ensime.sublime-settings").get("sbt_flags", ["-Dsbt.log.noformat=true"])


def sbt_binary_and_flags():
    if _sbt_binary() and _sbt_binary_exists():
        return [_sbt_binary()] + _sbt_flags()
    else:
        return None

def sbt_command(*args):
    if _sbt_binary() and _sbt_binary_exists():
        return [_sbt_binary()] + _sbt_flags() + list(args)
    else:
        message = "Configured path for the SBT binary, namely: " + _sbt_binary() + ", does not exist "
        message += "and cannot be resolved from your Sublime's PATH, namely: " + os.environ["PATH"] + "."
        message += "\n\n"
        message += "Consider updating the \"sbt_binary\" entry in Ensime configuration via "
        message += "Preferences > Package Settings > Ensime or adjusting your PATH. "
        message += "(Note that on Mac OS, Sublime doesn't read .bashrc or .bash_profile on startup, so "
        message += "it might be easier to provide an absolute path to the SBT binary rather than to try "
        message += "adjusting Sublime's PATH)."
        sublime.set_timeout(bind(sublime.error_message, message), 0)
        return None
