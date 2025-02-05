from django.db import models
from django.utils.translation import gettext_lazy as _

from django_utils.django.db.models import fields

__all__: list[str] = [
    'UUIDIDMixin',
]


class UUIDIDMixin(models.Model):
    class Meta:
        abstract = True

    id = fields.AutoUUID4Field(  # noqa: A003,VNE003
        primary_key=True,
        verbose_name=_("id"),
    )
