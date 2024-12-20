import uuid
from typing import TYPE_CHECKING

from django.db.models.fields import UUIDField

if TYPE_CHECKING:
    from typing import Any, Self

__all__: list[str] = [
    'AutoUUID4Field',
]


class AutoUUID4Field(UUIDField):
    def __init__(self: 'Self', verbose_name: str | None = None, **kwargs: 'Any') -> None:
        kwargs['default'] = uuid.uuid4
        super().__init__(verbose_name=verbose_name, **kwargs)
