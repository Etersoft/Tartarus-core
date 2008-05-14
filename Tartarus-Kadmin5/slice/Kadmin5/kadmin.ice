
module Tartarus { module iface

module Kerberos5 {

exception KerberosException
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

interface Kadmin5
{
    PrincKeys getPrincKeys(string name)
        throws KerberosException;

    PrincKeys createServicePrincipal(string service, string host)
        throws KerberosException;

    string createPrincipal(string name, string password)
        throws KerberosException;

    string changePrincPassword(string  name, string password)
        throws KerberosException;

    void deletePrincipal(string name)
        throws KerberosException;

    PrincSeq listPrincs(string expr)
        throws KerberosException;

    PrincSeq listAllPrincs()
        throws KerberosException;
};

};

}; };

