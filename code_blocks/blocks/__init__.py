from django.utils.html import format_html_join
from wagtail import blocks


class StreamBlockClassMixin:
    """Override for render_basic to add block_class (from child block(s) meta) to the div.

    NOTE!! This is obsoleted by the automatic addition of block_class via javascript.
    """
    # noinspection PyMethodMayBeStatic
    def render_basic(self, value, context=None):

        def child_block_class(value_child):
            return (
                ' ' + getattr(value_child.block.meta, 'block_class', '')
            ).rstrip()

        return format_html_join(
            "\n",
            '<div class="block-{1}{2}">{0}</div>',
            [
                (child.render(context=context), child.block_type, child_block_class(child))
                for child in value
            ],
        )


class ValueBlock(blocks.StaticBlock):
    """Static value block.

    Also includes a value for the admin interface.
    """
    value = None
    admin_value = None

    def __init__(self, *, value=None, admin_value=None, **kwds):
        self.value = value
        self.admin_value = admin_value
        super().__init__(**kwds)

    def __str__(self):
        return self.value

    def value_from_datadict(self, data, files, prefix):
        return self.value

    @property
    def label(self):
        return f"{self.meta.label}: {self.admin_value or self.value}"

    @label.setter
    def label(self, value):
        self.meta.label = value

    class Meta:
        label = "Value"
        admin_text = ""
        icon = "tag"
