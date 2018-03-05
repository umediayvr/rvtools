from .RvContext import RvContext
from basetools.App import Hook

class RvHook(Hook):
    """
    Hook implementation for rv.
    """

    def startup(self):
        """
        Perform startup routines.
        """
        super(RvHook, self).startup()


# registering hook
Hook.register(
    'rv',
    RvHook,
    RvContext
)
