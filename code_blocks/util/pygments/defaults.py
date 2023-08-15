from __future__ import annotations

from django.conf import settings

from pygments import lexers, styles

__all__ = (
    "CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES",
    "CODE_BLOCK_PYGMENTS_LANGUAGES",
    "CODE_BLOCK_PYGMENTS_STYLES",
    "CODE_BLOCK_PYGMENTS_LINENO_CHOICES",
    "CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS",
)

CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES: list[str] = list(getattr(settings, 'CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES', ['auto']))
CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES_ONLY: bool = bool(getattr(settings, "CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES_ONLY", False))

CODE_BLOCK_PYGMENTS_SHOW_ALIASES: bool = bool(getattr(settings, "CODE_BLOCK_PYGMENTS_SHOW_ALIASES", False))

CODE_BLOCK_PYGMENTS_STYLE_CHOICES: dict[str, str] = dict(getattr(settings, 'CODE_BLOCK_PYGMENTS_STYLE_CHOICES', {}))

CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS = getattr(settings, 'CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS', 'highlight')

CODE_BLOCK_PYGMENTS_LINENO_CHOICES = (
    ('inline', 'Inline'),
    ('table', 'Table'),
)


def _get_languages(defaults_only: bool = False):
    if auto := ("auto" in CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES):
        CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES.remove("auto")

    defaults: list[tuple[str, str] | None] = [None] * len(CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES)
    languages: list[tuple[str, str]] = []

    for name, aliases, filenames, mimetypes in lexers.get_all_lexers():
        if not aliases:
            continue

        for alias in aliases:
            if alias in CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES:
                defaults[CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES.index(alias)] = (alias, _make_name(alias, name))
                break
        else:
            languages.append((aliases[0], _make_name(aliases[0], name)))

    if not all(defaults):
        raise ValueError("One or more of CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES are not supported by Pygments.")

    return dict(
        ([("auto", "(Automatic)")] if auto else []) 
        + sorted(defaults, key=lambda x: x[1].lower())
        + sorted(languages if not defaults_only else [], key=lambda x: x[1].lower())
    )


def _get_styles():
    styles_ = []

    use_style = (lambda n: n in CODE_BLOCK_PYGMENTS_STYLE_CHOICES) if CODE_BLOCK_PYGMENTS_STYLE_CHOICES else (lambda n: True)

    for alias in filter(use_style, styles.get_all_styles()):
        styles_.append((alias, _make_name(alias,  alias.replace("_", " ").replace("-", " ").title())))

    if not styles_:
        raise ValueError("CODE_BLOCK_PYGMENTS_STYLE_CHOICES is non-empty and specifies unsupported styles.")

    return dict(sorted(styles_, key=lambda x: x[1].lower()))


def _make_name(alias: str, name: str) -> str:
    return (
        f"{name} ({alias})"
        if CODE_BLOCK_PYGMENTS_SHOW_ALIASES
        and alias.lower() != name.lower()
        and alias != "auto"
        else name
    )


CODE_BLOCK_PYGMENTS_LANGUAGES: dict[str, str] = _get_languages(CODE_BLOCK_PYGMENTS_DEFAULT_LANGUAGES_ONLY)
CODE_BLOCK_PYGMENTS_STYLES: dict[str, str] = _get_styles()
