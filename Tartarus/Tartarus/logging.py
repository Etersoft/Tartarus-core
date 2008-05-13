
import Ice

def _logger_from_communicator(comm, cond):
    do_log = False
    if type(cond) in [bool, int, long, type(None)]:
        do_log = bool(cond)
    elif (type(cond) == tuple and len(cond) == 2 and type(cond[0]) == str):
        i = comm.getProperties().getPropertyAsInt(cond[0])
        do_log = cond[1] <= i
    elif type(cond) == str:
        i = comm.getProperties().getPropertyAsInt(cond)
        do_log = i > 0
    else:
        raise TypeError,\
                "Could not determine logging condition form object %s", %obj

    if (do_log):
        return comm.getLogger()
    else:
        return None


def _logger(obj, cond):
    if obj == None:
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

def error(msg, cond = True, log_to = Ice.getProcessLogger() ):
    log = _logger(log_to, cond)
    if (log):
        log.error(msg)


def warning(msg, cond = True, log_to = Ice.getProcessLogger() ):
    log = _logger(log_to, cond)
    if (log):
        log.warning(msg)


def trace(category, msg, cond = True, log_to = Ice.getProcessLogger() ):
    log = _logger(log_to, cond)
    if (log):
        log.trace(category, msg)




