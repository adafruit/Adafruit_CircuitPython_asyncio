__all__ = ('StreamReader', 'StreamWriter')

from . import events
from . import exceptions
from . import tasks


async def _block(func, *args):
    result = func(*args)   
    while result is None:
        await tasks.sleep(0)
        result = func(*args)
    return result


class StreamReader:
    def __init__(self, stream, limit=256, loop=None):
        self._loop = loop if loop is not None else events.get_event_loop()
        self._stream = stream
        self._limit = limit
        self._eof = False
        self._exception = None
        self._buffer = bytearray()

    def at_eof(self):
        """Return True if the buffer is empty and 'feed_eof' was called."""
        return self._eof

    async def readline(self):
        """Read chunk of data from the stream until newline (b'\n') is found.

        On success, return chunk that ends with newline. If only partial
        line can be read due to EOF, return incomplete line without
        terminating newline. When EOF was reached while no bytes read, empty
        bytes object is returned.

        If limit is reached, ValueError will be raised. In that case, if
        newline was found, complete line including newline will be removed
        from internal buffer. Else, internal buffer will be cleared. Limit is
        compared against part of the line without newline.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        try:
            line = await self.readuntil(b'\n')
        except exceptions.IncompleteReadError as e:
            return e.partial
        except exceptions.LimitOverrunError as e:
            self._buffer.clear()
            raise ValueError(e.args[0])
        return line


    async def readuntil(self, separator=b'\n'):
        """Read data from the stream until ``separator`` is found.

        On success, the data and separator will be removed from the
        internal buffer (consumed). Returned data will include the
        separator at the end.

        Configured stream limit is used to check result. Limit sets the
        maximal length of data that can be returned, not counting the
        separator.

        If an EOF occurs and the complete separator is still not found,
        an IncompleteReadError exception will be raised, and the internal
        buffer will be reset.  The IncompleteReadError.partial attribute
        may contain the separator partially.

        If the data cannot be read because of over limit, a
        LimitOverrunError exception  will be raised, and the data
        will be left in the internal buffer, so it can be read again.
        """
        seplen = len(separator)
        if seplen != 1:
            raise ValueError('Separator should be a one-byte string')

        if self._exception is not None:
            raise self._exception

        blocks = []
        remaining = self._limit
        found = False
        while remaining > 0 and not found:
            block = await self.read(remaining)
            if not block:
                break

            offset = block.find(separator)
            remaining -= len(block)
            if offset != -1:
                self._buffer.extend(block[offset+1:])
                block = block[:offset+1]
                found = True

            blocks.append(block)
        blocks = b''.join(blocks)
        if found:
            return blocks
        elif remaining > 0:
            raise exceptions.IncompleteReadError(blocks, self._limit)
        else:
            self._buffer.extend(blocks)
            raise exceptions.LimitOverrunError('', self._limit)

    async def read(self, n=-1):
        """Read up to `n` bytes from the stream.

        If `n` is not provided or set to -1,
        read until EOF, then return all read bytes.
        If EOF was received and the internal buffer is empty,
        return an empty bytes object.

        If `n` is 0, return an empty bytes object immediately.

        If `n` is positive, return at most `n` available bytes
        as soon as at least 1 byte is available in the internal buffer.
        If EOF is received before any byte is read, return an empty
        bytes object.

        Returned value is not limited with limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        if self._exception is not None:
            raise self._exception

        if n == 0 or self._eof:
            return b''

        if n < 0:
            # This used to just loop creating a new waiter hoping to
            # collect everything in self._buffer, but that would
            # deadlock if the subprocess sends more than self.limit
            # bytes.  So just call self.read(self._limit) until EOF.
            blocks = []
            while True:
                block = await self.read(self._limit)
                if not block:
                    break
                blocks.append(block)
            return b''.join(blocks)

        if self._buffer:
            result = self._buffer[:n]
            del self._buffer[:n]
            return result

        try:
            result = await _block(self._stream.read, n)
            self._eof = self._eof or (result == b'')
            return result
        except Exception as e:
            self._exception = e
            raise

    async def readinto(self, buffer):
        if self._exception is not None:
            raise self._exception

        if len(buffer) == 0 or self._eof:
            return b''

        if self._buffer:
            buflen = min(len(self._buffer), len(buffer))
            buffer[:buflen] = self._buffer[:buflen]
            del self._buffer[:buflen]
            return buflen

        try:
            result = await _block(self._stream.readinto, buffer)
            self._eof = self._eof or (result == b'')
            return result
        except Exception as e:
            self._exception = e
            raise

    async def readexactly(self, n):
        """Read exactly `n` bytes.

        Raise an IncompleteReadError if EOF is reached before `n` bytes can be
        read. The IncompleteReadError.partial attribute of the exception will
        contain the partial read bytes.

        if n is zero, return empty bytes object.

        Returned value is not limited with limit, configured at stream
        creation.

        If stream was paused, this function will automatically resume it if
        needed.
        """
        if n < 0:
            raise ValueError('readexactly size can not be less than zero')

        if self._exception is not None:
            raise self._exception

        blocks = []
        remaining = n
        while remaining > 0:
            block = await self.read(remaining)
            if not block:
                break
            blocks.append(block)
            remaining -= len(block)
        blocks = b''.join(blocks)
        if remaining > 0:
            raise exceptions.IncompleteReadError(blocks, n)
        return blocks

    def __aiter__(self):
        return self

    async def __anext__(self):
        val = await self.readline()
        if val == b'':
            raise StopAsyncIteration
        return val

class StreamWriter:
    pass
