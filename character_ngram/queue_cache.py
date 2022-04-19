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

# Unless you are mad, use functools.lru_cache, go away and prosper.

class ConnectedListEntry(object):
    next = None

    def __init__(self, value):
        self.value = value

    def __iter__(self):
        current = self
        while current is not None:
            yield current.value
            current = current.next

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(list(self)))

class ConnectedList(ConnectedListEntry):
    def __init__(self):
        self.last = self

    def __iter__(self):
        if self.next:
            yield from self.next

    def extend(self, entry):
        self.last.next = entry
        self.last = entry

    def append(self, value):
        self.extend(ConnectedListEntry(value))

    def swap(self, previous):
        current = previous.next
        previous.next = current.next
        current.next = None
        self.extend(current)

class QueueCache(object):
    size = 0

    def __init__(self, cb, maxsize):
        self.cb = cb
        self.maxsize = maxsize
        self.queue = ConnectedList()
        self.prevs = {}

    def __repr__(self):
        return "{}({})".format(type(self).__name__, repr(list(self.queue)))

    def __getitem__(self, key):
        previous = self.prevs.get(key)
        if previous:
            current = previous.next
            if current is not self.queue.last:
                self.prevs[current.next.value[0]] = self.prevs[key]
                self.prevs[key] = self.queue.last
                self.queue.swap(previous)
            return current.value[1]
        else:
            value = self.cb(key)
            self.prevs[key] = self.queue.last
            if self.size == self.maxsize:
                del self.prevs[self.queue.next.value[0]]
                self.queue.swap(self.queue)
                self.queue.last.value = (key, value)
                self.prevs[self.queue.next.value[0]] = self.queue
            else:
                self.size += 1
                self.queue.append((key, value))
            return value
