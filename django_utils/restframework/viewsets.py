from typing import TYPE_CHECKING

from rest_framework.viewsets import GenericViewSet as _GenericViewSet

from django_utils.restframework.mixins import ResponseSerializerMixin

if TYPE_CHECKING:
    from typing import Any, Literal, Self

    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser
    from django.db.models import BaseManager
    from django.db.models.query import QuerySet
    from rest_framework.pagination import BasePagination
    from rest_framework.serializers import Serializer


class GenericViewSet(  # pyright: ignore[reportIncompatibleMethodOverride]
    ResponseSerializerMixin, _GenericViewSet
):
    serializer_classes: dict[
        "Literal['create', 'retrieve', 'update', 'partial_update', 'destroy', 'list']",
        type['Serializer'],
    ] = {}
    querysets: dict[
        "Literal['create', 'retrieve', 'update', 'partial_update', 'destroy', 'list']",
        'QuerySet[Any] | BaseManager[Any]',
    ] = {}

    @property
    def paginator(self: 'Self') -> 'None | BasePagination':
        if not hasattr(self, '_paginator'):
            paginator: None | BasePagination = None
            if self.pagination_class is None:
                paginator = None
            else:
                paginator = self.pagination_class()  # pyright: ignore[reportCallIssue]
                pagination_options: dict[str, Any] = getattr(self, 'pagination_options', {})
                for key, value in pagination_options.items():
                    setattr(paginator, key, value)
            # pylint: disable=attribute-defined-outside-init
            self._paginator: None | BasePagination = paginator
            # pylint: enable=attribute-defined-outside-init
        return self._paginator

    def get_action_from_request(
        self: 'Self',
    ) -> "Literal['create', 'retrieve', 'update', 'partial_update', 'destroy', 'list']":
        if self.request is not None and self.request.method is not None:
            return self.action_map.get(  # pyright: ignore[reportAttributeAccessIssue]
                self.request.method.lower()
            )
        return self.action  # pyright: ignore[reportReturnType]

    def get_serializer_class(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self',
    ) -> type['Serializer']:
        action: Literal['create', 'retrieve', 'update', 'partial_update', 'destroy', 'list'] = (
            self.get_action_from_request()
        )
        if action == 'partial_update' and 'partial_update' not in self.serializer_classes:
            action = 'update'
        serializer_class: type[Serializer] | None = self.serializer_classes.get(action)
        if serializer_class is None:
            serializer_class = super().get_serializer_class()
        return serializer_class  # noqa: R504

    def get_queryset(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self',
    ) -> 'QuerySet[Any] | BaseManager[Any]':
        action: str = self.get_action_from_request()
        if action == 'partial_update' and 'partial_update' not in self.querysets:
            action = 'update'
        queryset: 'QuerySet[Any] | BaseManager[Any] | None' = self.querysets.get(action)
        if queryset is None:
            queryset = super().get_queryset()
        if self.action == 'list' and getattr(self, 'filter_list_by_owner', True):
            owner_field: str | None = getattr(self, 'owner_field', None)
            if owner_field is not None:
                request_user: 'AbstractBaseUser | AnonymousUser | None' = self.request.user
                if owner_field == 'self':
                    owner_field = 'pk'
                    request_user = request_user.pk
                elif '__' in owner_field:
                    select_related: str = '__'.join(owner_field.split('__')[:-1])
                    queryset = queryset.select_related(select_related)
                queryset = queryset.filter(**{owner_field: request_user})
        return queryset  # noqa: R504

    def get_permissions(self: 'Self') -> list['Any']:
        if isinstance(self.permission_classes, dict):
            action: str = self.get_action_from_request()
            if action == 'partial_update' and 'partial_update' not in self.permission_classes:
                action = 'update'
            permission_classes: list[Any] | None = self.permission_classes.get(
                action, self.permission_classes.get('default', [])
            )
            if (
                self.request
                and self.request.method
                and self.request.method.lower() == 'options'
                and not permission_classes
            ):
                lookup_url_kwarg: str = self.lookup_url_kwarg or self.lookup_field
                kwarg: Any = self.kwargs.get(lookup_url_kwarg)
                if kwarg:
                    methods: list[str] = ['GET', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
                else:
                    methods: list[str] = ['GET', 'POST', 'HEAD', 'OPTIONS']
                for method in methods:
                    if (
                        method in self.allowed_methods
                        and method.lower()
                        in self.action_map  # pyright: ignore[reportAttributeAccessIssue]
                    ):
                        action = self.action_map.get(  # pyright: ignore[reportAttributeAccessIssue]
                            method.lower()
                        )
                        if action in self.permission_classes:
                            permission_classes = self.permission_classes.get(action)
                            break
        else:
            permission_classes = self.permission_classes
        if permission_classes:
            return [permission() for permission in permission_classes]
        return []
