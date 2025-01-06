from types import NoneType
from typing import TYPE_CHECKING

from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer as _ModelSerializer

from django_utils.helpers import isdict

if TYPE_CHECKING:
    from typing import Any, Literal, Self

    from rest_framework.request import Request


class ModelSerializer(_ModelSerializer):
    def __init__(  # pylint: disable=too-many-branches
        self: 'Self',
        instance: 'Model | None' = None,
        data: dict[str, 'Any'] | type[empty] = empty,
        **kwargs: 'Any',
    ) -> None:
        if not isinstance(instance, (Model, NoneType)):
            raise TypeError(_("'instance' must be instance of Model or None"))
        if not isinstance(data, (dict, empty)):
            raise TypeError(_("'data' must be a dict or empty"))
        if isinstance(data, dict) and not isdict(data, str):
            raise TypeError(_("'data' must be a dict with string keys"))

        self._is_response: bool = kwargs.pop('is_response', False)
        super().__init__(
            instance=instance,
            data=data,  # pyright: ignore[reportArgumentType]
            **kwargs,
        )
        request: Request | None = self.context.get('request')
        if request:
            allowed_fields_dict: dict[
                Literal['create', 'retrieve', 'update', 'partial_update', 'list'],
                tuple[str, ...] | list[str] | set[str],
            ] = getattr(
                self.Meta,  # noqa: E501  # pylint: disable=no-member  # pyright: ignore[reportAttributeAccessIssue]
                'allowed_fields',
                {},
            )
            allowed_fields = None
            if request.method == 'GET' or self._is_response:
                if self.instance is not None:
                    allowed_fields: tuple[str, ...] | list[str] | set[str] | None = (
                        allowed_fields_dict.get('retrieve')
                    )
                else:
                    allowed_fields: tuple[str, ...] | list[str] | set[str] | None = (
                        allowed_fields_dict.get('list')
                    )
            elif request.method == 'POST':
                allowed_fields: tuple[str, ...] | list[str] | set[str] | None = (
                    allowed_fields_dict.get('create')
                )
            elif request.method == 'PUT':
                allowed_fields: tuple[str, ...] | list[str] | set[str] | None = (
                    allowed_fields_dict.get('update')
                )
            elif request.method == 'PATCH':
                allowed_fields: tuple[str, ...] | list[str] | set[str] | None = (
                    allowed_fields_dict.get('partial_update', allowed_fields_dict.get('update'))
                )
            if allowed_fields is not None:
                for field_name in list(self.fields):
                    if field_name not in allowed_fields:
                        self.fields.pop(field_name)
