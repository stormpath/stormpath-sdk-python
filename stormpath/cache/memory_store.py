"""A memory store cache backend."""


class MemoryStore(object):
    """Simple caching implementation that uses memory as data storage.
    """
    def __init__(self):
        self.store = {}

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
