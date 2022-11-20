from django.apps import AppConfig


class CodeBlocksAppConfig(AppConfig):
    name = 'web.apps.code_blocks'
    label = 'code_blocks'
    verbose_name = 'Wagtail Code Blocks'
    default_auto_field = 'django.db.models.BigAutoField'
