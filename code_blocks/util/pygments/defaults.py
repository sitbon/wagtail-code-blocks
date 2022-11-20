from django.conf import settings

from pygments import lexers, styles

__all__ = (
    "CODE_BLOCK_LANGUAGES",
    "CODE_BLOCK_LANGUAGES_DEFAULT",
    "CODE_BLOCK_STYLES",
    "LINENO_CHOICES",
    "HIGHLIGHT_CLASS",
)


def _get_default_languages():
    defaults: list[tuple[str, str] | None] = [None] * len(CODE_BLOCK_LANGUAGES_DEFAULT)
    languages: list[tuple[str, str]] = []

    for name, aliases, filenames, mimetypes in lexers.get_all_lexers():
        if not aliases:
            continue

        for alias in aliases:
            if alias in CODE_BLOCK_LANGUAGES_DEFAULT:
                defaults[CODE_BLOCK_LANGUAGES_DEFAULT.index(alias)] = (alias, name)
                break
        else:
            languages.append((aliases[0], name))

    if not all(defaults):
        raise ValueError("One or more of CODE_BLOCK_LANGUAGES_DEFAULT are not supported by Pygments.")

    return defaults + languages


def _get_default_styles():
    styles_ = []

    for name in styles.get_all_styles():
        styles_.append((name, name.replace("_", " ").replace("-", " ").title()))

    return styles_


CODE_BLOCK_LANGUAGES_DEFAULT = getattr(settings, 'CODE_BLOCK_LANGUAGES_DEFAULT',
                                       ['text', 'python', 'pytb', 'pycon', 'bash'])
CODE_BLOCK_LANGUAGES = dict(getattr(settings, 'CODE_BLOCK_LANGUAGES', _get_default_languages()))
CODE_BLOCK_STYLES = dict(getattr(settings, 'CODE_BLOCK_STYLES', _get_default_styles()))

LINENO_CHOICES = (
    ('inline', 'Inline'),
    ('table', 'Table'),
)

HIGHLIGHT_CLASS = getattr(settings, 'HIGHLIGHT_CLASS', 'highlight')
