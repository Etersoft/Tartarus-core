import enum

class Enum(enum.Enum):
    def __init__(self, *args, **kwargs):
        enum.Enum.__init__(self, *args, **kwargs)
    def __setattr__(self, attr, value):
        object.__setattr__(self, attr, value)

