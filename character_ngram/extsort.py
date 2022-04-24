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

import functools
import gzip
import io
import heapq
import itertools
import marshal
import tempfile

import resourceman

__all__ = ["esorted"]


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
        if file_meta and size <= len(file_meta.buffer):
            b[:size] = file_meta.buffer[:size]
            file_meta.buffer = file_meta.buffer[size:]
            return size
        else:
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
                file_meta.buffer = file_meta.emptybuffer

                if file_meta.fp is None:
                    fp = open(filename, "rb")
                    fp.seek(file_meta.pos)
                    file_meta.fp = fp
                else:
                    fp = file_meta.fp
                    if fp.closed:
                        return buffer_len

                data_len = fp.readinto(memoryview(b)[buffer_len:])
                if data_len == 0:
                    fp.close()
                return buffer_len + data_len

            return readinto

        def free_cb(filename, read):
            file_meta = files[filename]
            fp = file_meta.fp
            if fp and not fp.closed:
                buffer = memoryview(bytearray(fp.read1()))
                file_meta.buffer = buffer
                file_meta.pos = fp.tell()
                fp.close()
                if buffer:
                    # Clear fp so that we know we should reopen next time
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


def esorted(items, key=lambda x: x,
            memsize=2**24, filesize=2**24, nofile=17, compresslevel=0):
    item_list = []
    item_iter = iter(items)
    size = 0
    for item in item_iter:
        item_list.append(item)
        size += len(marshal.dumps(item))
        if size > memsize:
            break
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
            compresslevel=compresslevel
        )
        yield from heapq.merge(*buckets, key=key)
