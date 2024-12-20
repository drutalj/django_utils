from django.db import models
from django.utils.translation import gettext_lazy as _

from . import fields

__all__: list[str] = [
    'UUIDIDMixin',
]


class UUIDIDMixin(models.Model):
    id = fields.AutoUUID4Field(  # noqa: A003
        primary_key=True,
        verbose_name=_("id"),
    )

    class Meta:
        abstract = True
