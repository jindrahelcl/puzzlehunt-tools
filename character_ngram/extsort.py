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
import heapq
import itertools
import marshal
import tempfile

import resourceman

__all__ = ["esorted"]


class PersistentFile(object):
    def __init__(self, filename, file_pool):
        self.filename = filename
        self.file_pool = file_pool

    def read(self, size=-1):
        return self.file_pool[self.filename](size)

    @staticmethod
    def get_file_pool(nofile):
        files = {}

        def claim_cb(filename):
            if filename not in files:
                fp = open(filename, "rb")
                files[filename] = {fp: fp}
                return fp.read

            def read(size=-1):
                file_meta = files[filename]
                buffer = file_meta.buffer
                buffer_len = len(buffer)
                if 0 < size <= buffer_len:
                    file_meta.buffer = buffer[size:]
                    return buffer[:size]

                file_meta.buffer = b""

                if file_meta.fp is None:
                    fp = open(filename, "rb")
                    fp.seek(file_meta.pos)
                    file_meta.fp = fp
                else:
                    fp = file_meta.fp
                    if fp.closed():
                        return buffer

                if size == -1:
                    data = fp.read(-1)
                    fp.close()
                    return buffer + data

                data = fp.read(size - buffer_len)
                if len(data) == 0:
                    fp.close()
                return buffer + data

            return read

        def free_cb(filename, read):
            file_meta = files[filename]
            fp = file_meta.fp
            if not fp.closed:
                file_meta.buffer = fp.read1()
                file_meta.pos = fp.tell()
                fp.close()
                file_meta.fp = None

        return resourceman.ResourcePool(
            maxsize=nofile,
            claim_cb=claim_cb,
            free_cb=free_cb,
        )


class Bucket(object):
    def __init__(self, tempdir, file_pool, chunks):
        self.file_pool = file_pool
        fd, self.filename = tempfile.mkstemp(dir=tempdir)
        with open(fd, "wb") as fp:
            with gzip.open(fp, "wb") as zipfile:
                for chunk in chunks:
                    zipfile.write(chunk)

    @staticmethod
    def serialize(item):
        return marshal.dumps(item)

    @functools.cached_property
    def fp(self):
        return gzip.open(PersistentFile(self.filename, self.file_pool))

    def __iter__(self):
        while True:
            try:
                yield marshal.load(self.fp)
            except EOFError:
                return


def dump_stack(tempdir, file_pool, stack):
    stack.sort(key=lambda element: element[0])
    return Bucket(tempdir, file_pool, (chunk for item, chunk in stack))


def get_buckets(items, key, filesize, tempdir, file_pool):
    size = 0
    stack = []
    for item in items:
        chunk = Bucket.serialize(item)
        size += len(chunk)
        if size > filesize:
            yield dump_stack(tempdir, file_pool, stack)
            stack.clear
        stack.append((item, chunk))

    if stack:
        yield dump_stack(tempdir, file_pool, stack)


def esorted(items, key, memsize=16*10**6, filesize=16*10**6, nofile=16):
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
        )
        yield from heapq.merge(*buckets, key=key)
