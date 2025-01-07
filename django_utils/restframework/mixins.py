from types import NoneType
from typing import TYPE_CHECKING

from django.db.models import Model
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin as _CreateModelMixin
from rest_framework.mixins import UpdateModelMixin as _UpdateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer, Serializer

from .serializers import ModelSerializer

if TYPE_CHECKING:
    from typing import Any, Self


class ResponseSerializerMixin(GenericAPIView):
    def get_response_object(self: 'Self', obj: 'Model') -> 'Model':
        if not isinstance(obj, Model):
            raise TypeError(_("'obj' must be instance of Model"))

        _is_response: bool = getattr(self, '_is_response', False)
        self.is_response = True
        ret: Model = self.get_object(obj)
        self._is_response: bool = _is_response
        return ret

    def get_object(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', obj: 'Model | None' = None  # pyright: ignore[reportRedeclaration]
    ) -> 'Model':
        if not isinstance(obj, (Model, NoneType)):
            raise TypeError(_("'obj' must be instance of Model or None"))

        if obj is None:
            ret: Model = super().get_object()
        else:
            ret: Model = obj
            if getattr(self, '_is_response', False):
                ret = self.get_object_by_pk(pk=ret.pk)

        return ret  # noqa: R504

    def get_object_by_pk(
        self: 'Self', pk: 'Any' = None, queryset: 'QuerySet | BaseManager | None' = None
    ) -> 'Model':
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        if not isinstance(queryset, (QuerySet, BaseManager, NoneType)):
            raise TypeError(_("'queryset' must be instance of QuerySet, BaseManager or None"))

        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.filter_queryset(queryset)

        if pk is None:
            # Perform the lookup filtering.
            lookup_url_kwarg: str = self.lookup_url_kwarg or self.lookup_field

            assert lookup_url_kwarg in self.kwargs, (  # noqa: S101
                f"Expected view {self.__class__.__name__} to be called with a URL keyword argument "
                "named \"{lookup_url_kwarg}\". Fix your URL conf, or set the `.lookup_field` "
                "attribute on the view correctly."
            )

            filter_kwargs: dict[str, Any] = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        else:
            filter_kwargs: dict[str, Any] = {self.lookup_field: pk}

        obj: 'Model' = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        if not getattr(self, '_is_response', False):
            self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer_class(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self',
    ) -> type['Serializer']:
        serializer_class: type[Serializer] | None = None
        if getattr(self, '_is_response', False) and hasattr(self, 'serializer_classes'):
            serializer_class = (
                self.serializer_classes.get(  # pyright: ignore[reportAttributeAccessIssue]
                    'retrieve'
                )
            )
        if serializer_class is None:
            serializer_class = super().get_serializer_class()
        return serializer_class  # noqa: R504  # pyright: ignore[reportReturnType]

    def get_queryset(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self',
    ) -> 'QuerySet | BaseManager':
        queryset: QuerySet | BaseManager | None = None
        if getattr(self, '_is_response', False) and hasattr(self, 'querysets'):
            queryset = self.querysets.get('retrieve')  # pyright: ignore[reportAttributeAccessIssue]
        if queryset is None:
            queryset = super().get_queryset()
        return queryset  # noqa: R504  # pyright: ignore[reportReturnType]

    def get_response_serializer(
        self: 'Self',
        instance: 'Model',
        serializer: 'Serializer | ListSerializer',
        get_object: bool = True,
    ) -> 'Serializer | ListSerializer':
        if not isinstance(instance, Model):
            raise TypeError(_("'instance' must be instance of Model"))
        if not isinstance(serializer, (Serializer, ListSerializer)):
            raise TypeError(_("'serializer' must be instance of Serializer or ListSerializer"))
        if not isinstance(get_object, bool):
            raise TypeError(_("'get_object' must be instance of bool"))

        _is_response: bool = getattr(self, '_is_response', False)
        self._is_response = True
        response_serializer_class: type['Serializer'] = self.get_serializer_class()
        self._is_response = _is_response
        if response_serializer_class and (
            response_serializer_class != serializer.__class__
            or issubclass(response_serializer_class, ModelSerializer)
        ):
            response_serializer_kwargs: dict[str, 'Any'] = {}
            response_serializer_kwargs.setdefault('context', self.get_serializer_context())
            if issubclass(response_serializer_class, ModelSerializer):
                response_serializer_kwargs.setdefault('is_response', True)

            if get_object is True:
                instance = self.get_response_object(obj=instance)

            return response_serializer_class(instance, **response_serializer_kwargs)
        return serializer


class CreateModelMixin(ResponseSerializerMixin, _CreateModelMixin):
    def create(
        self: 'Self', request: 'Request', *args: 'Any', **kwargs: 'Any'  # noqa: U100
    ) -> Response:
        if not isinstance(request, Request):
            raise TypeError(_("'request' must be instance of Request"))

        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: 'Model' = self.perform_create(serializer)
        headers: dict[str, str] = self.get_success_headers(serializer.data)

        response_serializer: Serializer | ListSerializer = self.get_response_serializer(
            instance, serializer
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', serializer: 'Serializer'
    ) -> 'Model':
        if not isinstance(serializer, Serializer):
            raise TypeError(_("'serializer' must be instance of Serializer"))

        return serializer.save()


class UpdateModelMixin(ResponseSerializerMixin, _UpdateModelMixin):
    def update(
        self: 'Self', request: 'Request', *args: 'Any', **kwargs: 'Any'  # noqa: U100
    ) -> Response:
        if not isinstance(request, Request):
            raise TypeError(_("'request' must be instance of Request"))

        partial: bool = kwargs.pop('partial', False)
        instance: 'Model' = self.get_object()
        serializer: 'Serializer' = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        response_instance: 'Model' = self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = (  # noqa: E501  # pylint: disable=protected-access  # pyright: ignore[reportAttributeAccessIssue]
                {}
            )

        response_serializer: Serializer | ListSerializer = self.get_response_serializer(
            response_instance, serializer
        )

        return Response(response_serializer.data)

    def perform_update(  # pyright: ignore[reportIncompatibleMethodOverride]
        self: 'Self', serializer: 'Serializer'
    ) -> 'Model':
        if not isinstance(serializer, Serializer):
            raise TypeError(_("'serializer' must be instance of Serializer"))

        return serializer.save()
