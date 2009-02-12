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
    void setParam(string key, string value);
    void unsetParam(string key);
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

interface Subnet {
    string id();
    string decl();
    IpRange range(RangeType type);
    void setRange(RangeType type, IpRange range);
    StrStrMap params();
    void setParam(string key, string value);
    void unsetParam(string key);
};

sequence<Subnet*> SubnetSeq;

interface Server {
    SubnetSeq subnets();
    Subnet* findSubnet(string decl);
    Subnet* addSubnet(string decl);
    void delSubnet(Subnet* s);
    HostSeq hosts();
    HostSeq hostsByNames(StrSeq names);
    Host* addHost(string name, HostId id);
    void delHosts(HostSeq hosts);
    StrStrMap params();
    void setParam(string key, string value);
    void unsetParam(string key);
    void commit();
    void reset();
};

interface Daemon {
    void start();
    void stop();
    bool running();
};

};
}; };
