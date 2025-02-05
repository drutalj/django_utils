import mimetypes
import re
from contextlib import suppress
from enum import Enum
from types import NoneType
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from django_utils.helpers import isallinstance

if TYPE_CHECKING:
    from typing import Any, Self


@deconstructible
class FileMinSizeValidator:
    message: str = _(
        "Ensure this file size is equal or greater than %(min_size)s. Your file size is %(size)s."
    )
    code: str = 'min_size'

    def __init__(
        self: 'Self',
        min_size: int = 0,
        message: str | None = None,
        code: str | None = None,
    ) -> None:
        if not isinstance(min_size, int):
            raise TypeError(_("'min_size' must be int"))
        if not isinstance(message, (str, NoneType)):
            raise TypeError(_("'message' must be None or str"))
        if not isinstance(code, (str, NoneType)):
            raise TypeError(_("'code' must be None or str"))

        self.min_size: int = min_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self: 'Self', value: 'File') -> None:
        if not isinstance(value, File):
            raise TypeError(_("'value' must be instance of File"))

        if self.min_size > 0 and value.size < self.min_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    'min_size': filesizeformat(self.min_size),
                    'size': filesizeformat(value.size),
                    'value': value,
                },
            )

    def __eq__(self: 'Self', other: 'Any') -> bool:
        return (
            isinstance(other, self.__class__)
            and self.min_size == other.min_size
            and self.message == other.message
            and self.code == other.code
        )


@deconstructible
class FileMaxSizeValidator:
    message: str = _(
        "Ensure this file size is not greater than %(max_size)s. Your file size is %(size)s."
    )
    code: str = 'max_size'

    def __init__(
        self: 'Self',
        max_size: int | None = None,
        message: str | None = None,
        code: str | None = None,
    ) -> None:
        if not isinstance(max_size, (int, NoneType)):
            raise TypeError(_("'max_size' must be None or int"))
        if not isinstance(message, (str, NoneType)):
            raise TypeError(_("'message' must be None or str"))
        if not isinstance(code, (str, NoneType)):
            raise TypeError(_("'code' must be None or str"))

        self.max_size: int | None = max_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self: 'Self', value: 'File') -> None:
        if not isinstance(value, File):
            raise TypeError(_("'value' must be instance of File"))

        if self.max_size is not None and value.size > self.max_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    'max_size': filesizeformat(self.max_size),
                    'size': filesizeformat(value.size),
                    'value': value,
                },
            )

    def __eq__(self: 'Self', other: 'Any') -> bool:
        return (
            isinstance(other, self.__class__)
            and self.max_size == other.max_size
            and self.message == other.message
            and self.code == other.code
        )


try:
    import filetype  # pyright: ignore[reportMissingImports]

    class FileType(Enum):
        ARCHIVE = 'archive'
        AUDIO = 'audio'
        FONT = 'font'
        IMAGE = 'image'
        VIDEO = 'video'
        DOCUMENT = 'document'

    @deconstructible
    class FileTypeValidator:
        message: str = _("Files of type %(file_type)s are not supported.")
        code: str = 'file_type'

        def __init__(
            self: 'Self',
            file_types: tuple[FileType, ...] | list[FileType] | set[FileType] | None = None,
            message: str | None = None,
            code: str | None = None,
        ) -> None:
            if not isallinstance(file_types, FileType, NoneType):
                raise TypeError(
                    _("'file_types' must be None or tuple, list or set of instances of FileType")
                )
            if not isinstance(message, (str, NoneType)):
                raise TypeError(_("'message' must be None or str"))
            if not isinstance(code, (str, NoneType)):
                raise TypeError(_("'code' must be None or str"))

            self.file_types: tuple[FileType, ...] | list[FileType] | set[FileType] | None = (
                file_types
            )
            if message is not None:
                self.message = message
            if code is not None:
                self.code = code

        def __call__(self: 'Self', value: 'File') -> None:
            if not isinstance(value, File):
                raise TypeError(_("'value' must be instance of File"))

            if self.file_types is not None:
                file_type = None
                if filetype.helpers.is_archive(value.file) is True:
                    file_type = FileType.ARCHIVE
                elif filetype.helpers.is_audio(value.file) is True:
                    file_type = FileType.AUDIO
                elif filetype.helpers.is_font(value.file) is True:
                    file_type = FileType.FONT
                elif filetype.helpers.is_image(value.file) is True:
                    file_type = FileType.IMAGE
                elif filetype.helpers.is_video(value.file) is True:
                    file_type = FileType.VIDEO
                elif filetype.helpers.is_document(value.file) is True:
                    file_type = FileType.DOCUMENT

                if file_type not in self.file_types:
                    raise ValidationError(
                        self.message,
                        code=self.code,
                        params={
                            'file_type': file_type,
                            'value': value,
                        },
                    )

        def __eq__(self: 'Self', other: 'Any') -> bool:
            return (
                isinstance(other, self.__class__)
                and self.file_types == other.file_types
                and self.message == other.message
                and self.code == other.code
            )

except ImportError:
    pass


