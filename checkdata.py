# -*- coding: UTF-8 -*-
# Copyright 2015 Luc Saffre
# License: BSD (see file COPYING for details)
"""Runs the :manage:`checkdata` management command with `--fix`
option.

"""

from django.core.management import call_command


def objects():
    call_command('checkdata', fix=True)
    return []
int(Command.help)

In other words, this command does the same as if a user would click on
the button with the bell ("Check plausibility") on each database
object for which there are data checkers.

"""

from __future__ import unicode_literals, print_function

from optparse import make_option
from clint.textui import puts, progress

from django.utils import translation
from django.core.management.base import BaseCommand

from lino.modlib.plausibility.choicelists import Checkers
from lino.modlib.plausibility.models import get_checkable_models

from lino.api import rt


def check_plausibility(args=[], fix=True):
    """Called by :manage:`check_plausibility`. See there."""
    Problem = rt.modules.plausibility.Problem
    mc = get_checkable_models(*args)
    with translation.override('en'):
        for m, checkers in mc.items():
            ct = rt.modules.contenttypes.ContentType.objects.get_for_model(m)
            Problem.objects.filter(owner_type=ct).delete()
            name = unicode(m._meta.verbose_name_plural)
            qs = m.objects.all()
            msg = "Running {0} plausibility checkers on {1} {2}...".format(
                len(checkers), qs.count(), name)
            puts(msg)
            sums = [0, 0, name]
            for obj in progress.bar(qs):
                for chk in checkers:
                    todo, done = chk.update_problems(obj, False, fix)
                    sums[0] += len(todo)
                    sums[1] += len(done)
            if sums[0] or sums[1]:
                msg = "Found {0} and fixed {1} plausibility problems in {2}."
                puts(msg.format(*sums))
            else:
                puts("No plausibility problems found in {0}.".format(name))


class Command(BaseCommand):
    args = "[app1.Model1.Checker1] [app2.Model2.Checker2] ..."
    help = """

    Update the table of plausibility problems.

    If no arguments are given, run it on all plausibility checkers.
    Otherwise every positional argument is expected to be a model name in
    the form `app_label.ModelName`, and only these models are being
    updated.

    """

    option_list = BaseCommand.option_list + (
        make_option(
            '-l', '--list', action='store_true', dest='list',
            default=False,
            help="Don't check, just show a list of available checkers."),
        make_option(
            '-f', '--fix', action='store_true', dest='fix',
            default=False,
            help="Fix any repairable problems."),
    )

    def handle(self, *args, **options):
        if options['list']:
            Checkers.show()
        else:
            rt.startup()
            check_plausibility(args=args, fix=options['fix'])
