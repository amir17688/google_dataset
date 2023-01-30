"""
    Patchemy
    ~~~~~~~~

    Create a more powerful SQLAlchemy.

    :copyright: (c) 2014 Eleme
    :license: MIT
"""

__all__ = ["monkey_patch", "patch_sqlalchemy"]

import json
import uuid
from sqlalchemy.dialects.postgresql import UUID as _UUID
from sqlalchemy.dialects.postgresql import JSON as _JSON
from sqlalchemy.util import py2k
from sqlalchemy.types import TypeDecorator, VARCHAR, TEXT


def monkey_patch():
    patch_sqlalchemy()


def patch_sqlalchemy():
    import sqlalchemy
    sqlalchemy.UUID = UUID
    sqlalchemy.__all__.append('UUID')
    sqlalchemy.JSON = JSON
    sqlalchemy.__all__.append('JSON')


class UUID(TypeDecorator):
    """Platform-independent UUID type.

    Uses Postgresql's UUID type, otherwise uses VARCHAR(36), storing as
    stringified hex values.
    """
    impl = VARCHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(_UUID(as_uuid=True))
        return dialect.type_descriptor(VARCHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        return uuid.UUID(value)


class JSON(TypeDecorator):
    """Platform-independent JSON type.

    Uses Postgresql's JSON type, otherwise uses TEXT, storing as json str.
    """

    impl = TEXT

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(_JSON())
        return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value
        if py2k:
            encoding = dialect.encoding
            return json.dumps(value).encode(encoding)
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        if dialect.name == 'postgresql':
            return value

        if py2k:
            encoding = dialect.encoding
            return json.loads(value.decode(encoding))
        return json.loads(value)
