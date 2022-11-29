from django import forms
from django.utils.functional import cached_property

# noinspection PyProtectedMember
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.telepath import register

from .block import PygmentsCodeBlock

__all__ = "PygmentsCodeBlockAdapter",


class PygmentsCodeBlockAdapter(StructBlockAdapter):
    js_constructor = 'code_blocks.blocks.pygments.PygmentsCodeBlock'

    CSS = ['code_blocks/css/admin/pygments_code_block.css']
    JS = ['code_blocks/js/admin/pygments_code_block.js']

    # noinspection PyProtectedMember
    @cached_property
    def media(self):
        structblock_media = super().media

        css = dict(structblock_media._css)
        css.setdefault('all', []).extend(self.CSS)

        return forms.Media(
            js=structblock_media._js + self.JS,
            css=css,
        )


register(PygmentsCodeBlockAdapter(), PygmentsCodeBlock)
