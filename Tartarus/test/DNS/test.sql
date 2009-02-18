BEGIN TRANSACTION;
CREATE TABLE domains (
    id                INTEGER PRIMARY KEY,
    name              VARCHAR(255) NOT NULL,
    master            VARCHAR(128) DEFAULT NULL,
    last_check        INTEGER DEFAULT NULL,
    type              VARCHAR(6) NOT NULL,
    notified_serial   INTEGER DEFAULT NULL,
    account           VARCHAR(40) DEFAULT NULL
);
INSERT INTO domains VALUES(1,'localhost',NULL,NULL,'NATIVE',NULL,NULL);
INSERT INTO domains VALUES(2,'127.in-addr.arpa',NULL,NULL,'NATIVE',NULL,NULL);
INSERT INTO domains VALUES(3,'localdomain',NULL,NULL,'NATIVE',NULL,NULL);
INSERT INTO domains VALUES(4,'0.in-addr.arpa',NULL,NULL,'NATIVE',NULL,NULL);
INSERT INTO domains VALUES(5,'255.in-addr.arpa',NULL,NULL,'NATIVE',NULL,NULL);
INSERT INTO domains VALUES(6,'saratov.etersoft.ru',NULL,NULL,'NATIVE',NULL,NULL);
INSERT INTO domains VALUES(7,'33.168.192.in-addr.arpa',NULL,NULL,'NATIVE',NULL,NULL);
CREATE TABLE records (
    id              INTEGER PRIMARY KEY,
    domain_id       INTEGER DEFAULT NULL,
    name            VARCHAR(255) DEFAULT NULL,
    type            VARCHAR(6) DEFAULT NULL,
    content         VARCHAR(255) DEFAULT NULL,
    ttl             INTEGER DEFAULT NULL,
    prio            INTEGER DEFAULT NULL,
    change_date     INTEGER DEFAULT NULL
);
INSERT INTO records VALUES(1,1,'localhost','SOA','localhost root.localhost 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(2,1,'localhost','NS','localhost',NULL,NULL,NULL);
INSERT INTO records VALUES(3,1,'localhost','A','127.0.0.1',NULL,NULL,NULL);
INSERT INTO records VALUES(4,2,'127.in-addr.arpa','SOA','localhost root.localhost 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(5,2,'127.in-addr.arpa','NS','localhost',NULL,NULL,NULL);
INSERT INTO records VALUES(6,2,'1.0.0.127.in-addr.arpa','PTR','localhost',NULL,NULL,NULL);
INSERT INTO records VALUES(7,2,'0.0.0.127.in-addr.arpa','PTR','localdomain',NULL,NULL,NULL);
INSERT INTO records VALUES(8,3,'localdomain','SOA','localhost root.localhost 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(9,3,'localdomain','NS','localhost',NULL,0,NULL);
INSERT INTO records VALUES(10,3,'localdomain','A','127.0.0.0',NULL,0,NULL);
INSERT INTO records VALUES(11,3,'localhost.localdomain','CNAME','localhost',NULL,0,NULL);
INSERT INTO records VALUES(12,4,'0.in-addr.arpa','SOA','localhost root.localhost 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(13,4,'127.in-addr.arpa','NS','localhost',NULL,NULL,NULL);
INSERT INTO records VALUES(14,5,'255.in-addr.arpa','SOA','localhost root.localhost 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(15,5,'127.in-addr.arpa','NS','localhost',NULL,NULL,NULL);
INSERT INTO records VALUES(16,6,'saratov.etersoft.ru','SOA','ns.saratov.etersoft.ru admin.saratov.etersoft.ru 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(17,6,'saratov.etersoft.ru','NS','ns.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(18,6,'saratov.etersoft.ru','A','192.168.33.15',NULL,NULL,NULL);
INSERT INTO records VALUES(19,6,'kerberos.saratov.etersoft.ru','CNAME','tartarus.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(20,6,'_kerberos._udp.saratov.etersoft.ru','SRV','0 88 kerberos.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(21,6,'_kerberos._tcp.saratov.etersoft.ru','SRV','0 88 kerberos.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(22,6,'_kpasswd._udp.saratov.etersoft.ru','SRV','0 464 kerberos.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(23,6,'_kerberos-adm._tcp.saratov.etersoft.ru','SRV','0 749 kerberos.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(24,6,'_kerberos.saratov.etersoft.ru','TXT','SARATOV.ETERSOFT.RU',NULL,NULL,NULL);
INSERT INTO records VALUES(25,6,'tartarus.saratov.etersoft.ru','A','192.168.33.15',NULL,0,NULL);
INSERT INTO records VALUES(26,6,'ns.saratov.etersoft.ru','CNAME','tartarus.saratov.etersoft.ru',NULL,0,NULL);
INSERT INTO records VALUES(27,7,'33.168.192.in-addr.arpa','SOA','ns.saratov.etersoft.ru admin.saratov.etersoft.ru 0 43200 3600 604800 3600',NULL,NULL,NULL);
INSERT INTO records VALUES(28,7,'33.168.192.in-addr.arpa','NS','ns.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(29,7,'15.33.168.192.in-addr.arpa','PTR','tartarus.saratov.etersoft.ru',NULL,NULL,NULL);
INSERT INTO records VALUES(30,6,'tclient.saratov.etersoft.ru','A','192.168.33.238',NULL,NULL,NULL);
INSERT INTO records VALUES(31,7,'238.33.168.192.in-addr.arpa','PTR','tclient.saratov.etersoft.ru',NULL,NULL,NULL);
CREATE TABLE supermasters (
    ip          VARCHAR(25) NOT NULL,
    nameserver  VARCHAR(255) NOT NULL,
    account     VARCHAR(40) DEFAULT NULL
);
CREATE UNIQUE INDEX name_index ON domains(name);
CREATE INDEX rec_name_index ON records(name);
CREATE INDEX nametype_index ON records(name,type);
CREATE INDEX domain_id ON records(domain_id);
COMMIT;

