"""Cache stats."""


from collections import namedtuple


class CacheStats(object):
    """Represents cache statistics."""
    Summary = namedtuple('CacheStats', 'puts hits misses expirations size')

    def __init__(self):
        self.puts = 0
        self.hits = 0
        self.misses = 0
        self.expirations = 0
        self.size = 0

    def put(self, new=True):
        self.puts += 1
        if new:
            self.size += 1

    def hit(self):
        self.hits += 1

    def miss(self, expired=False):
        self.misses += 1
        if expired:
            self.expirations += 1

    def delete(self):
        if self.size > 0:
            self.size -= 1

    def clear(self):
        self.size = 0

    @property
    def summary(self):
        return self.Summary(self.puts, self.hits, self.misses,
            self.expirations, self.size)
