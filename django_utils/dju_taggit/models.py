from django.db import models
from django.utils.translation import gettext_lazy as _

from django_utils.django.db.models.helpers import create_unique_constraint_name

try:
    from django_utils.dju_taggit_core.models import (  # pyright: ignore[reportMissingImports]
        GenericUUIDTaggedItemBase,
        HashtagBase,
    )
    from django_utils.dju_taggit_core.models import (
        HashtaggedItemBase as _HashtaggedItemBase,  # pyright: ignore[reportMissingImports]
    )
    from django_utils.dju_taggit_core.models import (
        TaggedItemBase as _TaggedItemBase,  # pyright: ignore[reportMissingImports]
    )

    class Hashtag(HashtagBase):
        class Meta(HashtagBase.Meta):
            verbose_name: str = _("hashtag")
            verbose_name_plural: str = _("hashtags")

    class TaggedItemBase(_TaggedItemBase):
        tag = models.ForeignKey(
            Hashtag, related_name='%(app_label)s_%(class)s_items', on_delete=models.CASCADE
        )

        class Meta(_TaggedItemBase.Meta):
            abstract = True

    class HashtaggedItemBase(
        TaggedItemBase, _HashtaggedItemBase
    ):  # pylint: disable=too-many-ancestors
        class Meta(TaggedItemBase.Meta, _HashtaggedItemBase.Meta):
            abstract = True

    class TaggedItem(
        GenericUUIDTaggedItemBase, TaggedItemBase
    ):  # pylint: disable=too-many-ancestors
        class Meta(GenericUUIDTaggedItemBase.Meta, TaggedItemBase.Meta):
            verbose_name: str = _("tagged item")
            verbose_name_plural: str = _("tagged items")
            indexes: list[models.Index] = [
                models.Index(
                    fields=(
                        'content_type',
                        'object_id',
                    ),
                )
            ]
            constraints: list[models.UniqueConstraint] = [
                models.UniqueConstraint(
                    fields=(
                        'content_type',
                        'object_id',
                        'tag',
                    ),
                    name=create_unique_constraint_name(
                        table_name='dju_taggit_taggeditem',
                        column_names=(
                            'content_type',
                            'object_id',
                            'tag',
                        ),
                    ),
                )
            ]

    class HashtaggedItem(
        GenericUUIDTaggedItemBase, HashtaggedItemBase
    ):  # pylint: disable=too-many-ancestors
        class Meta(
            GenericUUIDTaggedItemBase.Meta, HashtaggedItemBase.Meta
        ):  # pylint: disable=too-many-ancestors
            verbose_name: str = _("hashtagged item")
            verbose_name_plural: str = _("hashtagged items")
            indexes: list[models.Index] = HashtaggedItemBase.Meta.indexes + [
                models.Index(
                    fields=(
                        'content_type',
                        'object_id',
                    ),
                ),
            ]
            constraints: list[models.UniqueConstraint] = [
                models.UniqueConstraint(
                    fields=(
                        'content_type',
                        'object_id',
                        'tag',
                    ),
                    name=create_unique_constraint_name(
                        table_name='dju_taggit_hashtaggeditem',
                        column_names=(
                            'content_type',
                            'object_id',
                            'tag',
                        ),
                    ),
                )
            ]

except ImportError:
    pass
