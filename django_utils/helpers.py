from types import NoneType
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from typing import Any


def isallinstance(
    obj_or_sequence_or_set: 'Any',
    type_or_tuple: type['Any'] | tuple[type['Any'], ...],
    type_or_tuple_if_obj: type['Any'] | tuple[type['Any'], ...] | None = None,
) -> bool:
    if not isinstance(type_or_tuple, (type, tuple)) or (
        isinstance(type_or_tuple, tuple)
        and not all(isinstance(item, type) for item in type_or_tuple)
    ):
        raise TypeError(_("'type_or_tuple' must be a type or tuple of types"))
    if not isinstance(type_or_tuple_if_obj, (type, tuple, NoneType)) or (
        isinstance(type_or_tuple_if_obj, tuple)
        and not all(isinstance(item, type) for item in type_or_tuple_if_obj)
    ):
        raise TypeError(_("'type_or_tuple_if_obj' must be None or type or tuple of types"))

    if not isinstance(obj_or_sequence_or_set, (tuple, list, set)):
        if type_or_tuple_if_obj is not None:
            return isinstance(obj_or_sequence_or_set, type_or_tuple_if_obj)
        return False

    return all(isinstance(item, type_or_tuple) for item in obj_or_sequence_or_set)


def isdict(
    value: 'Any',
    type_or_tuple_key: type['Any'] | tuple[type['Any'], ...],
    type_or_tuple_value: type['Any'] | tuple[type['Any'], ...] = object,
) -> bool:
    if not isinstance(type_or_tuple_key, (type, tuple)) or (
        isinstance(type_or_tuple_key, tuple)
        and not all(isinstance(item, type) for item in type_or_tuple_key)
    ):
        raise TypeError(_("'type_or_tuple_key' must be a type or tuple of types"))
    if not isinstance(type_or_tuple_value, (type, tuple)) or (
        isinstance(type_or_tuple_value, tuple)
        and not all(isinstance(item, type) for item in type_or_tuple_value)
    ):
        raise TypeError(_("'type_or_tuple' must be a type or tuple of types"))

    if not isinstance(value, dict):
        return False

    if not isallinstance(list(value.keys()), type_or_tuple_key):
        return False

    if not isallinstance(list(value.values()), type_or_tuple_value):
        return False

    return True


def getattr_nested(
    obj: 'Any', attr_path: str, last_item_suffix: str = '', default: 'Any' = None
) -> 'Any':
    try:
        attr_path += last_item_suffix
        for attr in attr_path.split('__'):
            obj = getattr(obj, attr)
        return obj
    except AttributeError:
        return default
