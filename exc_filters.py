#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Define exception redefinitions for SQLAlchemy DBAPI exceptions."""

import collections
import logging
import re

from sqlalchemy import event
from sqlalchemy import exc as sqla_exc

from oslo_db._i18n import _LE
from oslo_db import exception


LOG = logging.getLogger(__name__)


_registry = collections.defaultdict(
    lambda: collections.defaultdict(
        list
    )
)


def filters(dbname, exception_type, regex):
    """Mark a function as receiving a filtered exception.

    :param dbname: string database name, e.g. 'mysql'
    :param exception_type: a SQLAlchemy database exception class, which
     extends from :class:`sqlalchemy.exc.DBAPIError`.
    :param regex: a string, or a tuple of strings, that will be processed
     as matching regular expressions.

    """
    def _receive(fn):
        _registry[dbname][exception_type].extend(
            (fn, re.compile(reg))
            for reg in
            ((regex,) if not isinstance(regex, tuple) else regex)
        )
        return fn
    return _receive


# NOTE(zzzeek) - for Postgresql, catch both OperationalError, as the
# actual error is
# psycopg2.extensions.TransactionRollbackError(OperationalError),
# as well as sqlalchemy.exc.DBAPIError, as SQLAlchemy will reraise it
# as this until issue #3075 is fixed.
@filters("mysql", sqla_exc.OperationalError, r"^.*\b1213\b.*Deadlock found.*")
@filters("mysql", sqla_exc.OperationalError,
         r"^.*\b1205\b.*Lock wait timeout exceeded.*")
@filters("mysql", sqla_exc.InternalError, r"^.*\b1213\b.*Deadlock found.*")
@filters("postgresql", sqla_exc.OperationalError, r"^.*deadlock detected.*")
@filters("postgresql", sqla_exc.DBAPIError, r"^.*deadlock detected.*")
@filters("ibm_db_sa", sqla_exc.DBAPIError, r"^.*SQL0911N.*")
def _deadlock_error(operational_error, match, engine_name, is_disconnect):
    """Filter for MySQL or Postgresql deadlock error.

    NOTE(comstud): In current versions of DB backends, Deadlock violation
    messages follow the structure:

    mysql+mysqldb:
    (OperationalError) (1213, 'Deadlock found when trying to get lock; try '
                         'restarting transaction') <query_str> <query_args>

    mysql+mysqlconnector:
    (InternalError) 1213 (40001): Deadlock found when trying to get lock; try
                         restarting transaction

    postgresql:
    (TransactionRollbackError) deadlock detected <deadlock_details>


    ibm_db_sa:
    SQL0911N The current transaction has been rolled back because of a
    deadlock or timeout <deadlock details>

    """
    raise exception.DBDeadlock(operational_error)


@filters("mysql", sqla_exc.IntegrityError,
         r"^.*\b1062\b.*Duplicate entry '(?P<value>.+)'"
         r" for key '(?P<columns>[^']+)'.*$")
# NOTE(jd) For binary types
@filters("mysql", sqla_exc.IntegrityError,
         r"^.*\b1062\b.*Duplicate entry \\'(?P<value>.+)\\'"
         r" for key \\'(?P<columns>.+)\\'.*$")
# NOTE(pkholkin): the first regex is suitable only for PostgreSQL 9.x versions
#                 the second regex is suitable for PostgreSQL 8.x versions
@filters("postgresql", sqla_exc.IntegrityError,
         (r'^.*duplicate\s+key.*"(?P<columns>[^"]+)"\s*\n.*'
          r'Key\s+\((?P<key>.*)\)=\((?P<value>.*)\)\s+already\s+exists.*$',
          r"^.*duplicate\s+key.*\"(?P<columns>[^\"]+)\"\s*\n.*$"))
def _default_dupe_key_error(integrity_error, match, engine_name,
                            is_disconnect):
    """Filter for MySQL or Postgresql duplicate key error.

    note(boris-42): In current versions of DB backends unique constraint
    violation messages follow the structure:

    postgres:
    1 column - (IntegrityError) duplicate key value violates unique
               constraint "users_c1_key"
    N columns - (IntegrityError) duplicate key value violates unique
               constraint "name_of_our_constraint"

    mysql+mysqldb:
    1 column - (IntegrityError) (1062, "Duplicate entry 'value_of_c1' for key
               'c1'")
    N columns - (IntegrityError) (1062, "Duplicate entry 'values joined
               with -' for key 'name_of_our_constraint'")

    mysql+mysqlconnector:
    1 column - (IntegrityError) 1062 (23000): Duplicate entry 'value_of_c1' for
               key 'c1'
    N columns - (IntegrityError) 1062 (23000): Duplicate entry 'values
               joined with -' for key 'name_of_our_constraint'



    """

    columns = match.group('columns')

    # note(vsergeyev): UniqueConstraint name convention: "uniq_t0c10c2"
    #                  where `t` it is table name and columns `c1`, `c2`
    #                  are in UniqueConstraint.
    uniqbase = "uniq_"
    if not columns.startswith(uniqbase):
        if engine_name == "postgresql":
            columns = [columns[columns.index("_") + 1:columns.rindex("_")]]
        else:
            columns = [columns]
    else:
        columns = columns[len(uniqbase):].split("0")[1:]

    value = match.groupdict().get('value')

    raise exception.DBDuplicateEntry(columns, integrity_error, value)


