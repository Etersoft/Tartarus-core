#ifndef TARTARUS_DNS_ICE
#define TARTARUS_DNS_ICE

module Tartarus { module iface {

module DNS
{


module Errors
{
    exception Basic
    {
        string reason;
    };

    exception ObjectNotFound extends Basic
    {
    };

    exception AlreadyExists extends Basic
    {
    };

    exception ValueError extends Basic
    {
        string value;
    };

    exception ConfigError extends Basic
    {
        string property;
    };
};

enum RecordType
{
    A ,    //The A record contains an IP address.
           //It is stored as a decimal dotted quad string
           //for example: '213.244.168.210'.
    AAAA,  //The AAAA record contains an IPv6 address.
           //An example: '3ffe:8114:2000:bf0::1'.
    AFSDB, //Specialised record type for the 'Andrew Filesystem'.
           //Stored as: '#subtype hostname', where subtype is a number.
    CERT,  //Specialised record type for storing certificates (RFC 2538).
    CNAME, //The CNAME record specifies the canonical name of a record.
           //It is stored plainly. Like all other records, it is
           //not terminated by a dot. A sample might be
           //'webserver-01.yourcompany.com'.
    DNSKEY,//The DNSKEY DNSSEC record type, as described in RFC 3757.
    DS,    //The DS DNSSEC record type, as described in RFC 3757.
    HINFO, //Hardware Info record, used to specify CPU and OS.
           //Stored with a single space separating these two,
           //example: 'i386 Linux'.
    KEY,   //The KEY record (see RFC 2535).
    LOC,   //The LOC record (see RFC 1876).
    MX,    //The MX record specifies a mail exchanger host for a domain.
           //Each mail exchanger also has a priority or preference.
           //This should be specified in the separate field, 'prio'.
    NAPTR, //Naming Authority Pointer, RFC 2915.
    NS,    //Nameserver record. Specifies nameservers for a domain.
           //Stored plainly: 'ns1.tartarus.ru', without a terminating dot.
    NSEC,  //The NSEC DNSSEC record type, as described in RFC 3757.
    PTR,   //Reverse pointer, used to specify the host name belonging to
           //an IP or IPv6 address. Stored plainly, no terminating dot.
    RP,    //Responsible Person record, as described in RFC 1183.
           //Stored with a single space between the mailbox name and the
           //more-information pointer.
           //Example 'iv.tartarus.ru iv.people.tartarus.ru',
    RRSIG, //The RRSIG DNSSEC record type, as described in RFC 3757.
    SPF,   //SPF records can be used to store Sender Permitted From details.
    SSHFP, //The SSHFP record type, used for storing Secure Shell (SSH)
           //fingerprints. A sample from RFC 4255 is:
           //'2 1 123456789abcdef67890123456789abcdef67890'.
    SRV,   //SRV records can be used to encode the location and port
           //of services on a domain name. When encoding, the priority
           //field is used to encode the priority. For example,
           //'_ldap._tcp.dc._msdcs.conaxis.ch SRV 0 100 389 mars.conaxis.ch'
           //would be encoded with 0 in the priority field and
           //'100 389 mars.conaxis.ch' in the content field.
    TXT    //The TXT field can be used to attach textual data to a domain.
           //Text is stored plainly.
    // SOA record type is supported by other means.
};

struct Record
{
    string name;
    RecordType type;
    string content;
    long ttl;
    long prio; // not really used
};
sequence<Record> RecordSeq;


struct SOARecord
{
    string primary;
    string hostmaster;
    long serial;
    long refresh;
    long retry;
    long expire;
    long defaultTtl;
};

interface Domain
{
    void addRecord(Record r) throws Errors::Basic;
    void addRecords(RecordSeq rs) throws Errors::Basic;
    idempotent void clearAll() throws Errors::Basic;
    void dropRecord(string name, RecordType type) throws Errors::Basic;

    RecordSeq getRecords(long offset, long limit) throws Errors::Basic;
    long countRecords() throws Errors::Basic;
    RecordSeq findRecords(string phrase, long limit) throws Errors::Basic;

    idempotent SOARecord getSOA() throws Errors::Basic;
    idempotent void setSOA(SOARecord soar) throws Errors::Basic;
};
sequence<Domain*> DomainSeq;


struct ServerOption
{
    string name;
    string value;
};
sequence<ServerOption> ServerOptionSeq;

interface Server
{
    idempotent DomainSeq getDomains() throws Errors::Basic;
    idempotent Domain* getDomain(string name) throws Errors::Basic;
    Domain* createDomain(string name) throws Errors::Basic;
    void deleteDomain(string name) throws Errors::Basic;
    void deleteDomainByRef(Domain* proxy) throws Errors::Basic;

    idempotent ServerOptionSeq getOptions() throws Errors::Basic;
    idempotent void setOptions(ServerOptionSeq opts) throws Errors::Basic;
    idempotent void setOption(ServerOption opt) throws Errors::Basic;
};


};// module DNS


};};

#endif //TARTARUS_DNS_ICE

