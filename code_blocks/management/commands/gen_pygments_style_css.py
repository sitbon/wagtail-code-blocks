from pathlib import Path
import sys

from django.core.management.base import BaseCommand

from pygments.cmdline import main as pygments_main
from pygments.formatters import HtmlFormatter

import code_blocks
from code_blocks.util.pygments import defaults

CSS_DIR = Path(code_blocks.__path__[0]) / "static" / "code_blocks" / "css" / "pygments"

class Command(BaseCommand):
    help = "Generate pygments style css files."

    def add_arguments(self, parser):
        parser.add_argument('--dir', action="store", type=str, help="Change output dir.")
        parser.add_argument('--clean', action="store_true", help="Remove CSS files from output dir.")
        parser.add_argument('--replace', action="store_true", help="Replace existing styles in output dir.")
        parser.add_argument('--list', action="store_true", help="List available styles.")
        parser.add_argument('--styles', action="store", nargs="+", default=[],
                            help="Generate selected styles.")

    def handle(self, *args, **options):
        if options["list"]:
            for style, name in defaults.CODE_BLOCK_PYGMENTS_STYLES.items():
                print(name.ljust(20), style)
            return 0

        replace = options["replace"]
        clean = options["clean"]
        css_dir = CSS_DIR

        if options["dir"]:
            css_dir = Path(options["dir"])

            if not css_dir.exists():
                print(f"Creating directory '{css_dir}'", file=sys.stderr)
                css_dir.mkdir(parents=True)

        if clean:
            for file in css_dir.iterdir():
                if file.suffix == ".css":
                    print(f"Removing {file}", file=sys.stderr)
                    file.unlink()

        styles = options["styles"] or defaults.CODE_BLOCK_PYGMENTS_STYLES

        for style_name in styles:
            if style_name not in defaults.CODE_BLOCK_PYGMENTS_STYLES:
                print(f"Invalid style '{style_name}'", file=sys.stderr)
                continue

            # css_file_name = os.path.join(css_dir, f"{style_name}.css")
            css_file = css_dir / f"{style_name}.css"

            if not replace and css_file.exists():
                print(f"Skipping {style_name} (already exists)", file=sys.stderr)
                continue

            with css_file.open("w") as file:
                sys.stdout = file

                args = [
                    "pygmentize",
                    "-S", style_name,
                    "-f", "html",
                    "-a", f".{defaults.CODE_BLOCK_PYGMENTS_HIGHLIGHT_CLASS}-{style_name}"
                ]

                error = pygments_main(args)

                if error:
                    return error

# Hooks HTML formatter output for pygmentize.
#


def get_style_defs(self, arg=None):
    """
    Return CSS style definitions for the classes produced by the current
    highlighting style. ``arg`` can be a string or list of selectors to
    insert before the token type classes.
    """
    style_lines = []

    style_lines.extend(self.get_linenos_style_defs(arg))
    style_lines.extend(self.get_background_style_defs(arg))
    style_lines.extend(self.get_token_style_defs(arg))

    return '\n'.join(style_lines)


def get_linenos_style_defs(self, arg):
    lines = [
        '%s pre { %s }' % (arg, self._pre_style),
        '%s td.linenos .normal { %s }' % (arg, self._linenos_style),
        '%s span.linenos { %s }' % (arg, self._linenos_style),
        '%s td.linenos .special { %s }' % (arg, self._linenos_special_style),
        '%s span.linenos.special { %s }' % (arg, self._linenos_special_style),
    ]

    return lines


HtmlFormatter.get_style_defs = get_style_defs
HtmlFormatter.get_linenos_style_defs = get_linenos_style_defs
