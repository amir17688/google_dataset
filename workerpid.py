import os

from wsgid.interfaces.filters import IPostRequestFilter
from wsgid.core import Plugin


class WorkerPidFilter(Plugin):
    '''
     Simple fillter that adds one more response header containing the
     pid of the Wsgid workers that was running the WSGI application
    '''

    implements = [IPostRequestFilter, ]

    def process(self, message, status, headers, body):
        return (status, headers + [('X-Worker', os.getpid())], body)

    def exception(self, message, e):
        pass
