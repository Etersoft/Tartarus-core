
Version: 0.8.2
Release: alt1

%define tname Tartarus

Summary: %tname Core components
Name: %tname-core
Source: %tname-%version.tar
License: %gpl2plus
Group: System/Configuration/Other
Url: http://www.tartarus.ru
Packager: Ivan A. Melnikov <iv@altlinux.org>

BuildRequires(pre): rpm-build-licenses, rpm-build-python

BuildRequires: python-devel gcc-c++ ice-devel-utils libice-devel

%description
Core components for %tname.

# {{{1 Utility

%package -n %tname-common
Summary: Common files for %tname
Group: System/Configuration/Other

%description -n %tname-common
Common files required by most of %tname modules.


%package -n %tname-srv1
Summary: %tname python service loader
Group: System/Servers
Provides: %tname = %version-%release
Requires: %tname-common = %version-%release
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-daemon = %version-%release

%description -n %tname-srv1
%tname python service loader

%package -n %tname-deploy-srv
Summary: %tname server deployment utility
Group: System/Configuration/Other
Requires: %tname-leave = %version-%release
Requires: %tname-common = %version-%release
Requires: %tname = %version-%release
Requires: %tname-DNS = %version-%release
Requires: %tname-Kadmin5 = %version-%release
Requires: %tname-SysDB = %version-%release
Requires: %tname-DNS-slice = %version-%release
Requires: %tname-Kerberos-slice = %version-%release
Requires: %tname-SysDB-slice = %version-%release
Requires: python-module-dnet
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-deploy = %version-%release
Requires: python-module-%tname-system = %version-%release
Requires: libnss-tartarus, krb5-kinit, pam_krb5

%description -n %tname-deploy-srv
%tname-deploy-srv is a simple console utility which will help you to create
inital configuration for Tartarus server.


%package -n %tname-join
Summary: Tartarus client deployment
Group: System/Configuration/Other
Requires: %tname-leave = %version-%release
Requires: %tname-common = %version-%release
Requires: %tname-Kerberos-slice = %version-%release
Requires: %tname-SysDB-slice = %version-%release
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-deploy = %version-%release
Requires: python-module-%tname-system = %version-%release
Requires: %tname-dnsupdate >= 0.1.0
Requires: libnss-tartarus, krb5-kinit, pam_krb5, nscd

%description -n %tname-join
Tartarus client deployment.

%package -n %tname-leave
Summary: Tartarus client leave
Group: System/Configuration/Other
Requires: %tname-common = %version-%release
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-deploy = %version-%release
Requires: python-module-%tname-system = %version-%release

%description -n %tname-leave
Tartarus client leave.


# {{{1 Internal modules

%package -n python-module-%tname
Summary: Core components of %tname for Python.
Group: Development/Python

%description -n python-module-%tname
Core components of %tname for Python.

This module is built for python %__python_version


%package -n python-module-%tname-daemon
Summary: Daemonization support for %tname.
Group: Development/Python
Requires: python-module-%tname = %version-%release

%description -n python-module-%tname-daemon
Daemonization support for %tname.

This module is built for python %__python_version


%package -n python-module-%tname-system
Summary: System tools for %tname.
Group: Development/Python
Requires: python-module-%tname = %version-%release
Requires: python-module-kadmin5

%description -n python-module-%tname-system
System tools for %tname.

This module is built for python %__python_version


%package -n python-module-%tname-db
Summary: Database support for %tname.
Group: Development/Python
Requires: python-module-%tname = %version-%release

%description -n python-module-%tname-db
Database support for %tname.

This module is built for python %__python_version


%package -n python-module-%tname-deploy
Summary: %tname deployment internals.
Group: Development/Python
Requires: python-module-%tname = %version-%release

%description -n python-module-%tname-deploy
%tname deployment internals.

This module is built for python %__python_version


# {{{1 Configurators

%package -n %tname-DNS
Summary: %tname DNS Configurator.
Group: System/Configuration/Other
Requires: python%__python_version(sqlite)
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-db = %version-%release
Requires: %tname = %version-%release
Requires: pdns-backend-sqlite3

%description -n %tname-DNS
%tname DNS Configurator.

This module is built for python %__python_version


%package -n %tname-Kadmin5
Summary: %tname Kadmin5 Configurator.
Group: System/Configuration/Other
Requires: python-module-%tname = %version-%release
Requires: python-module-kadmin5 >= 0.0.5
Requires: %tname = %version-%release
Requires: krb5-kdc

%description -n %tname-Kadmin5
%tname Kadmin5 Configurator.

This module is built for python %__python_version


%package -n %tname-SysDB
Summary: %tname SysDB service.
Group: System/Servers
Requires: python%__python_version(sqlite3)
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-db = %version-%release
Requires: %tname = %version-%release

