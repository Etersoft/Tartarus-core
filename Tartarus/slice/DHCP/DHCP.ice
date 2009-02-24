#include <core/exceptions.ice>

module Tartarus { module iface {
module DHCP {

sequence<string> StrSeq;

enum HostIdType {
    IDENTITY,
    HARDWARE
};

struct HostId {
    HostIdType type;
    string value;
};

dictionary<string,string> StrStrMap;

interface Host {
    string name();
    HostId id();
    StrStrMap params();
    void setParam(string key, string value) throws core::Error;
    void unsetParam(string key) throws core::Error;
};

sequence<Host*> HostSeq;

enum RangeType {
    STATIC,
    TRUST,
    UNTRUST
};

struct IpRange {
    string start;
    string end;
    bool hasValue;
};

interface Range {
    string id();
    RangeType type();
    string addrs(out string start, out string end);
    StrStrMap params();
    void setParam(string key, string value) throws core::Error;
    void unsetParam(string key) throws core::Error;
};

sequence<Range*> RangeSeq;

interface Subnet {
    string id();
    string decl();
    //IpRange range(RangeType type);
    void setRange(RangeType type, IpRange range) throws core::Error;
    StrStrMap params();
    void setParam(string key, string value) throws core::Error;
    void unsetParam(string key) throws core::Error;
    RangeSeq ranges();
    Range* findRange(string ip) throws core::Error;
    Range* addRange(string start, string end) throws core::Error;
    void delRange(string ip) throws core::Error;
};

sequence<Subnet*> SubnetSeq;

interface Server {
    SubnetSeq subnets();
    Subnet* findSubnet(string decl) throws core::Error;
    Subnet* addSubnet(string decl) throws core::Error;
    void delSubnet(Subnet* s) throws core::Error;
    HostSeq hosts();
    HostSeq hostsByNames(StrSeq names);
    Host* addHost(string name, HostId id) throws core::Error;
    void delHosts(HostSeq hosts) throws core::Error;
    StrStrMap params();
    void setParam(string key, string value) throws core::Error;
    void unsetParam(string key) throws core::Error;
    void commit() throws core::Error;
    void reset() throws core::Error;
};

interface Daemon {
    void start() throws core::Error;
    void stop() throws core::Error;
    bool running();
};

exception DHCPKeyError extends core::Error
{
    string key;
};

exception DHCPValueError extends core::Error
{
    string key;
    string value;
};

};
}; };
