try:
    from typing import TYPE_CHECKING

    from django.conf import settings
    from django.db.models.fields.reverse_related import ManyToOneRel
    from django.db.models.signals import post_delete, post_save
    from django.dispatch import receiver
    from taggit.models import TagBase, TaggedItemBase  # pyright: ignore[reportMissingImports]

    from django_utils.dju_taggit.models import (  # pyright: ignore[reportMissingImports]
        HashtagBase,
        HashtaggedItemBase,
    )

    if TYPE_CHECKING:
        from datetime import datetime
        from typing import Any

        from django.db import models

    @receiver(post_save, dispatch_uid='post_save_hashtagged_item')
    def post_save_hashtagged_item(
        sender: 'type[models.Model]',  # pylint: disable=unused-argument
        instance: 'models.Model',
        created: bool,
        **kwargs: 'Any',
    ) -> None:
        if isinstance(instance, HashtaggedItemBase) and created is True:
            hashtag: 'TagBase' = instance.tag
            if isinstance(hashtag, HashtagBase):
                hashtag.count += 1
                if hashtag.last_used is None or instance.created_at > hashtag.last_used:
                    hashtag.last_used = instance.created_at
                hashtag.save()

    @receiver(post_delete, dispatch_uid='post_delete_tagged_item')
    def post_delete_hashtagged_item(
        sender: 'type[models.Model]',  # pylint: disable=unused-argument
        instance: 'models.Model',
        **kwargs: 'Any',
    ) -> None:
        if isinstance(instance, TaggedItemBase):  # pylint: disable=too-many-nested-blocks
            tag: 'TagBase' = instance.tag
            tag_is_used: bool = False
            if isinstance(tag, TagBase):
                for field in tag.__class__._meta.get_fields():
                    if isinstance(field, ManyToOneRel):
                        tag_is_used = field.field.model.objects.filter(
                            **{field.field.name: tag},
                        ).exists()
                        if tag_is_used is True:
                            break

            if tag_is_used is False and getattr(
                settings, 'DJANGO_UTILS_TAGGIT_AUTO_REMOVE_UNUSED_TAGS', False
            ):
                tag.delete()

            if (
                tag_is_used is True
                and isinstance(instance, HashtaggedItemBase)
                and isinstance(tag, HashtagBase)
            ):
                last_used: 'datetime | None' = None
                for field in tag.__class__._meta.get_fields():
                    if isinstance(field, ManyToOneRel):
                        related_model = field.field.model
                        if issubclass(related_model, HashtaggedItemBase):
                            latest_hashtagged_item: HashtaggedItemBase | None = (
                                related_model.objects.filter(tag=tag)
                                .order_by('-created_at')
                                .first()
                            )
                            if latest_hashtagged_item is not None and (
                                last_used is None or latest_hashtagged_item.created_at > last_used
                            ):
                                last_used = latest_hashtagged_item.created_at
                tag.count -= 1
                tag.last_used = last_used
                tag.save()

except ImportError:
    pass