@filters("sqlite", sqla_exc.IntegrityError,
         (r"^.*columns?(?P<columns>[^)]+)(is|are)\s+not\s+unique$",
          r"^.*UNIQUE\s+constraint\s+failed:\s+(?P<columns>.+)$",
          r"^.*PRIMARY\s+KEY\s+must\s+be\s+unique.*$"))
def _sqlite_dupe_key_error(integrity_error, match, engine_name, is_disconnect):
    """Filter for SQLite duplicate key error.

    note(boris-42): In current versions of DB backends unique constraint
    violation messages follow the structure:

    sqlite:
    1 column - (IntegrityError) column c1 is not unique
    N columns - (IntegrityError) column c1, c2, ..., N are not unique

    sqlite since 3.7.16:
    1 column - (IntegrityError) UNIQUE constraint failed: tbl.k1
    N columns - (IntegrityError) UNIQUE constraint failed: tbl.k1, tbl.k2

    sqlite since 3.8.2:
    (IntegrityError) PRIMARY KEY must be unique

    """
    columns = []
    # NOTE(ochuprykov): We can get here by last filter in which there are no
    #                   groups. Trying to access the substring that matched by
    #                   the group will lead to IndexError. In this case just
    #                   pass empty list to exception.DBDuplicateEntry
    try:
        columns = match.group('columns')
        columns = [c.split('.')[-1] for c in columns.strip().split(", ")]
    except IndexError:
        pass

    raise exception.DBDuplicateEntry(columns, integrity_error)


@filters("sqlite", sqla_exc.IntegrityError,
         r"(?i).*foreign key constraint failed")
@filters("postgresql", sqla_exc.IntegrityError,
         r".*on table \"(?P<table>[^\"]+)\" violates "
         "foreign key constraint \"(?P<constraint>[^\"]+)\".*\n"
         "DETAIL:  Key \((?P<key>.+)\)=\(.+\) "
         "is (not present in|still referenced from) table "
         "\"(?P<key_table>[^\"]+)\".")
@filters("mysql", sqla_exc.IntegrityError,
         r".* u?'Cannot (add|delete) or update a (child|parent) row: "
         'a foreign key constraint fails \([`"].+[`"]\.[`"](?P<table>.+)[`"], '
         'CONSTRAINT [`"](?P<constraint>.+)[`"] FOREIGN KEY '
         '\([`"](?P<key>.+)[`"]\) REFERENCES [`"](?P<key_table>.+)[`"] ')
def _foreign_key_error(integrity_error, match, engine_name, is_disconnect):
    """Filter for foreign key errors."""

    try:
        table = match.group("table")
    except IndexError:
        table = None
    try:
        constraint = match.group("constraint")
    except IndexError:
        constraint = None
    try:
        key = match.group("key")
    except IndexError:
        key = None
    try:
        key_table = match.group("key_table")
    except IndexError:
        key_table = None

    raise exception.DBReferenceError(table, constraint, key, key_table,
                                     integrity_error)


@filters("postgresql", sqla_exc.IntegrityError,
         r".*new row for relation \"(?P<table>.+)\" "
         "violates check constraint "
         "\"(?P<check_name>.+)\"")
def _check_constraint_error(
        integrity_error, match, engine_name, is_disconnect):
    """Filter for check constraint errors."""

    try:
        table = match.group("table")
    except IndexError:
        table = None
    try:
        check_name = match.group("check_name")
    except IndexError:
        check_name = None

    raise exception.DBConstraintError(table, check_name, integrity_error)


@filters("ibm_db_sa", sqla_exc.IntegrityError, r"^.*SQL0803N.*$")
def _db2_dupe_key_error(integrity_error, match, engine_name, is_disconnect):
    """Filter for DB2 duplicate key errors.

    N columns - (IntegrityError) SQL0803N  One or more values in the INSERT
                statement, UPDATE statement, or foreign key update caused by a
                DELETE statement are not valid because the primary key, unique
                constraint or unique index identified by "2" constrains table
                "NOVA.KEY_PAIRS" from having duplicate values for the index
                key.

    """

    # NOTE(mriedem): The ibm_db_sa integrity error message doesn't provide the
    # columns so we have to omit that from the DBDuplicateEntry error.
    raise exception.DBDuplicateEntry([], integrity_error)


