import re
try:
    from markdown import Markdown
except ImportError:
    Markdown = None  # NOQA
from radpress.readers import BaseReader


class Reader(BaseReader):
    name = 'Markdown'
    enabled = bool(Markdown)
    initial = """
        title: Title here
        slug: title-here
        tags: world
              big bang
              sheldon
        published: no
        image: not specified

        Content here...
    """
    description = initial

    def convertRSTmetaToMD(self):
        token = re.compile(r":(\w+:)")
        # http://stackoverflow.com/questions/2212933/python-regex-for-reading-csv-like-rows  # NOPEP8
        comma = re.compile(r'''
            \s*                # Any whitespace.
            (                  # Start capturing here.
              [^,"']+?         # Either a series of non-comma non-quote chars.
              |                # OR
              "(?:             # A double-quote followed by a string of chars.
                  [^"\\]|\\.   # That are either non-quotes or escaped...
               )*              # ...repeated any number of times.
              "                # Followed by a closing double-quote.
              |                # OR
              '(?:[^'\\]|\\.)*'# Same as above, for single quotes.
            )                  # Done capturing.
            \s*                # Allow arbitrary space before the comma.
            (?:,|$)            # Followed by a comma or the end of a string.
            ''', re.VERBOSE)
        pass1 = []
        pass2 = []

        # First, replace ":token:" with "token:"
        for line in self.source.split('\r\n'):
            if not line or line.isspace():
                break
            pass1.append(token.sub(r'\1', line))

        # Assume it's properly formatted markdown
        if pass1 == self.source.split('\r\n')[:len(pass1)]:
            return

        # Next, split up comma-seperated tags into newlines + indents
        for line in pass1:
            csv = comma.sub('\\1\n    ', line).strip()
            if csv != line:
                pass2.append(csv)
            else:
                pass2.append(line)

        # First line is a title
        pass2[0] = "title: " + pass2[0]
        # Every other line until the point where they're all the same char must
        # be the title line too, so we indent those.
        for i in xrange(1, len(pass2)):
            if pass2[i] and pass2[i] == len(pass2[i]) * pass2[i][0]:
                pass2 = pass2[:i] + pass2[i+1:]
                break
            else:
                pass2[i] = "   " + pass2[i]

        # Now, reconstruct the source: use our new tags + the remainder of the
        # source (+1 for the sake of the line of #'s).
        # Put the \r back because that's how django gave it to us, even though
        # it's stupid.
        self.source = "\r\n".join(
            pass2 + self.source.split("\r\n")[len(pass2)+1:])

    def _parse_metadata(self, meta):
        out = meta
        for key in out.keys():
            if len(out[key]) == 1:
                out[key] = "".join(out[key])
            if key == "published":
                out[key] = out[key] == "yes"
            if key == "tags":
                out[key] = list(set(out[key]))

        return out

    def read(self):
        """Parse content and metadata of markdown files"""
        self.convertRSTmetaToMD()
        self._md = Markdown(extensions=['meta', 'codehilite(linenums=True)'])
        content = self._md.convert(self.source)
        metadata = self._parse_metadata(self._md.Meta)
        return content, metadata
