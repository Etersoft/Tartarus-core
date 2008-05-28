
module Tartarus { module iface {

module Kadmin5 {

exception KadminException
{
    int code;
    string where;
    string what;
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
        throws KadminException;

    PrincKeys createServicePrincipal(string service, string host)
        throws KadminException;

    string createPrincipal(string name, string password)
        throws KadminException;

    string changePrincPassword(string  name, string password)
        throws KadminException;

    void deletePrincipal(string name)
        throws KadminException;

    PrincSeq listPrincs(string expr)
        throws KadminException;

    PrincSeq listAllPrincs()
        throws KadminException;
};

};

}; };

