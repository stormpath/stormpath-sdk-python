"""A memory store cache backend."""

from collections import OrderedDict


class LimitedSizeDict(OrderedDict):

    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop("max_entries")
        if self.size_limit < 1:
            raise ValueError('Memory store: max entries needs to be a positive number.')
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

    MAX_ENTRIES = 1000  # Maximum number of entries in cache

    def __init__(self, *args, **kwargs):
        max_entries = kwargs.pop('max_entries', self.MAX_ENTRIES)
        self.store = LimitedSizeDict(max_entries=max_entries)

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
