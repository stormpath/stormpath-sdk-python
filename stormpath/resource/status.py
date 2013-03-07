__author__ = 'ecrisostomo'

class Status:
    def __init__(self):
        self.value = str(self)

class Enabled(Status):
    def __repr__(self):
        return "ENABLED"

class Disabled(Status):
    def __repr__(self):
        return "DISABLED"

enabled, disabled = Enabled(), Disabled()

status_dict = {enabled.value : enabled, disabled.value : disabled}
