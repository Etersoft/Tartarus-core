
#ifndef TARTARUS_IFACE_CORE_EXCEPTIONS_ICE
#define TARTARUS_IFACE_CORE_EXCEPTIONS_ICE

module Tartarus { module iface {

module core {

exception Error
{
    string reason;
};

exception ConfigError extends Error
{
    string property;
};


exception ValueError extends Error
{
    string value;
};

exception DBError extends Error
{
    string response;
};

exception NotFoundError extends DBError
{
};

exception AlreadyExistsError extends DBError
{
};

exception InternalError extends DBError
{
};

exception PermissionError extends Error
{
    string operation;
    string agent;
};

exception RuntimeError extends Error
{
};

}; // module core

};};

#endif //TARTARUS_IFACE_CORE_EXCEPTIONS_ICE

