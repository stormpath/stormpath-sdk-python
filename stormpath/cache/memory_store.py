"""A memory store cache backend."""

from collections import OrderedDict


class LimitedSizeDict(OrderedDict):
    MAX_ENTRIES = 1000  # Maximum number of entries in cache

    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop("max_entries", self.MAX_ENTRIES)
        OrderedDict.__init__(self, *args, **kwargs)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        while len(self) > self.size_limit:
            self.popitem(last=False)


class MemoryStore(object):
    """Simple caching implementation that uses memory as data storage."""

    def __init__(self):
        self.store = LimitedSizeDict()

    def __getitem__(self, key):
        return self.store.get(key)

    def __setitem__(self, key, entry):
        self.store[key] = entry

    def __delitem__(self, key):
        if key in self.store:
            del self.store[key]

    def clear(self):
        self.store.clear()

    def __len__(self):
        return len(self.store)

