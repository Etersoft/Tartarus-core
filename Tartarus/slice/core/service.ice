
#ifndef TARTARUS_IFACE_CORE_SERVICE_ICE
#define TARTARUS_IFACE_CORE_SERVICE_ICE

#include <core/exceptions.ice>

module Tartarus { module iface {

module core
{

dictionary <string, string> OptionsDict;

interface Service
{
    idempotent string getName();
    idempotent bool isConfigured();
    void configure(OptionsDict opts) throws Error;
};

sequence <Service*> ServiceSeq;

}; //module core

};};

#endif // TARTARUS_IFACE_CORE_SERVICE_ICE

