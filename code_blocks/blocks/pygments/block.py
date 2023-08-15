import itertools
from functools import lru_cache, cache

from django.core.exceptions import ValidationError
from django import forms
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from wagtail import blocks

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from wagtail.blocks.struct_block import StructBlockValidationError

from ...util.pygments.formatter import CustomHtmlFormatter
from ...util.pygments.defaults import (
    CODE_BLOCK_PYGMENTS_LANGUAGES,
    CODE_BLOCK_PYGMENTS_STYLES,
    CODE_BLOCK_PYGMENTS_LINENO_CHOICES,
    CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS
)

from .. import ValueBlock

__all__ = "PygmentsCodeBlock",


class HtmlFieldBlock(blocks.FieldBlock):
    field = forms.CharField(widget=forms.HiddenInput)


class PygmentsCodeBlock(blocks.StructBlock):
    """A Pygments-powered code block.

    TODO: Arrange form via form_template:
    https://docs.wagtail.org/en/stable/advanced_topics/customisation/streamfield_blocks.html#custom-editing-interfaces-for-structblock

    TODO:
        - Add a "Copy to clipboard" button.
        - Add a reset button for editable.
    """
    language = blocks.ChoiceBlock(choices=CODE_BLOCK_PYGMENTS_LANGUAGES.items(),
                                  default=next(iter(CODE_BLOCK_PYGMENTS_LANGUAGES.keys())))
    style = blocks.ChoiceBlock(choices=CODE_BLOCK_PYGMENTS_STYLES.items(),
                               default=next(iter(CODE_BLOCK_PYGMENTS_STYLES.keys())))
    style_dark = blocks.ChoiceBlock(choices=CODE_BLOCK_PYGMENTS_STYLES.items(),
                                    required=False, )
    heading = blocks.CharBlock(required=False, default="")
    corner_text = blocks.CharBlock(required=False, default="", help_text="Defaults to language name.")
    show_corner_text = blocks.BooleanBlock(required=False, default=True)
    linenos = blocks.ChoiceBlock(choices=CODE_BLOCK_PYGMENTS_LINENO_CHOICES, required=False)
    max_height = blocks.IntegerBlock(required=False, default=None, min_value=40)
    resizable = blocks.BooleanBlock(required=False, default=False)
    fit_content = blocks.BooleanBlock(required=False, default=False,
                                      help_text="Fit width to content (and make horizontally resizable if resizable).")
    editable = blocks.BooleanBlock(required=False, default=False)
    code = blocks.TextBlock(form_classname="code-block-code")
    html = HtmlFieldBlock()

    MUTABLE_META_ATTRIBUTES = ["default", "disabled", "hidden", "block_class"]

    class Meta:
        icon = 'code'
        label_format = "Code [{language}]"
        form_template = "code_blocks/admin/forms/pygments_code_block.html"
        classname = "block-code not-prose"
        form_classname = "code-block-form struct-block"
        default = {
            "show_corner_text": False,
        }
        disabled = {}
        hidden = {
            "editable": False,
            "linenos": None,
        }

    def __init__(self, *args, **kwds):

        # Merge these keyword dicts with class meta defaults, instead of letting the superclass overwrite them.
        default = kwds.pop("default", {})
        disabled = kwds.pop("disabled", {})
        hidden = kwds.pop("hidden", {})
        block_class = kwds.pop("block_class", "")
        languages = kwds.pop("languages", [])
        styles = kwds.pop("styles", [])

        super().__init__(*args, **kwds)

        self.meta.default.update(default)
        self.meta.disabled.update(disabled)
        self.meta.hidden.update(hidden)

        self.meta.block_class = block_class or getattr(self.meta, "block_class", "")
        self.meta.languages = languages or getattr(self.meta, "languages", [])
        self.meta.styles = styles or getattr(self.meta, "styles", [])

        self.__configure()

    def __configure(self):
        disabled = dict(self.meta.disabled)
        default = self.meta.default
        hidden = self.meta.hidden

        allowed_keys = set(self.child_blocks.keys())

        shared_keys = PygmentsCodeBlock.__check_exclusivity(default, disabled, hidden)

        if shared_keys:
            raise ValueError(f"Cannot use the same field for default, disabled, and hidden: {shared_keys}")

        used_keys = set(itertools.chain(default, disabled, hidden))
        invalid_keys = used_keys - allowed_keys

        if invalid_keys:
            raise ValueError(f"Invalid keys in default, disabled, or hidden: {invalid_keys}")

        languages = self.meta.__dict__.pop("languages", [])
        styles = self.meta.__dict__.pop("styles", [])

        if languages and "language" in used_keys and "language" not in default:
            raise ValueError("Cannot use languages when specifying disabled/hidden language.")

        if styles and "style" in used_keys and "style" not in default:
            raise ValueError("Cannot use styles when specifying disabled/hidden style.")

        language = disabled.pop("language", hidden.get("language", None))

        if language:
            languages = [language]
        elif "language" in default and default["language"] not in CODE_BLOCK_PYGMENTS_LANGUAGES:
            raise ValueError(f"Invalid default language: {default['language']}")

        language_choices = {}
        default_language = None

        for language in languages:
            if language not in CODE_BLOCK_PYGMENTS_LANGUAGES:
                raise ValueError(f"Invalid language: {language}")

            language_choices[language] = CODE_BLOCK_PYGMENTS_LANGUAGES[language]

            if not default_language:
                default_language = language

        language_name = None

        if len(language_choices) == 1:
            language_id, language_name = list(language_choices.items())[0]

            if language not in hidden:
                self.child_blocks["language"] = ValueBlock(
                    label="Language",
                    value=language_id,
                    admin_value=language_name,
                )
        elif language_choices:
            self.child_blocks["language"] = blocks.ChoiceBlock(choices=language_choices.items(),
                                                               default=default_language)

        style = disabled.pop("style", hidden.get("style", None))
        style_dark = disabled.get("style_dark", hidden.get("style_dark", None))

        if style:
            styles = [style]
        elif "style" in default and default["style"] not in CODE_BLOCK_PYGMENTS_STYLES:
            raise ValueError(f"Invalid default style: {default['style']}")

        style_choices = {}
        default_style = None
        default_style_dark = style_dark

        for style in styles:
            if style not in CODE_BLOCK_PYGMENTS_STYLES:
                raise ValueError(f"Invalid style: {style}")

            style_choices[style] = CODE_BLOCK_PYGMENTS_STYLES[style]

            if not default_style:
                default_style = style

            if not default_style_dark:
                default_style_dark = style

        # Allow valid dark styles outside of style_choices.
        if style_dark and style_dark not in CODE_BLOCK_PYGMENTS_STYLES:
            raise ValueError(f"Invalid style_dark: {style_dark}")

        if len(style_choices) == 1:
            style_id, style_name = list(style_choices.items())[0]

            if style not in hidden:
                self.child_blocks["style"] = ValueBlock(
                    label="Style",
                    value=style_id,
                    admin_value=style_name,
                )

            if style_dark and "style_dark" not in hidden:
                self.child_blocks["style_dark"] = ValueBlock(
                    label="Style dark",
                    value=style_id,
                    admin_value=style_name,
                )
        elif style_choices:
            self.child_blocks["style"] = blocks.ChoiceBlock(choices=style_choices.items(), default=default_style)

            if not style_dark:
                self.child_blocks["style_dark"] = blocks.ChoiceBlock(
                    choices=style_choices.items(), default=default_style_dark
                )

        for field, value in disabled.items():
            self.child_blocks[field] = ValueBlock(
                label=field.title(),
                value=value,
                admin_value=value,
            )

        for field, value in hidden.items():
            del self.child_blocks[field]

        # NOTE: It's left up to the caller to ensure that the default/hidden/disabled fields
        #       make sense, e.g. hiding or disabling corner_text if show_corner_text is off
        #       and hidden or disabled... or the other way around if show_corner_text is on.

        if self.meta.label:
            self.meta.label_format = self.meta.label + " [{language}]"

        if language_name:
            # noinspection StrFormat
            self.meta.label_format = self.meta.label_format.format(language=language_name)

    @staticmethod
    def __check_exclusivity(*dicts):
        sets = [set(d.keys()) for d in dicts]
        shared = []

        for s1, s2 in itertools.combinations(sets, 2):
            inter = s1 & s2
            if inter:
                shared.append(inter)

        return shared

    def __value_or_hidden(self, value, field):
        v = value.get(field, self.meta.hidden.get(field, ...))

        if v is ...:
            raise ValueError(f"Missing value for {field}")

        return v

    def __error_field(self, field, alt_field):
        if field not in self.meta.hidden:
            return field

        if alt_field not in self.meta.hidden:
            return alt_field

        return next(iter(self.child_blocks.keys()))

    def clean(self, value):
        corner_text = self.__value_or_hidden(value, "corner_text")
        show_corner_text = self.__value_or_hidden(value, "show_corner_text")
        editable = self.__value_or_hidden(value, "editable")
        linenos = self.__value_or_hidden(value, "linenos")
        language = self.__value_or_hidden(value, "language")

        # TODO: This doesn't work to show validation errors on hidden fields.

        if corner_text and not show_corner_text:
            error = ValidationError("Cannot set custom corner text without showing it.")

            raise StructBlockValidationError({
                self.__error_field("corner_text", "show_corner_text"): ErrorList([error]),
            })

        if editable and linenos:
            error = ValidationError("Editable code blocks cannot have line numbers (for now).")

            raise StructBlockValidationError({
                self.__error_field("editable", "linenos"): ErrorList([error]),
            })

        if editable and language != 'text':
            error = ValidationError("Editable code blocks must be plain text (for now).")

            raise StructBlockValidationError({
                self.__error_field("editable", "language"): ErrorList([error]),
            })

        if language == "auto":
            code = self.__value_or_hidden(value, "code")
            lexer = guess_lexer(code)

            for alias in lexer.__class__.aliases:
                if alias in CODE_BLOCK_PYGMENTS_LANGUAGES:
                    language = lexer.__class__.aliases[0]
                    self.language = value["language"] = language
                    break
                else:
                    error = ValidationError(
                        f"Auto-detected language {lexer.__class__.name} is not present in CODE_BLOCK_PYGMENTS_LANGUAGES."
                    )

                    raise StructBlockValidationError({
                        self.__error_field("language", "code"): ErrorList([error]),
                    })

        value["html"] = ""
        value["html"] = self.render_basic(value)

        return super().clean(value)

    @staticmethod
    @cache
    def get_formatter(
            heading, title, block_class, cssclass, colorclass, style,
            style_dark, linenos, max_height, resizable, fit_content, editable
    ):
        return CustomHtmlFormatter(
            heading=heading,
            title=title,
            block_class=block_class,
            cssclass=cssclass,
            colorclass=colorclass,
            # classprefix='code-',
            # noclasses=True,
            style=style,
            style_dark=style_dark,
            linenos=linenos or False,
            # linenostart=1,  # TODO: make this configurable
            # lineanchors='line',  # TODO: make this configurable
            # anchorlinenos=True,  # TODO: make this configurable
            wrapcode=True,
            max_height=max_height,
            resizable=resizable,
            fit_content=fit_content,
            editable=editable,
        )

    @staticmethod
    @lru_cache(maxsize=1024)
    def highlight(
            language, style, style_dark, linenos, editable, resizable, fit_content, max_height,
            corner_text, show_corner_text, heading, code, block_class
    ):
        cssclass = CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS
        colorclass = f"{cssclass}-{style}"

        if style_dark:
            style_dark = f"{cssclass}-{style_dark}"

        if language == "auto":
            lexer = guess_lexer(code)
            language = lexer.__class__.name
        else:
            lexer = get_lexer_by_name(language)

        title = corner_text or (language.upper() if show_corner_text else "")

        html_formatter = PygmentsCodeBlock.get_formatter(
            heading,
            title,
            block_class,
            cssclass,
            colorclass,
            style,
            style_dark,
            linenos,
            max_height,
            resizable,
            fit_content,
            editable,
        )

        return highlight(code, lexer, html_formatter)

    def render_basic(self, value, context=None):
        html = value.get("html", "")

        if not html:
            language = self.__value_or_hidden(value, "language")
            style = self.__value_or_hidden(value, "style")
            style_dark = self.__value_or_hidden(value, "style_dark")
            linenos = self.__value_or_hidden(value, "linenos")
            editable = self.__value_or_hidden(value, "editable")
            resizable = self.__value_or_hidden(value, "resizable")
            fit_content = self.__value_or_hidden(value, "fit_content")
            max_height = self.__value_or_hidden(value, "max_height")
            corner_text = self.__value_or_hidden(value, "corner_text")
            show_corner_text = self.__value_or_hidden(value, "show_corner_text")
            heading = self.__value_or_hidden(value, "heading")
            code = self.__value_or_hidden(value, "code")

            block_class = self.meta.block_class

            html = PygmentsCodeBlock.highlight(
                language, style, style_dark, linenos, editable, resizable, fit_content, max_height,
                corner_text, show_corner_text, heading, code, block_class
            )

        # noinspection DjangoSafeString
        return mark_safe(html)
