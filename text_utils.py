"""
Set of small utility functions that take text strings as input.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

from cld2 import detect as cld2_detect

from textacy.compat import PY2, str
from textacy.regexes_etc import ACRONYM_REGEX


def is_acronym(token, exclude=None):
    """
    Pass single token as a string, return True/False if is/is not valid acronym.

    Args:
        token (str): single word to check for acronym-ness
        exclude (set[str]): if technically valid but not actually good acronyms
        are known in advance, pass them in as a set of strings; matching tokens
        will return False

    Returns:
        bool
    """
    # exclude certain valid acronyms from consideration
    if exclude and token in exclude:
        return False
    # don't allow empty strings
    if not token:
        return False
    # don't allow spaces
    if ' ' in token:
        return False
    # 2-character acronyms can't have lower-case letters
    if len(token) == 2 and not token.isupper():
        return False
    # acronyms can't be all digits
    if token.isdigit():
        return False
    # acronyms must have at least one upper-case letter or start/end with a digit
    if (not any(char.isupper() for char in token)
            and not (token[0].isdigit() or token[-1].isdigit())):
        return False
    # acronyms must have between 2 and 10 alphanumeric characters
    if not 2 <= sum(1 for char in token if char.isalnum()) <= 10:
        return False
    # only certain combinations of letters, digits, and '&/.-' allowed
    if not ACRONYM_REGEX.match(token):
        return False
    return True


def detect_language(text):
    """
    Detect the most likely language of a text and return its 2-letter code
    (see https://cloud.google.com/translate/v2/using_rest#language-params).
    Uses the `cld2-cffi <https://pypi.python.org/pypi/cld2-cffi>`_ package;
    to take advantage of optional params, call :func:`cld2.detect()` directly.

    Args:
        text (str)

    Returns:
        str
    """
    if PY2:
        is_reliable, _, best_guesses = cld2_detect(str(text).encode('utf8'), bestEffort=True)
    else:
        is_reliable, _, best_guesses = cld2_detect(str(text), bestEffort=True)
    if is_reliable is False:
        msg = '**WARNING: Text language detected with low confidence; best guesses: {}'
        print(msg.format(best_guesses))
    return best_guesses[0][1]


def keyword_in_context(text, keyword, ignore_case=True,
                       window_width=50, print_only=True):
    """
    Search for ``keyword`` in ``text`` via regular expression, return or print strings
    spanning ``window_width`` characters before and after each occurrence of keyword.

    Args:
        text (str): text in which to search for ``keyword``
        keyword (str): technically, any valid regular expression string should work,
            but usually this is a single word or short phrase: "spam", "spam and eggs";
            to account for variations, use regex: "[Ss]pam (and|&) [Ee]ggs?"

            N.B. If keyword contains special characters, be sure to escape them!!!
        ignore_case (bool, optional): if True, ignore letter case in `keyword` matching
        window_width (int, optional): number of characters on either side of
            `keyword` to include as "context"
        print_only (bool, optional): if True, print out all results with nice
            formatting; if False, return all (pre, kw, post) matches as generator
            of raw strings

    Returns:
        generator(tuple(str, str, str)), or None
    """
    flags = re.IGNORECASE if ignore_case is True else 0
    if print_only is True:
        for match in re.finditer(keyword, text, flags=flags):
            print('{pre} {kw} {post}'.format(
                    pre=text[max(0, match.start() - window_width): match.start()].rjust(window_width),
                    kw=match.group(),
                    post=text[match.end(): match.end() + window_width].ljust(window_width)))
    else:
        return ((text[max(0, match.start() - window_width): match.start()],
                 match.group(),
                 text[match.end(): match.end() + window_width])
                for match in re.finditer(keyword, text, flags=flags))
