
Version: 0.1.2
Release: alt0.1

%define tname Tartarus

Summary: %tname Core components
Name: %tname-core
Source: %tname-%version.tar
License: %gpl2plus
Group: System/Configuration/Other
Url: http://www.tartarus.ru
Packager: Ivan A. Melnikov <iv@altlinux.org>

BuildRequires(pre): rpm-build-licenses, rpm-build-python

# Automatically added by buildreq on Fri Mar 21 2008
BuildRequires: python-devel

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
Provides: %tname = %version-%release
Requires: %tname-common = %version-%release
Requires: %tname-Kerberos-slice = %version-%release
Requires: %tname-SysDB-slice = %version-%release
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-deploy = %version-%release
Requires: python-module-%tname-system = %version-%release
Requires: %tname-dnsupdate >= 0.1.0
Requires: libnss-tartarus, krb5-kinit, pam_krb5

%description -n %tname-join
Tartarus client deployment.


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


# {{{1 install

%install
mkdir -p %buildroot%tmoduledir
cp -pR %tname/[A-Z]* %buildroot%tmoduledir

mkdir -p %buildroot%tpythondir
cp -pR %tname/[a-z_]* %buildroot%tpythondir

mkdir -p %buildroot%_sbindir
cp -pR bin/* %buildroot%_sbindir

mkdir -p %buildroot%tconfdir
cp -pR config/* %buildroot%tconfdir

mkdir -p %buildroot%ttemplatedir
cp -pR templates/* %buildroot%ttemplatedir

mkdir -p %buildroot%_initdir
cp -pR init/* %buildroot%_initdir

mkdir -p %buildroot%tslicedir
cp -pR slice/* %buildroot%tslicedir

mkdir -p %buildroot%_sysconfdir/pam.d
cp -pR pam/* %buildroot%_sysconfdir/pam.d

mkdir -p %buildroot%_localstatedir/%tname/SysDB


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
%_localstatedir/%tname/SysDB


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
* Mon Jan 26 2009 Ivan A. Melnikov <iv@altlinux.org> 0.1.2-alt0.1
- new version: refactored SysDB database code

* Fri Dec 26 2008 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.1-alt0.10
- fixed syntax error

* Tue Dec 23 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.9
- new snapshot: join improvements

* Tue Dec 23 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.8
- new snapshot: bugfixes

* Mon Dec 22 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.7
- new snapshot: better diagnostics in few places

* Mon Dec 22 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.6
- relaxed dependency on dnsupdate

* Mon Dec 22 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.5
- new snapshot: bugfixes

* Mon Dec 22 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.3
- added forgotten auth submodule

* Mon Dec 22 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.2
- fixed a typo

* Mon Dec 22 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.1-alt0.1
- new version
  + basic authorization added

* Fri Nov 28 2008 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.0-alt0.18
- fixed join with missed sethostname() implementation

* Fri Nov 28 2008 Evgeny Sinelnikov <sin@altlinux.ru> 0.1.0-alt0.17
- fixed join with missed system.hosts
- fixed first deployment server prompt

* Fri Nov 28 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.16
- new snapshot: join improvements
- dependency cleanup

* Thu Nov 27 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.15
- added missed requirements to Tartarus-deploy-srv

* Thu Nov 27 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.14
- new snapshot: bugfixes

* Wed Nov 26 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.13
- new snapshot:
  - many improvements in server deployment
  - added Tartarus-leave: utility to remove clients from domain

* Wed Nov 26 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.12
- new snapshot: minor fixes in deployment

* Wed Nov 26 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.11
- fixed a typo in specfile

* Wed Nov 26 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.10
- added Tartarus-join subpackage to deploy clients

* Tue Nov 25 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.9
- new snapshot:
  - several bug fixes
  - many deployment improvements; in partucular:
    - server is it's own client now (closes #25)
    - necessary services are restarted after deployment is finished

* Tue Nov 18 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.8
- new snapshot: improved error diagnostics and handling

* Tue Nov 18 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.7
- new snapshot: Kadmin5: fixed default path to templates

* Tue Nov 18 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.6
- fixed configuration files installation
- added dependency on python-module-dnet

* Mon Nov 17 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.5
- new snapshot:
    deploy-srv: better system network address detection
    DNS: sqlite3 as default database engine
- now modules require services they configure

* Mon Nov 17 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.4
- added missed %% in dependencies
- fixed requirements for deploy-srv

* Mon Nov 17 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.3
- fixed creating directory for SysDB database

* Mon Nov 17 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.2
- added packages related to server deployment:
  - python-module-Tartarus-deploy
  - Tartarus-deploy-srv
- fixed some errors in dependencies

* Mon Nov 10 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.1
- inital build from one common files

