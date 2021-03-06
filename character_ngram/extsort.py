##
# Copyright (C) 2022 Tomas "trosos" Tintera
#
# Permission to use, copy, modify, and/or distribute this
# software for any purpose with or without fee is hereby
# granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS
# ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH
# THE USE OR PERFORMANCE OF THIS SOFTWARE.
##

__all__ = ["esorted"]

import functools
import gzip
import heapq
import io
import itertools
import marshal
import tempfile

import resourceman


class FileMeta(object):
    emptybuffer = memoryview(bytearray(b""))

    def __init__(self, fp):
        self.fp = fp
        self.buffer = self.emptybuffer
        self.pos = 0

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr({
            "fp": self.fp,
            "buffer": bytes(self.buffer),
            "pos": self.pos,
        }))


class PersistentFile(io.RawIOBase):
    def __init__(self, filename, file_pool):
        self.filename = filename
        self.file_pool = file_pool

    def readinto(self, b):
        size = len(b)
        if size == 0:
            return 0
        file_meta = self.file_pool.files.get(self.filename)
        if file_meta:
            buffer = file_meta.buffer
            buffer_len = len(buffer)
            if size <= buffer_len:
                b[:size] = buffer[:size]
                file_meta.buffer = buffer[size:]
                return size
            fp = file_meta.fp
            if fp and fp.closed:
                b[:buffer_len] = buffer
                file_meta.buffer = file_meta.emptybuffer
                return buffer_len
        return self.file_pool[self.filename](b)

    @staticmethod
    def get_file_pool(nofile):
        files = {}

        def claim_cb(filename):
            if filename not in files:
                fp = open(filename, "rb")
                files[filename] = FileMeta(fp)

            def readinto(b):
                file_meta = files[filename]
                buffer = file_meta.buffer
                buffer_len = len(buffer)

                b[:buffer_len] = buffer

                if file_meta.fp is None:
                    fp = open(filename, "rb")
                    fp.seek(file_meta.pos)
                    file_meta.fp = fp
                else:
                    fp = file_meta.fp

                data_len = fp.readinto(memoryview(b)[buffer_len:])
                buffer = memoryview(bytearray(fp.read1()))
                if len(buffer) == 0:
                    fp.close()
                    file_meta.buffer = file_meta.emptybuffer
                else:
                    file_meta.buffer = buffer
                return buffer_len + data_len

            return readinto

        def free_cb(filename, read):
            file_meta = files[filename]
            fp = file_meta.fp
            if fp and not fp.closed:
                file_meta.pos = fp.tell()
                fp.close()
                # Clear fp so that we know we should reopen next time:
                file_meta.fp = None

        file_pool = resourceman.ResourcePool(
            maxsize=nofile,
            claim_cb=claim_cb,
            free_cb=free_cb,
        )
        file_pool.files = files
        return file_pool


class Bucket(object):
    @staticmethod
    def _write_chunks(fp, chunks):
        for chunk in chunks:
            fp.write(chunk)

    def __init__(self, tempdir, file_pool, chunks, compresslevel):
        self.compresslevel = compresslevel
        self.file_pool = file_pool
        fd, self.filename = tempfile.mkstemp(dir=tempdir)
        with open(fd, "wb") as fp:
            if compresslevel == 0:
                self._write_chunks(fp, chunks)
                return
            with gzip.open(fp, "wb", compresslevel=compresslevel) as zipfile:
                self._write_chunks(zipfile, chunks)

    @staticmethod
    def serialize(item):
        return marshal.dumps(item)

    @functools.cached_property
    def fp(self):
        persistent_file = PersistentFile(self.filename, self.file_pool)
        if self.compresslevel == 0:
            return persistent_file
        return gzip.open(persistent_file)

    def __iter__(self):
        while True:
            try:
                yield marshal.load(self.fp)
            except EOFError:
                return


def dump_stack(tempdir, key, file_pool, stack, compresslevel):
    stack.sort(key=lambda element: key(element[0]))
    return Bucket(
        tempdir=tempdir,
        file_pool=file_pool,
        chunks=(chunk for item, chunk in stack),
        compresslevel=compresslevel,
    )


def get_buckets(items, key, filesize, tempdir, file_pool, compresslevel):
    size = 0
    stack = []
    for item in items:
        chunk = Bucket.serialize(item)
        chunk_len = len(chunk)
        size += chunk_len
        if size > filesize and stack:
            yield dump_stack(tempdir, key, file_pool, stack, compresslevel)
            stack.clear()
            size = chunk_len
        stack.append((item, chunk))

    if stack:
        yield dump_stack(tempdir, key, file_pool, stack, compresslevel)


def esorted(
        items, key=lambda x: x,
        memsize=2**24,
        filesize=2**17,
        nofile=17,
        compresslevel=0):
    """Sort an iterable using controlled memory footprint.

    Parameters
    ----------
    items : Iterable
        Items to be sorted.
    key : Callable[[Any], Any], optional
        Key function to be used to compare items.
    memsize : int, optional
        Approximate threshold for RAM usage.
        Algorithm will use external sort if RAM usage would be greater.
        To speed things up, use 0 if you know you want external sort.
        The default, 16 MiB should be nice to RAM.
    filesize : int, optional
        Maximum size of temporary files, in uncompressed form.
        The default, 128 KiB seems to go well with 1 MiB L2 cache.
    nofile : int, optional
        Maximum number of open file descriptors.
        Speedup for higher values should be noticable mainly for
        real-life inputs, where data are not in truly random order.
        The dafault, 17 is quite moderate on today's systems;
        it is taken from the default for GNU sort when getrlimit
        functionality is unavailable.
    compresslevel : int, optional
        gzip compression level
        The default, 0 disables gzip completely.

    Returns
    -------
    Iterable
        Items sorted.
    """
    item_list = []
    item_iter = iter(items)
    size = 0
    for item in item_iter:
        item_list.append(item)
        if size >= memsize:
            break
        size += len(marshal.dumps(item))
    else:
        item_list.sort(key=key)
        yield from item_list
        return

    with tempfile.TemporaryDirectory() as tempdir:
        buckets = get_buckets(
            items=itertools.chain(item_list, item_iter),
            key=key,
            filesize=filesize,
            tempdir=tempdir,
            file_pool=PersistentFile.get_file_pool(nofile),
            compresslevel=compresslevel,
        )
        yield from heapq.merge(*buckets, key=key)
