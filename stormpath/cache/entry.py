"""Cache entry abstractions."""


from datetime import (
    datetime,
    timedelta,
)


class CacheEntry(object):
    """A single entry inside a cache.

    It contains the data as originally returned by Stormpath along with
    additional metadata like timestamps.
    """

    def __init__(self, value, created_at=None, last_accessed_at=None):
        self.value = value
        self.created_at = created_at or datetime.utcnow()
        self.last_accessed_at = last_accessed_at or self.created_at

    def touch(self):
        self.last_accessed_at = datetime.utcnow()

    def is_expired(self, ttl, tti):
        now = datetime.utcnow()
        return (now >= self.created_at + timedelta(seconds=ttl) or
            now >= self.last_accessed_at + timedelta(seconds=tti))

    @classmethod
    def parse(cls, data):
        def parse_date(val):
            try:
                return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
            except Exception:
                return None

        return cls(data.get('value'),
            created_at=parse_date(data.get('created_at')),
            last_accessed_at=parse_date(data.get('last_accessed_at')))

    def to_dict(self):
        def print_date(val):
            return val.strftime('%Y-%m-%d %H:%M:%S.%f')

        return {
            'created_at': print_date(self.created_at),
            'last_accessed_at': print_date(self.last_accessed_at),
            'value': self.value,
        }
