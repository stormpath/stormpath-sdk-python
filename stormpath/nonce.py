class Nonce(object):
    def __init__(self, value):
        self.value = value
        # we fake the href to comply with what the data store expects
        self.href = '//nonces/%s' % value