@filters("mysql", sqla_exc.DBAPIError, r".*\b1146\b")
def _raise_mysql_table_doesnt_exist_asis(
        error, match, engine_name, is_disconnect):
    """Raise MySQL error 1146 as is.

    Raise MySQL error 1146 as is, so that it does not conflict with
    the MySQL dialect's checking a table not existing.
    """

    raise error


@filters("mysql", sqla_exc.OperationalError,
         r".*(1292|1366).*Incorrect \w+ value.*")
@filters("mysql", sqla_exc.DataError,
         r".*1265.*Data truncated for column.*")
@filters("mysql", sqla_exc.DataError,
         r".*1264.*Out of range value for column.*")
@filters("mysql", sqla_exc.InternalError,
         r"^.*1366.*Incorrect string value:*")
@filters("sqlite", sqla_exc.ProgrammingError,
         r"(?i).*You must not use 8-bit bytestrings*")
def _raise_data_error(error, match, engine_name, is_disconnect):
    """Raise DBDataError exception for different data errors."""

    raise exception.DBDataError(error)


@filters("*", sqla_exc.OperationalError, r".*")
def _raise_operational_errors_directly_filter(operational_error,
                                              match, engine_name,
                                              is_disconnect):
    """Filter for all remaining OperationalError classes and apply.

    Filter for all remaining OperationalError classes and apply
    special rules.
    """
    if is_disconnect:
        # operational errors that represent disconnect
        # should be wrapped
        raise exception.DBConnectionError(operational_error)
    else:
        # NOTE(comstud): A lot of code is checking for OperationalError
        # so let's not wrap it for now.
        raise operational_error


@filters("mysql", sqla_exc.OperationalError, r".*\(.*(?:2002|2003|2006|2013|1047)")  # noqa
@filters("postgresql", sqla_exc.OperationalError, r".*could not connect to server")  # noqa
@filters("ibm_db_sa", sqla_exc.OperationalError, r".*(?:30081)")
def _is_db_connection_error(operational_error, match, engine_name,
                            is_disconnect):
    """Detect the exception as indicating a recoverable error on connect."""
    raise exception.DBConnectionError(operational_error)


@filters("*", sqla_exc.DBAPIError, r".*")
def _raise_for_remaining_DBAPIError(error, match, engine_name, is_disconnect):
    """Filter for remaining DBAPIErrors.

    Filter for remaining DBAPIErrors and wrap if they represent
    a disconnect error.
    """
    if is_disconnect:
        raise exception.DBConnectionError(error)
    else:
        LOG.exception(
            _LE('DBAPIError exception wrapped from %s') % error)
        raise exception.DBError(error)


@filters('*', UnicodeEncodeError, r".*")
def _raise_for_unicode_encode(error, match, engine_name, is_disconnect):
    raise exception.DBInvalidUnicodeParameter()


@filters("*", Exception, r".*")
def _raise_for_all_others(error, match, engine_name, is_disconnect):
    LOG.exception(_LE('DB exception wrapped.'))
    raise exception.DBError(error)


def handler(context):
    """Iterate through available filters and invoke those which match.

    The first one which raises wins.   The order in which the filters
    are attempted is sorted by specificity - dialect name or "*",
    exception class per method resolution order (``__mro__``).
    Method resolution order is used so that filter rules indicating a
    more specific exception class are attempted first.

    """
    def _dialect_registries(engine):
        if engine.dialect.name in _registry:
            yield _registry[engine.dialect.name]
        if '*' in _registry:
            yield _registry['*']

    for per_dialect in _dialect_registries(context.engine):
        for exc in (
                context.sqlalchemy_exception,
                context.original_exception):
            for super_ in exc.__class__.__mro__:
                if super_ in per_dialect:
                    regexp_reg = per_dialect[super_]
                    for fn, regexp in regexp_reg:
                        match = regexp.match(exc.args[0])
                        if match:
                            try:
                                fn(
                                    exc,
                                    match,
                                    context.engine.dialect.name,
                                    context.is_disconnect)
                            except exception.DBConnectionError:
                                context.is_disconnect = True
                                raise


def register_engine(engine):
    event.listen(engine, "handle_error", handler)


def handle_connect_error(engine):
    """Connect to the engine, including handle_error handlers.

    The compat library now builds this into the engine.connect()
    system as per SQLAlchemy 1.0's behavior.

    """
    return engine.connect()
