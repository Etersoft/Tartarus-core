import os
import tpg

class Krb5Conf:
    def __init__(self):
        self.__sections = CfgReader()(file('/etc/krb5.conf').read())
    def setDefaultRealm(self, realm):
        d = self.__sections.section('libdefaults')
        d.setTag('default_realm', realm)
    def defaultRealm(self):
        d = self.__sections.section('libdefaults')
        return d.tag('default_realm')
    def setRealmDomain(self, realm, domain):
        s = self.__sections.section('domain_realm')
        s.setTag(domain, realm)
        s.setTag('.' + domain, realm)
    def setRealm(self, realm, kdc, kadmin=None):
        s = self.__sections.section('realms')
        val = Subsection()
        val.setTag('kdc', kdc)
        val.setTag('admin_server', kadmin or kdc)
        s.setTag(realm, val)
    def realms(self):
        s = self.__sections.section('realms')
        for realm, opts in s.tags():
            yield (realm, opts.tag('kdc'), opts.tag('admin_server'))
    def setLookup(self, val=True):
        s = self.__sections.section('libdefaults')
        val = 'true' if val else 'false'
        s.setTag('dns_lookup_realm', val)
        s.setTag('dns_lookup_kdc', val)
    def lookup(self):
        s = self.__sections.section('libdefaults')
        return (s.tag('dns_lookup_realm') == 'true'
                and s.tag('dns_lookup_kdc') == 'true')
    def setPamConfig(self):
        appdef_sec = self.__sections.section('appdefaults')
        pam_sec = appdef_sec.tag('pam')
        if not isinstance(pam_sec, Subsection):
            pam_sec = Subsection()
        pam_sec.setTag('retain_after_close', 'yes')
        pam_sec.setTag('ccache', '/tmp/krb5cc_%u')
        appdef_sec.setTag('pam', pam_sec)
    def save(self):
        open('/etc/krb5.conf.new', 'w+').write(str(self.__sections))
        os.rename('/etc/krb5.conf.new', '/etc/krb5.conf')

class Sections:
    def __init__(self):
        self.__sections = {}
    def sections(self):
        return self.__sections.itervalues()
    def section(self, name):
        if name in self.__sections:
            return self.__sections[name]
        s = Section(name)
        self.addSection(s)
        return s
    def addSection(self, section):
        self.__sections[section.name()] = section
    def delSection(self, name):
        del self.__section[name]
    def __str__(self):
        return ''.join((str(s) for s in self.sections()))

class Tags:
    def __init__(self):
        self.__tags = {}
    def tag(self, name):
        return self.__tags.get(name, None)
    def tags(self):
        return self.__tags.iteritems()
    def setTag(self, name, value):
        self.__tags[name] = value
    def unsetTag(self, name):
        del self.__tags[name]

class Section(Tags):
    def __init__(self, name):
        Tags.__init__(self)
        self.__name = name
    def name(self):
        return self.__name
    def __str__(self):
        ret = []
        push = ret.append
        push('[%s]\n' % self.__name)
        for tname, tval in self.tags():
            push('  %s = %s\n' % (tname, tval))
        push('\n')
        return ''.join(ret)

class Subsection(Tags):
    def __init__(self):
        Tags.__init__(self)
    def __str__(self):
        ret = []
        push = ret.append
        push('{\n')
        for i in self.tags():
            push('    %s = %s\n' % i)
        push('  }')
        return ''.join(ret)

class CfgReader(tpg.Parser):
    r'''
    separator spaces    '\s';
    separator comment   '#.*?\n';

    token word   '[\w:./%]+';

    START / sections ->                     $ sections = Sections()
        ( SECTION/section                   $ sections.addSection(section)
        )*
        ;

    SECTION / section ->
        '\[' word/sname '\]'                $ section = Section(sname)
        ( word/tname '=' TAGVALUE/tval      $ section.setTag(tname, tval)
        )*
        ;
    TAGVALUE / value ->
        word/value
        | (
        '{'                                 $ value = Subsection()
        ( word/tname '=' TAGVALUE/tval      $ value.setTag(tname, tval)
        )*
        '}'
        )
        ;
    '''

