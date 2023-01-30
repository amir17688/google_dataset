from docutils.parsers.rst import Directive
from radpress.settings import MORE_TAG


class More(Directive):
    """
    Adds `more` tag to separate summary of entry. You can show only summaries
    of blog entries at index page.
    """
    def run(self):
        return MORE_TAG
