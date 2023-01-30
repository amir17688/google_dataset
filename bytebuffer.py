#
# A convenient read-write buffer.  Located here for want of a better place.
#

from pypy.interpreter.buffer import RWBuffer
from pypy.interpreter.gateway import ObjSpace


class ByteBuffer(RWBuffer):

    def __init__(self, len):
        self.data = ['\x00'] * len

    def getlength(self):
        return len(self.data)

    def getitem(self, index):
        return self.data[index]

    def setitem(self, index, char):
        self.data[index] = char


def bytebuffer(space, length):
    return space.wrap(ByteBuffer(length))
bytebuffer.unwrap_spec = [ObjSpace, int]
