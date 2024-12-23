from typing import Any, Literal

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.backends.utils import names_digest  # pyright: ignore[reportAttributeAccessIssue]
from django.db.backends.utils import split_identifier

from django_utils.helpers import isallinstance


def create_generic_index_name(
    table_name: str,
    fields: tuple[str, ...] | list[str] | set[str],
    suffix: str = '',
) -> str:
    """
    Generate a unique name for the index.

    The name is divided into 3 parts - table name (12 chars), field name
    (8 chars) and unique hash + suffix (10 chars). Each part is made to
    fit its size by truncating the excess length.
    """
    # pylint: disable=import-outside-toplevel
    from django.utils.translation import gettext_lazy as _

    # pylint: enable=import-outside-toplevel

    if not isinstance(table_name, str):
        raise TypeError(_("'table_name' must be str"))
    if not isallinstance(fields, str):
        raise TypeError(_("'fields' must be a tuple, list or set of str"))
    if not isinstance(suffix, str):
        raise TypeError(_("'suffix' must be str"))

    table_name = table_name.lower()
    _, table_name = split_identifier(table_name)
    fields_orders: list[tuple[str, str]] = [
        (field_name[1:], 'DESC') if field_name.startswith('-') else (field_name, '')
        for field_name in fields
    ]
    column_names: list[str] = [field_name for field_name, order in fields_orders]
    column_names_with_order: list[str] = [
        (('-%s' if order else '%s') % column_name)
        for column_name, (field_name, order) in zip(column_names, fields_orders)
    ]
    # The length of the parts of the name is based on the default max
    # length of 30 characters.
    hash_data: list[str] = [table_name] + column_names_with_order + [suffix]
    hash_length = 9 - len(suffix)
    name: str = (
        f'{table_name[:11]}_{column_names[0][:7]}_{names_digest(*hash_data, length=hash_length)}_{suffix}'  # noqa: E501,LN001  # pylint: disable=line-too-long
    )
    max_name_length = 30
    if len(name) > max_name_length:
        raise ValueError(  # noqa: TRY003
            "Index too long for multiple database support. Is self.suffix "
            "longer than 3 characters?"
        )
    if name[0] == '_' or name[0].isdigit():
        name = f'D{name[1:]}'
    return name  # noqa: R504


def create_generic_index_name_old(
    table_name: str,
    column_names: tuple[str, ...] | list[str] | set[str],
    suffix: str = '',
    connection: Any = None,
) -> str:
    """
    Generate a unique name for an index/unique constraint.

    The name is divided into 3 parts: the table name, the column names,
    and a unique digest and suffix.
    """
    # pylint: disable=import-outside-toplevel
    from django.utils.translation import gettext_lazy as _

    # pylint: enable=import-outside-toplevel

    if not isinstance(table_name, str):
        raise TypeError(_("'table_name' must be str"))
    if not isallinstance(column_names, str):
        raise TypeError(_("'column_names' must be a tuple, list or set of str"))
    if not isinstance(suffix, str):
        raise TypeError(_("'suffix' must be str"))

    table_name = table_name.lower()
    __, table_name = split_identifier(table_name)
    hash_suffix_part: str = f'{names_digest(table_name, *column_names, length=8)}_{suffix}'
    if connection is None:
        connection = DEFAULT_DB_ALIAS
    if isinstance(connection, str):
        connection = connections[connection]
    max_length: Any | Literal[200] = connection.ops.max_name_length() or 200
    # If everything fits into max_length, use that name.
    index_name: str = f'{table_name}_{'_'.join(column_names)}_{hash_suffix_part}'
    if len(index_name) <= max_length:
        return index_name
    # Shorten a long suffix.
    if len(hash_suffix_part) > max_length / 3:
        hash_suffix_part = hash_suffix_part[: max_length // 3]
    other_length = (max_length - len(hash_suffix_part)) // 2 - 1
    index_name = (
        f'{table_name[:other_length]}_{'_'.join(column_names)[:other_length]}_{hash_suffix_part}'
    )
    # Prepend D if needed to prevent the name from starting with an
    # underscore or a number (not permitted on Oracle).
    if index_name[0] == '_' or index_name[0].isdigit():
        index_name = f'D{index_name[:-1]}'
    return index_name  # noqa: R504


def create_index_name(
    table_name: str,
    column_names: tuple[str, ...] | list[str] | set[str],
) -> str:
    return create_generic_index_name(
        table_name=table_name,
        fields=column_names,
        suffix='idx',
    )


def create_unique_constraint_name(
    table_name: str,
    column_names: tuple[str, ...] | list[str] | set[str],
) -> str:
    return create_generic_index_name(
        table_name=table_name,
        fields=column_names,
        suffix='uniq',
    )