@deconstructible
class FileContentTypeValidator:
    message: str = _("Files of type %(content_type)s are not supported.")
    code: str = "content_type"

    def __init__(
        self: 'Self',
        content_types: tuple[str, ...] | list[str] | set[str] | None = None,
        message: str | None = None,
        code: str | None = None,
    ) -> None:
        if not isallinstance(content_types, str, NoneType):
            raise TypeError(_("'content_types' must be None or tuple, list or set of str"))
        if not isinstance(message, (str, NoneType)):
            raise TypeError(_("'message' must be None or str"))
        if not isinstance(code, (str, NoneType)):
            raise TypeError(_("'code' must be None or str"))

        self.content_types: tuple[str, ...] | list[str] | set[str] | None = content_types
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self: 'Self', value: 'UploadedFile') -> None:
        if not isinstance(value, UploadedFile):
            raise TypeError(_("'value' must be instance of UploadedFile"))

        if self.content_types is not None:
            content_type: str | None = value.content_type
            if content_type is None:
                try:
                    content_type_tuple: tuple[str | None, str | None] = mimetypes.guess_file_type(
                        value.name
                    )
                except AttributeError:
                    content_type_tuple = mimetypes.guess_type(value.name)
                content_type = content_type_tuple[0]
            if content_type is None:
                with suppress(NameError):
                    content_type = (
                        filetype.guess_mime(  # pyright: ignore[reportPossiblyUnboundVariable]
                            value.file
                        )
                    )

            if content_type is None or not any(
                re.fullmatch(pattern, content_type) for pattern in self.content_types
            ):
                raise ValidationError(
                    self.message,
                    code=self.code,
                    params={
                        'content_type': content_type,
                        'value': value,
                    },
                )

    def __eq__(self: 'Self', other: 'Any') -> bool:
        return (
            isinstance(other, self.__class__)
            and self.content_types == other.content_types
            and self.message == other.message
            and self.code == other.code
        )


try:
    from PIL import Image  # pyright: ignore[reportMissingImports]

    if TYPE_CHECKING:
        from PIL.Image import Image as ImageFile

    @deconstructible
    class ImageMinSizeValidator:
        message: str = _(
            "Ensure this image size is equal or greater than %(min_width)spx x%(min_height)spx. Your file size is %(width)spx x %(height)spx."  # noqa: E501  # pylint: disable=line-too-long
        )
        code: str = 'min_size'

        def __init__(
            self: 'Self',
            min_width: int = 0,
            min_height: int = 0,
            message: str | None = None,
            code: str | None = None,
        ) -> None:
            if not isinstance(min_width, int):
                raise TypeError(_("'min_width' must be int"))
            if not isinstance(min_height, int):
                raise TypeError(_("'min_height' must be int"))
            if not isinstance(message, (str, NoneType)):
                raise TypeError(_("'message' must be None or str"))
            if not isinstance(code, (str, NoneType)):
                raise TypeError(_("'code' must be None or str"))

            self.min_width: int = min_width
            self.min_height: int = min_height
            if message is not None:
                self.message = message
            if code is not None:
                self.code = code

        def __call__(self: 'Self', value: 'File') -> None:
            if not isinstance(value, File):
                raise TypeError(_("'value' must be instance of File"))

            if self.min_width > 0 or self.min_height > 0:
                image: ImageFile = Image.open(value.file)
                if (self.min_width > 0 and image.width < self.min_width) or (
                    self.min_height > 0 and image.height < self.min_height
                ):
                    raise ValidationError(
                        self.message,
                        code=self.code,
                        params={
                            'min_width': self.min_width,
                            'min_height': self.min_height,
                            'width': image.width,
                            'height': image.height,
                            'value': value,
                        },
                    )

        def __eq__(self: 'Self', other: 'Any') -> bool:
            return (
                isinstance(other, self.__class__)
                and self.min_width == other.min_width
                and self.min_height == other.min_height
                and self.message == other.message
                and self.code == other.code
            )

    @deconstructible
    class ImageMaxSizeValidator:
        message: str = _(
            "Ensure this image size is not greater than %(max_width)spx x%(max_height)spx. Your file size is %(width)spx x %(height)spx."  # noqa: E501  # pylint: disable=line-too-long
        )
        code: str = 'max_size'

        def __init__(
            self: 'Self',
            max_width: int | None = None,
            max_height: int | None = None,
            message: str | None = None,
            code: str | None = None,
        ) -> None:
            if not isinstance(max_width, (int, NoneType)):
                raise TypeError(_("'max_width' must be None or int"))
            if not isinstance(max_height, (int, NoneType)):
                raise TypeError(_("'max_height' must be None or int"))
            if not isinstance(message, (str, NoneType)):
                raise TypeError(_("'message' must be None or str"))
            if not isinstance(code, (str, NoneType)):
                raise TypeError(_("'code' must be None or str"))

            self.max_width: int | None = max_width
            self.max_height: int | None = max_height
            if message is not None:
                self.message = message
            if code is not None:
                self.code = code

        def __call__(self: 'Self', value: 'File') -> None:
            if not isinstance(value, File):
                raise TypeError(_("'value' must be instance of File"))

            if self.max_width is not None or self.max_height is not None:
                image: ImageFile = Image.open(value.file)
                if (self.max_width is not None and image.width > self.max_width) or (
                    self.max_height is not None and image.height > self.max_height
                ):
                    raise ValidationError(
                        self.message,
                        code=self.code,
                        params={
                            'max_width': (
                                self.max_width if self.max_width is not None else _("unlimited")
                            ),
                            'max_height': (
                                self.max_height if self.max_height is not None else _("unlimited")
                            ),
                            'width': image.width,
                            'height': image.height,
                            'value': value,
                        },
                    )

        def __eq__(self: 'Self', other: 'Any') -> bool:
            return (
                isinstance(other, self.__class__)
                and self.max_width == other.max_width
                and self.max_height == other.max_height
                and self.message == other.message
                and self.code == other.code
            )

except ImportError:
    pass
