from typing import TYPE_CHECKING

from drf_spectacular.openapi import AutoSchema as _AutoSchema

if TYPE_CHECKING:
    from typing import Self

    from drf_spectacular.utils import _SerializerType


class AutoSchema(_AutoSchema):
    def get_response_serializers(self: 'Self') -> '_SerializerType | None':
        """override this for custom behaviour"""
        _is_response: bool = getattr(self.view, '_is_response', False)
        self.view._is_response = True  # pylint: disable=protected-access
        serializer: '_SerializerType | None' = self._get_serializer()
        self.view._is_response = _is_response  # pylint: disable=protected-access
        return serializer  # noqa: R504
