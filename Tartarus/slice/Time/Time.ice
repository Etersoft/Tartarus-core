
#ifndef TARTARUS_IFACE_TIME_ICE
#define TARTARUS_IFACE_TIME_ICE

#include <core/exceptions.ice>

module Tartarus { module iface {

module Time {

exception TimeError extends core::Error
{
};

struct tm
{
    int sec;
    int min;
    int hour;
    int mday;
    int mon;
    int year;
    int wday;
    int yday;
    int isdst;
};

interface Server
{
    tm getGMTime()
        throws core::Error;

    tm getLocalTime()
        throws core::Error;

    int getTime()
        throws core::Error;
};
};

}; };

#endif // TARTARUS_IFACE_TIME_ICE

