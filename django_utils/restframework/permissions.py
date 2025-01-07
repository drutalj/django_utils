from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated as _IsAuthenticated

from django_utils.helpers import get_nested_attr

if TYPE_CHECKING:
    from typing import Self

    from django.db.models import Model
    from rest_framework.request import Request
    from rest_framework.views import APIView


class IsAuthenticated(_IsAuthenticated):
    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', request: 'Request', view: 'APIView', obj: 'Model'  # noqa: U100
    ) -> bool:
        return self.has_permission(request, view)


class IsActive(BasePermission):
    def has_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', request: 'Request', view: 'APIView'  # noqa: U100
    ) -> bool:
        return bool(request.user and request.user.is_active)

    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', request: 'Request', view: 'APIView', obj: 'Model'  # noqa: U100
    ) -> bool:
        return self.has_permission(request, view)


class IsOwner(BasePermission):
    def has_object_permission(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', request: 'Request', view: 'APIView', obj: 'Model'
    ) -> bool:
        owner_field: str = getattr(view, 'owner_field', 'user')
        field_name: str = 'pk' if owner_field == 'self' else owner_field + '_id'
        return bool(
            self.has_permission(request, view)
            and request.user
            and get_nested_attr(obj, field_name) == request.user.pk
        )
