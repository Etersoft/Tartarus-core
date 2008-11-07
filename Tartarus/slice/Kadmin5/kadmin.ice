
#ifndef TARTARUS_IFACE_KADMIN5_KADMIN_ICE
#define TARTARUS_IFACE_KADMIN5_KADMIN_ICE

#include <core/exceptions.ice>

module Tartarus { module iface {

module Kadmin5 {

exception KadminError extends core::DBError
{
    int code;
};

sequence<byte> KeyData;
sequence<string> PrincSeq;

struct Key
{
    // krb5_kvno is in fact uint32_t.
    long kvno;

    // krb5_enctype is int32_t
    int enctype;

    KeyData data;
};

sequence<Key> KeySeq;

struct PrincKeys
{
    string name;
    KeySeq keys;
};

interface Kadmin
{
    PrincKeys getPrincKeys(string name)
        throws core::Error;

    PrincKeys createServicePrincipal(string service, string host)
        throws core::Error;

    string createPrincipal(string name, string password)
        throws core::Error;

    string changePrincPassword(string  name, string password)
        throws core::Error;

    void deletePrincipal(string name)
        throws core::Error;

    PrincSeq listPrincs(string expr)
        throws core::Error;

    PrincSeq listAllPrincs()
        throws core::Error;

    bool isPrincEnabled(string name)
        throws core::Error;

    void setPrincEnabled(string name, bool enable)
        throws core::Error;

    void reGenerateDatabase(string password)
        throws core::Error;
};
};

}; };

#endif // TARTARUS_IFACE_KADMIN5_KADMIN_ICE

