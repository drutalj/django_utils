from django.db import models
from django.utils.translation import gettext_lazy as _

from django_utils.django.db.models import UUIDIDMixin

try:
    from taggit.models import (
        GenericTaggedItemBase as _GenericTaggedItemBase,  # pyright: ignore[reportMissingImports]
    )
    from taggit.models import (  # noqa: E501  # pyright: ignore[reportMissingImports]
        GenericUUIDTaggedItemBase as _GenericUUIDTaggedItemBase,
    )
    from taggit.models import TagBase as _TagBase  # pyright: ignore[reportMissingImports]
    from taggit.models import (
        TaggedItemBase as _TaggedItemBase,  # pyright: ignore[reportMissingImports]
    )

    class TagBase(UUIDIDMixin, _TagBase):
        class Meta(UUIDIDMixin.Meta, _TagBase.Meta):
            abstract = True

    class HashtagBase(TagBase):
        count = models.BigIntegerField(
            null=False,
            blank=True,
            default=0,
            editable=False,
            verbose_name=_("count"),
            db_index=True,
        )
        last_used = models.DateTimeField(
            null=True,
            blank=True,
            default=None,
            editable=False,
            verbose_name=_("last used"),
            db_index=True,
        )

        class Meta(TagBase.Meta):
            abstract = True

    class TaggedItemBase(UUIDIDMixin, _TaggedItemBase):
        class Meta(UUIDIDMixin.Meta, _TaggedItemBase.Meta):
            abstract = True

    class HashtaggedItemBase(TaggedItemBase):
        created_at = models.DateTimeField(
            null=False,
            blank=True,
            auto_now_add=True,
            editable=False,
            verbose_name=_("created at"),
            db_index=True,
        )

        class Meta(TaggedItemBase.Meta):
            abstract = True
            indexes: list[models.Index] = [
                models.Index(
                    fields=(
                        'tag',
                        'created_at',
                    ),
                ),
            ]

    class GenericTaggedItemBase(UUIDIDMixin, _GenericTaggedItemBase):
        class Meta(UUIDIDMixin.Meta, _GenericTaggedItemBase.Meta):
            abstract = True

    class GenericUUIDTaggedItemBase(UUIDIDMixin, _GenericUUIDTaggedItemBase):
        class Meta(UUIDIDMixin.Meta, _GenericUUIDTaggedItemBase.Meta):
            abstract = True

except ImportError:
    pass
