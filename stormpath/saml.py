class SamlCallbackResult(object):
    def __init__(self, account, state, status):
        self.account = account
        self.state = state
        self.status = status