%description -n %tname-SysDB
%tname SysDB service.

This module is built for python %__python_version


# {{{1 Slices

%package -n %tname-core-slice
Summary: Interface defenision files for %tname core objects.
Group: Development/Other

%description -n %tname-core-slice
Interface defenision files for %tname core objects.


%package -n %tname-Kerberos-slice
Summary: Interface defenision files for Kerberos %tname.
Group: Development/Other
Requires: %tname-core-slice = %version-%release

%description -n %tname-Kerberos-slice
Interface defenision files for %tname core objects.


%package -n %tname-DNS-slice
Summary: Interface defenision files for %tname core objects.
Group: Development/Other
Requires: %tname-core-slice = %version-%release

%description -n %tname-DNS-slice
Interface defenision files for %tname core objects.

%package -n %tname-SysDB-slice
Summary: Interface defenision files for %tname core objects.
Group: Development/Other
Requires: %tname-core-slice = %version-%release

%description -n %tname-SysDB-slice
Interface defenision files for %tname core objects.


# {{{1 prep

%prep
%define tconfdir %_sysconfdir/%tname
%define tmoduledir %_libdir/%tname/modules
%define tslicedir %_datadir/%tname/slice
%define ttemplatedir %_datadir/%tname/templates
%define tpythondir %python_sitelibdir/%tname

%setup  -q -n %tname-%version

%build
# check version
if [ "%version" != "`./waf --package-version`" ]; then
    echo RPM and package versions are not equal
    exit 1
fi

./configure
./waf

# {{{1 install

%install
./waf install --destdir=%buildroot

# {{{1 triggers

%preun -n %tname-leave
if [ "$1" = "0" ]; then
    Tartarus-leave -f
fi


# {{{1 files

%files -n %tname-common
%dir %tconfdir
%dir %tconfdir/modules
%dir %tconfdir/deploy
%dir %tconfdir/clients

%dir %tmoduledir
%dir %_datadir/%tname
%dir %tslicedir
# FIXME: this should have a better place
%ttemplatedir
# and this too
%_sysconfdir/pam.d/*


%files -n %tname-srv1
%_sbindir/*1
%tconfdir/%{tname}*.conf
%_initdir/*

%files -n %tname-deploy-srv
%_sbindir/*deploy-srv
%tconfdir/clients/deploy*

%files -n %tname-join
%_sbindir/*join*

%files -n %tname-leave
%_sbindir/*leave*

%files -n python-module-%tname
%dir %tpythondir
%tpythondir/__init__*
%tpythondir/auth*
%tpythondir/iface*
%tpythondir/logging*
%tpythondir/modules*
%tpythondir/slices*

%files -n python-module-%tname-daemon
%tpythondir/daemon*

%files -n python-module-%tname-system
%tpythondir/system*

%files -n python-module-%tname-db
%tpythondir/db*

%files -n python-module-%tname-deploy
%tpythondir/deploy*

%files -n %tname-DNS
%tconfdir/*/DNS*
%tmoduledir/DNS


%files -n %tname-Kadmin5
%tconfdir/*/Kadmin5*
%tmoduledir/Kadmin5

%files -n %tname-SysDB
%tconfdir/*/SysDB*
%tmoduledir/SysDB

%files -n %tname-core-slice
%dir %tslicedir
%tslicedir/core

%files -n %tname-Kerberos-slice
%tslicedir/Kerberos

%files -n %tname-DNS-slice
%tslicedir/DNS

%files -n %tname-SysDB-slice
%tslicedir/SysDB


# {{{1 changelog

%changelog
* Wed Feb 18 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.8.2-alt1
- add waf build system

* Wed Feb 18 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.8.1-alt2
- build fixes for sisyphus prebuild of alpha3
+ Now proper services should start and stop in proper moments (#114)
+ core: minor pylint-driven code cleanup
+ SysDB: fixed broken test database dump
+ SysDB: improved diagnostics on user and group creation

* Fri Feb 06 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.8.1-alt1
- build alpha2 for sisyphus
+ add leave running to Tartarus-leave preun script
+ add force option to Tartarus-leave for uninstall scripts

* Fri Jan 30 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.2-alt3
- build fixes for sisyphus prebuild of alpha2
+ add SRV records for kadmin service
+ change join default admin username

* Thu Jan 29 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.2-alt2
- build for sisyphus prebuild of alpha2
+ fixed admin and user names, added kadmin and nscd starting

* Wed Jan 28 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.2-alt1
- build for sisyphus prebuild of alpha2
+ refuse to create system users
+ refactored SysDB database code

* Fri Jan 23 2009 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.1-alt1
- build for sisyphus alpha1

