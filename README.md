# Django utils

## django_utils.core.validators

- FileMinSizeValidator
- FileMaxSizeValidator
- FileTypeValidator
- FileContentTypeValidator

## django_utils.django.db.models

- AutoUUID4Field
- UUIDIDMixin

## django_utils.django.db.models.helpers

- create_generic_index_name
- create_index_name
- create_unique_constraint_name

## django_utils.dju_taggit_core.models

- TagBase (abstract)
- HashtagBase (abstract)
- TaggedItemBase (abstract)
- HashtaggedItemBase (abstract)
- GenericTaggedItemBase (abstract)
- GenericUUIDTaggedItemBase (abstract)

## django_utils.dju_taggit.models

- Hashtag
- TaggedItemBase (abstract)
- HashtaggedItemBase (abstract)
- TaggedItem
- HashtaggedItem

## django_utils.drf_spectacular.openapi

- AutoSchema

## django_utils.restframework.fields

- FileField
- ImageField
- Base64FileField
- Base64ImageField

## django_utils.restframework.serializers

- ModelSerializer

## django_utils.restframework.mixins

- ResponseSerializerMixin
- CreateModelMixin
- UpdateModelMixin

## django_utils.restframework.views

- GenericViewSet

## Django apps

- django_utils.dju_taggit_core
- django_utils.dju_taggit

## Settings

- `DJANGO_UTILS_TAGGIT_AUTO_REMOVE_UNUSED_TAGS` (default: `False`)
- `TAGGIT_CASE_INSENSITIVE` (default: `False`)
- `TAGGIT_STRIP_UNICODE_WHEN_SLUGIFYING`  (default: `False`)

## Requirements

- filetype
  - django_utils.core.validators.FileType
  - django_utils.core.validators.FileContentTypeValidator (optional)
  - django_utils.restframework.fields (optional)
- django-taggit
  - django_utils.dju_taggit_core
  - django_utils.dju_taggit
- drf_spectacular
  - django_utils.drf_spectacular.openapi.AutoSchema
- Pillow
  - django_utils.restframework.fields.Base64FileField (optional)
  - django_utils.restframework.fields.Base64ImageField (optional)
- unidecode
  - django_utils.dju_taggit_core (optional)
  - django_utils.dju_taggit (optional)

## django_utils.drf_spectacular.openapi

```python
REST_FRAMEWORK = {
    ...
    "DEFAULT_SCHEMA_CLASS": "django_utils.drf_spectacular.openapi.AutoSchema",
    ...
}
```
