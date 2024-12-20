from typing import TYPE_CHECKING

from django.apps import AppConfig

if TYPE_CHECKING:
    from typing import Self


class DjuTaggitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_utils.dju_taggit_core'

    def ready(self: 'Self') -> None:
        from . import signals  # noqa: F401  # pylint: disable=import-outside-toplevel,unused-import
