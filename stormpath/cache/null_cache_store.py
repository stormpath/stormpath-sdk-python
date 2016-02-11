"""Null cache backend."""


class NullCacheStore(object):
    """Simple caching implementation that performs no caching."""

    def __getitem__(self, key):
        return None

    def __setitem__(self, key, entry):
        pass

    def __delitem__(self, key):
        pass

    def clear(self):
        pass

    def __len__(self):
        return 0
