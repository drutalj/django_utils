from typing import TYPE_CHECKING

from django.apps import AppConfig

if TYPE_CHECKING:
    from typing import Self


class DjuTaggitConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_utils.dju_taggit_core'

    def ready(self: 'Self') -> None:
        from django_utils.dju_taggit_core import (  # noqa: F401,E501  # pylint: disable=import-outside-toplevel,unused-import
            signals,
        )
