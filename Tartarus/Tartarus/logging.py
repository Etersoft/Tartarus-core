"""Logging facilities for Tartarus.

Module Tartarus.logging provides logging facilities for Tartarus. Three
functions are defined here:
    error(...) -- for logging error messages
    warning(...) -- for warning messages
    trace(...) -- for debug and informational messages.

Some simple exaples:

>>> from Tartarus import logging
>>> logging.error("I'm bored with the documentation")
05/13/08 19:32:07.533 error: I'm bored with the documentation
>>> logging.warning("My brain will explode soon!")
05/13/08 19:34:17.702 warning: My brain will explode soon!
>>> logging.trace("LOOK", "Previous examples were stupid")
[ 05/13/08 19:35:39.841 LOOK: Previous examples were stupid ]

The following messages will not be logged:

>>> logging.trace("DON'T", "REALY STRANGE MESSAGE", 2*2 == 42)
>>> logging.error("Actually, no error", None)
>>> 

If you have Ice communicator comm, and you want to issue a warning
with it's logger iff a property "MyApp.IssueWarnings" is set to a positive
integer, you can do it as follows:

>>> logging.warning("Beware of unnecessary warnings",
...     cond="MyApp.IssueWarnings", log_to=comm)

If instead you want to issue a warning if the property value is greater or
equal, say, 42, you shold have passed cond=("MyApp.IssueWarnings", 42).

Internally Ice logging is used.

First parameter of all functions is a message to log (a string),
except trace(...) function, which first parameter is a message category
(also a string), and message is the second parameter.

After the message, two keyword parameters might be specified:
    cond -- which determines whether message should be logged or ignored;
        default is True;
    log_to -- an object which determines a logger to write to.

For log_to parameter the following values are possible:
    None -- the default, the process logger (as returned by
        Ice.getProcessLogger())  will be used
    an instance of Ice.Logger -- it will be used
    an instance of Ice.Communicator -- logger returned by it's
        getLogger() will be used
    an Ice.Current structure -- a logger of of communicator current
        object adapter will be used.

You can use the following objects as conditions:
    object of integer types or None:
        message is logged if cond evaluates to True
    A string:
        if log_to object is an instance of Ice.Communicator or
        Ice.Current, cond parameter defines an Ice property name. This
        property should have integer value. The message is logged if
        this value is positive.
    A 2-tuple (string, number):
        if log_to object is an instance of Ice.Communicator or
        Ice.Current, string defines an Ice property name. This property
        should have an integer value. The message is logged if this
        value is greater or equal to second tuple element.

If you provide bad log_to or cond values, exception of type TypeError
is raised.
"""

import Ice

def _logger_from_communicator(comm, cond):
    """Private function for internal use."""
    do_log = False
    if type(cond) in [bool, int, long, type(None)]:
        do_log = bool(cond)
    elif (type(cond) is tuple and len(cond) == 2 and type(cond[0]) is str):
        i = comm.getProperties().getPropertyAsInt(cond[0])
        do_log = cond[1] <= i
    elif type(cond) is str:
        i = comm.getProperties().getPropertyAsInt(cond)
        do_log = i > 0
    else:
        raise TypeError,\
                "Could not determine logging condition form object %s" % obj

    if (do_log):
        return comm.getLogger()
    else:
        return None


def _logger(obj, cond):
    """Private function for internal use."""
    if obj is None:
        if cond:
            return Ice.getProcessLogger()
        else:
            return None
    elif isinstance(obj, Ice.Logger):
        if cond:
            return obj
        else:
            return None
    elif isinstance(obj, Ice.Communicator):
        _logger_from_communicator(obj, cond)
    elif isinstance(obj, Ice.Current):
        _logger_from_communicator(obj.adapter.getCommunicator(), cond)
    else:
        raise TypeError, "Could not get logger from object %s" % obj



def error(msg, cond = True, log_to = None):
    """Log an error message."""
    log = _logger(log_to, cond)
    if (log):
        log.error(msg)


def warning(msg, cond = True, log_to = None):
    """Log a warning message."""
    log = _logger(log_to, cond)
    if (log):
        log.warning(msg)


def trace(category, msg, cond = True, log_to = None):
    """Log debug or informational message"""
    log = _logger(log_to, cond)
    if (log):
        log.trace(category, msg)

