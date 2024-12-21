try:
    from typing import TYPE_CHECKING

    from django.utils.functional import keep_lazy_text
    from django.utils.text import slugify as _slugify
    from unidecode import unidecode

    if TYPE_CHECKING:
        from django.utils.safestring import SafeText

    @keep_lazy_text
    def slugify(value: str, allow_unicode: bool = False) -> 'SafeText':
        if not allow_unicode:
            value = unidecode(value)
        return _slugify(value=value, allow_unicode=allow_unicode)

except ImportError:
    pass
