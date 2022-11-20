from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)

__all__ = "CodeBlockSettings",


@register_setting(icon="code")
class CodeBlockSettings(BaseGenericSetting):
    block_class = models.CharField(
        max_length=255, blank=True,
        help_text="Additional CSS class names for div.block-code (alternative to using Meta.block_class).",
    )

    panels = [
        FieldPanel('block_class'),
    ]

    class Meta:
        verbose_name = "Code Blocks"
