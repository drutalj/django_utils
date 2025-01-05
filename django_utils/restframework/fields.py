import base64
import io
import mimetypes
import uuid
from types import NoneType
from typing import Any, Self

from django.core import validators as django_core_validators
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import SkipField

from django_utils.django.core import validators
from django_utils.helpers import isallinstance


class FileField(serializers.FileField):
    def __init__(  # noqa: E501,CFQ002  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self: Self,
        allowed_extensions: None | tuple[str, ...] | list[str] | set[str] = None,
        min_size: int = 0,
        max_size: None | int = None,
        content_types: None | tuple[str, ...] | list[str] | set[str] = None,
        file_types: (
            None
            | tuple[validators.FileType, ...]
            | list[validators.FileType]
            | set[validators.FileType]
        ) = None,
        **kwargs: Any,
    ) -> None:
        if not isallinstance(allowed_extensions, str, NoneType):
            raise TypeError(_("'allowed_extensions' must be None or tuple, list or set of str"))
        if not isinstance(min_size, int):
            raise TypeError(_("'min_size' must be int"))
        if not isinstance(max_size, (NoneType, int)):
            raise TypeError(_("'max_size' must be None or int"))
        if not isallinstance(content_types, str, NoneType):
            raise TypeError(_("'content_types' must be None or tuple, list or set of str"))
        if not isallinstance(file_types, validators.FileType, NoneType):
            raise TypeError(
                _("'file_types' must be None or tuple, list or set of instances of FileType"),
            )

        if allowed_extensions is not None:
            self.default_validators.append(
                django_core_validators.FileExtensionValidator(
                    allowed_extensions=allowed_extensions,
                ),
            )
        if min_size > 0:
            self.default_validators.append(validators.FileMinSizeValidator(min_size=min_size))
        if max_size is not None:
            self.default_validators.append(validators.FileMaxSizeValidator(max_size=max_size))
        if content_types is not None:
            self.default_validators.append(
                validators.FileContentTypeValidator(content_types=content_types),
            )
        if file_types is not None:
            self.default_validators.append(validators.FileTypeValidator(file_types=file_types))
        super().__init__(**kwargs)


class ImageField(FileField, serializers.ImageField):
    def __init__(  # noqa: CFQ002
        self: Self,
        allowed_extensions: None | tuple[str, ...] | list[str] | set[str] = None,
        min_size: int = 0,
        max_size: None | int = None,
        min_width: int = 0,
        min_height: int = 0,
        max_width: None | int = None,
        max_height: None | int = None,
        content_types: None | tuple[str, ...] | list[str] | set[str] = None,
        **kwargs: Any,
    ) -> None:
        if not isinstance(min_width, int):
            raise TypeError(_("'min_width' must be int"))
        if not isinstance(min_height, int):
            raise TypeError(_("'min_height' must be int"))
        if not isinstance(max_width, (NoneType, int)):
            raise TypeError(_("'max_width' must be None or int"))
        if not isinstance(max_height, (NoneType, int)):
            raise TypeError(_("'max_height' must be None or int"))

        file_types = [validators.FileType.IMAGE]
        if min_width > 0 or min_height > 0:
            self.default_validators.append(
                validators.ImageMinSizeValidator(min_width=min_width, min_height=min_height)
            )
        if max_width is not None or max_height is not None:
            self.default_validators.append(
                validators.ImageMaxSizeValidator(max_width=max_width, max_height=max_height)
            )
        super().__init__(
            allowed_extensions=allowed_extensions,
            min_size=min_size,
            max_size=max_size,
            content_types=content_types,
            file_types=file_types,
            **kwargs,
        )


class Base64FileField(FileField):
    def to_internal_value(self: Self, data: Any) -> Any:  # pylint: disable=too-many-branches
        filename: str | None = None
        if isinstance(data, dict) and data:
            if not all(key in data for key in ("filename", "data")):
                raise serializers.ValidationError(
                    _("Must be an object containing keys 'filename' and 'data'"),
                )
            filename = data["filename"]
            if not isinstance(filename, str):
                raise serializers.ValidationError(_("Invalid file name"))
            filename = filename.strip()
            if not filename:
                raise serializers.ValidationError(_("Invalid file name"))
            data = data["data"]

        if data in ('', {}, None):
            return None

        if isinstance(data, str):
            header = None
            content_type = None
            if ";base64," in data:
                header, datastr = data.split(';base64,')  # header ~= data:image/X,
                content_type = header.replace('data:', '')
            elif data.startswith('http'):  # noqa: R506
                raise SkipField()
            else:
                datastr = data

            try:
                decoded_data: bytes = base64.b64decode(datastr)
            except (TypeError, ValueError) as exc:
                raise serializers.ValidationError(_("Invalid base64 data")) from exc
            if not filename:
                extension: str = (
                    self._get_extension(content_type=content_type, data=decoded_data) or ''
                )
                extension = f'.{extension}' if extension else ''
                filename = f'{uuid.uuid4()}{extension}'
            if not content_type:
                content_type: str | None = self._get_content_type(
                    filename=filename, data=decoded_data
                )
            if content_type:
                data = SimpleUploadedFile(
                    name=filename,
                    content=decoded_data,
                    content_type=content_type,
                )
            else:
                data = SimpleUploadedFile(
                    name=filename,
                    content=decoded_data,
                )

        elif isinstance(data, UploadedFile):
            pass
        else:
            raise serializers.ValidationError(_("Invalid data"))
        return super().to_internal_value(data)

    def _get_extension(self: Self, content_type: None | str, data: bytes) -> None | str:
        if not isinstance(content_type, (NoneType, str)):
            raise TypeError(_("'content_type' must be None or str"))
        if not isinstance(data, bytes):
            raise TypeError(_("'data' must be bytes"))

        extension = None
        if content_type:
            extension: str | None = mimetypes.guess_extension(content_type)
            if isinstance(extension, str):
                extension = extension.strip()
                if extension:
                    extension = extension[1:] if len(extension) > 0 else None
        if not extension:
            try:
                import filetype  # noqa: E501  # pylint: disable=import-outside-toplevel  # pyright: ignore[reportMissingImports]

                extension = filetype.guess_extension(data)
            except ImportError:
                pass
        if not extension:
            try:
                from PIL import (  # noqa: E501  # pylint: disable=import-outside-toplevel  # pyright: ignore[reportMissingImports]
                    Image,
                )

                image: Any = Image.open(io.BytesIO(data))
            except (ImportError, OSError):
                pass
            else:
                if image and image.format:
                    extension = image.format.lower()
        return extension

    def _get_content_type(self: Self, filename: str, data: bytes) -> None | str:
        if not isinstance(filename, str):
            raise TypeError(_("'filename' must be str"))
        if not isinstance(data, bytes):
            raise TypeError(_("'data' must be bytes"))

        try:
            content_type_tuple: tuple[str | None, str | None] = mimetypes.guess_file_type(
                filename,
            )
        except AttributeError:
            content_type_tuple = mimetypes.guess_type(filename)
        content_type: str | None = content_type_tuple[0]
        if not content_type:
            try:
                import filetype  # noqa: E501  # pylint: disable=import-outside-toplevel  # pyright: ignore[reportMissingImports]

                content_type = filetype.guess_mime(data)
            except ImportError:
                pass
        return content_type


class Base64ImageField(Base64FileField, ImageField):
    pass
