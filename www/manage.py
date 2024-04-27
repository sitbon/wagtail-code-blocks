import os
import sys

import django
from django.core.management import execute_from_command_line


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "www.conf")
    django.setup()
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
