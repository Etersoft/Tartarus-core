
Version: 0.1.0
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

# Utility

%package -n %tname-common
Summary: Common files for %tname
Group: System/Configuration/Other

%description -n %tname-common
Common files required by most of %tname modules.


%package -n %tname-srv1
Summary: %tname python service loader
Group: System/Servers
Provides: %tname = %version-release
Requires: %tname-common = %version-%release
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-daemon = %version-%release

%description -n %tname-srv1
%tname python service loader


# Internal modules

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


# Configurators

%package -n %tname-DNS
Summary: %tname DNS Configurator.
Group: System/Configuration/Other
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-db = %version-%release
Requires: %tname = %version-release

%description -n %tname-DNS
%tname DNS Configurator.

This module is built for python %__python_version


%package -n %tname-Kadmin5
Summary: %tname Kadmin5 Configurator.
Group: System/Configuration/Other
Requires: python-module-%tname = %version-%release
Requires: python-module-kadmin5 >= 0.0.5
Requires: %tname = %version-release

%description -n %tname-Kadmin5
%tname Kadmin5 Configurator.

This module is built for python %__python_version


%package -n %tname-SysDB
Summary: %tname SysDB service.
Group: System/Servers
Requires: python-module-%tname = %version-%release
Requires: python-module-%tname-db = %version-%release
Requires: %tname = %version-release

%description -n %tname-SysDB
%tname SysDB service.

This module is built for python %__python_version


# Slices

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


%prep
%define tconfdir %_sysconfdir/%tname
%define tmoduledir %_libdir/%tname/modules
%define tslicedir %_datadir/%tname/slice
%define tpythondir %python_sitelibdir/%tname

%setup  -q -n %tname-%version

%install
mkdir -p %buildroot%tmoduledir
cp -pR %tname/[A-Z]* %buildroot%tmoduledir

mkdir -p %buildroot%tpythondir
cp -pR %tname/[a-z_]* %buildroot%tpythondir

mkdir -p %buildroot%_sbindir
cp -pR bin/* %buildroot%_sbindir

mkdir -p %buildroot%tconfdir
cp -pR config/* %buildroot%tconfdir

mkdir -p %buildroot%_initdir
cp -pR init/* %buildroot%_initdir

mkdir -p %buildroot%tslicedir
cp -pR slice/* %buildroot%tslicedir

mkdir -p %_localstatedir/%tname/SysDB



%files -n %tname-common
%dir %tconfdir
%dir %tconfdir/modules
%dir %tconfdir/deploy

%dir %tmoduledir

%files -n %tname-srv1
%_sbindir/*
%tconfdir/%{tname}*.conf
%_initdir/*


%files -n python-module-%tname
%dir %tpythondir
%tpythondir/__init__*
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


%changelog
* Mon Nov 10 2008 Ivan A. Melnikov <iv@altlinux.org> 0.1.0-alt0.1
- inital build from one common files

