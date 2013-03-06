__author__ = 'ecrisostomo'

class Status:
    pass

class Enabled(Status):
    def __repr__(self):
        return "ENABLED"

class Disabled(Status):
    def __repr__(self):
        return "DISABLED"

enabled = Enabled()
disabled = Disabled()
