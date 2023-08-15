from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from ..util.pygments import defaults as pygments_defaults

CSS_LINK_BASE = "code_blocks/css/"
CSS_LINK_FORMAT = """<link rel="stylesheet"{id} href="{url}">"""
JS_BASE = "code_blocks/js/"

register = template.Library()


# noinspection StrFormat
def css_link(path):
    id_attr = ""

    if isinstance(path, tuple):
        path, id_attr = path

    if id_attr:
        id_attr = f' id="{id_attr}"'

    if not path.startswith("http"):
        return CSS_LINK_FORMAT.format(url=static(CSS_LINK_BASE + path), id=id_attr)

    return CSS_LINK_FORMAT.format(url=path, id=id_attr)


@register.simple_tag
def pygments_css(styles="none"):
    links = [
        "pygments_code_block.css",
        "https://cdnjs.cloudflare.com/ajax/libs/hack-font/3.3.0/web/hack.min.css",
    ]

    if styles == "all":
        styles = pygments_defaults.CODE_BLOCK_PYGMENTS_STYLES.keys()

    elif styles == "none":
        styles = []

    else:
        styles = map(str.split, styles.split(","))

    for style in styles:
        if style not in pygments_defaults.CODE_BLOCK_PYGMENTS_STYLES:
            raise ValueError(f"Invalid pygments code block style '{style}'")

        links.append((f"pygments/{style}.css", f"pygments-style-{style}"))

    # noinspection DjangoSafeString
    return mark_safe("\n".join(map(css_link, links)))


@register.simple_tag
def pygments_js(dynamic_css=True):
    dynamic_css = str(dynamic_css).lower()
    dynamic_css = f'dynamic-css="{dynamic_css}"'
    css_static_base = f'css-static-base={static(CSS_LINK_BASE)}'
    highlight_class = f'highlight-class="{pygments_defaults.CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS}"'
    src = static(JS_BASE + 'pygments_code_block.js')

    return mark_safe(
        f"""<script type="text/javascript" src="{src}" {highlight_class} {css_static_base} {dynamic_css}></script>"""
    )
