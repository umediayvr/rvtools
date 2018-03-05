from basetools.App import Context, ContextFileNameError

class RvContext(Context):
    """
    Context implementation for rv.
    """

    @classmethod
    def fileName(cls):
        """
        Return a string about current file path of the opened file.

        In case the file is not saved, then raise the exception ContextFileNameError.
        """
        raise ContextFileNameError(
            "Could not figure out scene name"
        )

    @classmethod
    def isEmpty(cls):
        """
        Return a boolean telling if the scene has never been saved.
        """
        return True

    @classmethod
    def hasModification(cls):
        """
        Return a boolean telling if the scene has modifications.

        This is used to decide if the scene needs to be saved.
        """
        return False

    @classmethod
    def hasGUI(cls):
        """
        Return a boolean telling if application is running with through GUI.
        """
        return True
