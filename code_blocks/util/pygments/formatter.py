"""Pygments HTML formatter override to support custom tags.
"""
from io import StringIO

from pygments.formatters.html import HtmlFormatter

__all__ = ("CustomHtmlFormatter",)


class CustomHtmlFormatter(HtmlFormatter):
    name = 'Code Blocks HTML'
    aliases = ['code_blocks_html']

    def __init__(self, *args, **kwds):
        self.max_height = kwds.pop('max_height', None)
        self.resizable = kwds.pop('resizable', False)
        self.editable = kwds.pop('editable', False)
        self.heading = kwds.pop('heading', None)
        self.fit_content = kwds.pop('fit_content', False)
        self.style_dark = kwds.pop('style_dark', None)
        self.colorclass = kwds.pop('colorclass', None)
        self.block_class = kwds.pop('block_class', None)
        cssclass = kwds.pop('cssclass', None)
        kwds['wrapcode'] = True

        if not self.colorclass or not cssclass:
            raise ValueError('cssclass and colorclass must be set')

        kwds["cssclass"] = f'{cssclass} {self.colorclass}'

        super().__init__(*args, **kwds)

    def _wrap_div(self, inner):
        """An ugly copy-paste of the original method, but with rel=<title> for div tag."""
        style = []
        if (self.noclasses and not self.nobackground and
                self.style.background_color is not None):
            style.append('background: %s' % (self.style.background_color,))
        if self.cssstyles:
            style.append(self.cssstyles)
        style = '; '.join(style)

        fit_content = ' fit-content-width' if self.fit_content else ''
        light_dark_attrs = f' data-class-light="{self.colorclass}"' + (
            f' data-class-dark="{self.style_dark}"'
            if self.style_dark else ""
        )

        data_block_class = f""" data-block-class="{self.block_class}" """.rstrip() if self.block_class else ""

        if self.heading:
            yield 0, f'<div class="{self.cssclass} heading"{light_dark_attrs}>{self.heading}</div>'

        yield 0, (f'<div rel="{self.title}"{light_dark_attrs}{data_block_class}' +
                  (self.cssclass and f' class="%s{fit_content}"' % self.cssclass) +
                  (style and (' style="%s"' % style)) + '>')

        yield from inner
        yield 0, '</div>\n'

    def _wrap_tablelinenos(self, inner):
        dummyoutfile = StringIO()
        lncount = 0
        for t, line in inner:
            if t:
                lncount += 1
            dummyoutfile.write(line)

        fl = self.linenostart
        mw = len(str(lncount + fl - 1))
        sp = self.linenospecial
        st = self.linenostep
        anchor_name = self.lineanchors or self.linespans
        aln = self.anchorlinenos
        nocls = self.noclasses

        lines = []

        for i in range(fl, fl+lncount):
            print_line = i % st == 0
            special_line = sp and i % sp == 0

            if print_line:
                line = '%*d' % (mw, i)
                if aln:
                    line = '<a href="#%s-%d">%s</a>' % (anchor_name, i, line)
            else:
                line = ' ' * mw

            if nocls:
                if special_line:
                    style = ' style="%s"' % self._linenos_special_style  # noqa
                else:
                    style = ' style="%s"' % self._linenos_style  # noqa
            else:
                if special_line:
                    style = ' class="special"'
                else:
                    style = ' class="normal"'

            if style:
                line = '<span%s>%s</span>' % (style, line)

            lines.append(line)

        ls = '\n'.join(lines)

        # If a filename was specified, we can't put it into the code table as it
        # would misalign the line numbers. Hence, we emit a separate row for it.
        filename_tr = ""
        if self.filename:
            filename_tr = (
                '<tr><th colspan="2" class="filename">'
                '<span class="filename">' + self.filename + '</span>'
                '</th></tr>')

        # Added code: add max-height to table style if present
        table_class = 'scroller'
        table_style = ''

        if self.max_height:
            table_style += f' style="max-height: {self.max_height}px;"'

        resize_div = ''

        if self.resizable:
            table_class += ' resize-vertical' if not self.fit_content else ' resize-both'
            resize_div = '<div class="resize_handle"></div>'

        editable_attrs = ' contenteditable="true" spellcheck="false"' if self.editable else ''

        # in case you wonder about the seemingly redundant <div> here: since the
        # content in the other cell also is wrapped in a div, some browsers in
        # some configurations seem to mess up the formatting...
        yield 0, (f'{resize_div}<table class="{table_class} {self.cssclass}-table"{table_style}>' + filename_tr +
                  f'<tr><td class="linenos"><div class="linenodiv"><pre{editable_attrs}>' +
                  ls + '</pre></div></td><td class="code">')
        yield 0, '<div>'
        yield 0, dummyoutfile.getvalue()
        yield 0, '</div>'
        yield 0, '</td></tr></table>'

    def _wrap_code(self, inner):
        code_style = ''
        resize_div = ''
        scroller_class = ''

        if self.linenos != 1:
            scroller_class = 'scroller'

            if self.max_height or self.resizable:
                code_style = ' style="'

                if self.max_height:
                    code_style += f'max-height: {self.max_height}px; '

                if self.resizable:
                    scroller_class += ' resize-vertical' if not self.fit_content else ' resize-both'
                    resize_div = '<div class="resize_handle"></div>' if self.resizable else ''

                code_style += '"'

            scroller_class = f' class="{scroller_class}"'

        editable_attrs = ' contenteditable="true" spellcheck="false"' if self.editable else ''

        yield 0, f'{resize_div}<code{editable_attrs}{scroller_class}{code_style}>'
        yield from inner
        yield 0, '</code>'
