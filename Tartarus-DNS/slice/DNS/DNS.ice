#ifndef TARTARUS_DNS_ICE
#define TARTARUS_DNS_ICE

module Tartarus { module iface {

module DNS
{


exception Error
{
    string message;
};

exception DBError extends Error
{
    string response;
};

exception ObjectNotFound extends DBError
{
};

exception ValueError extends Error
{
    string value;
};

exception ConfigError extends Error
{
    string property;
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
    string data;
    long ttl;
    long prio;
};
sequence<Record> RecordSeq;


struct SOARecord
{
    string nameserver;
    string hostmaster;
    long serial;
    long refresh;
    long retry;
    long expire;
    long ttl;
};

interface Zone
{
    idempotent string getName() throws Error;

    void addRecord(Record r) throws Error;
    void addRecords(RecordSeq rs) throws Error;
    idempotent void clearAll() throws Error;
    void dropRecord(Record r) throws Error;

    long countRecords() throws Error;
    RecordSeq getRecords(long limit, long offset) throws Error;
    RecordSeq findRecords(string phrase, long limit) throws Error;

    idempotent SOARecord getSOA() throws Error;
    idempotent void setSOA(SOARecord soar) throws Error;
};
sequence<Zone*> ZoneSeq;

struct ServerOption
{
    string name;
    string value;
};
sequence<ServerOption> ServerOptionSeq;

interface Server
{
    idempotent ZoneSeq getZones() throws Error;
    idempotent Zone* getZone(string name) throws Error;
    Zone* createZone(string name, SOARecord soar) throws Error;
    void deleteZone(string name) throws Error;
    void deleteZoneByRef(Zone* proxy) throws Error;

    idempotent ServerOptionSeq getOptions() throws Error;
    void setOptions(ServerOptionSeq opts) throws Error;
    void changeOptions(ServerOptionSeq opts) throws Error;

    //called once on deployment:
    void initNewDatabaseUnsafe(ServerOptionSeq opts) throws Error;
};


};// module DNS


};};

#endif //TARTARUS_DNS_ICE

