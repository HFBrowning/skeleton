import arcpy


class ArcpyLog(object):
    """Wrap Arcpy GetMessage() with the Standard logger.

    This class simply wraps the module level logger and logging level to allow
    passing of arcpy messages to the same log file.

    Attributes
    ----------
    log_level: str
        Logging severity conformant to standard logging
    log_object: logging object
        Standard logging object instance


    Example
    -------
    .. code-block:: python

        # This code block commented because it is for example purposes only (should not be run)

        # alog = ArcpyLog("DEBUG", log_object=logger)
        # arcpy.CopyFeatures(in_fc, out_fc)
        # alog.log()

    """
    def __init__(self, log_object, log_level):
        """
        Parameters
        ----------
        log_object: logging object
            Module level logger
        log_level: str
            Logging severity conformant to standard logging
        """
        self.log_object = log_object
        self.log_level = log_level

    def log(self):
        """Pass an arcpy message to log file.
        """
        # A bit redundant here but not sure what to do about it
        if self.log_level in ('DEBUG', 'INFO'):
            text = arcpy.GetMessages(0)
            if len(text) > 0:
                self.log_object.info(text)
        if self.log_level == 'WARNING':
            text = arcpy.GetMessages(1)
            if len(text) > 0:
                self.log_object.warning(text)
        if self.log_level in ('ERROR', 'CRITICAL'):
            text = arcpy.GetMessage(2)
            if len(text) > 0:
                self.log_object.error(text)
