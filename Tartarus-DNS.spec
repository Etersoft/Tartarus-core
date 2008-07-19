# -*- coding: utf-8 -*-

%define modulename DNS

Version: 0.0.1
Release: alt2


Summary: Tartarus example servant
Name: Tartarus-%modulename
Source: %name-%version.tar
License: %gpl2plus
Group: System/Servers
Url: http://www.tartarus.ru
Packager: Ivan A. Melnikov <iv@altlinux.org>
BuildArchitectures: noarch

Requires: %name-slice = %version-%release, Tartarus
Requires: python-module-pysqlite, pdns-backend-sqlite


BuildRequires(pre): rpm-build-licenses
# Automatically added by buildreq on Wed May 28 2008
BuildRequires: python-base

%description
This module privides Tartarus example servant named %modulename.

This module is built for python %__python_version.


%package slice
Group: Development/Other
Summary: Interface definisions for %modulename

BuildArchitectures: noarch

%description slice
Interface definisions for %name.

%prep

%setup  -q


%install
%__mkdir_p %buildroot%_datadir/Tartarus
%__cp -R slice %buildroot%_datadir/Tartarus

%__mkdir_p %buildroot%_libdir/Tartarus/modules
%__cp -R Tartarus/* %buildroot%_libdir/Tartarus/modules

%__mkdir_p %buildroot%_sysconfdir/Tartarus/modules
%__cp config/%modulename.conf %buildroot%_sysconfdir/Tartarus/modules

%__mkdir_p %buildroot%_sysconfdir/Tartarus/deploy
%__cp config/%modulename-deploy.conf %buildroot%_sysconfdir/Tartarus/deploy/%modulename.conf

%files
%_libdir/Tartarus/modules/*
%config(noreplace) %_sysconfdir/Tartarus/modules/%modulename.conf
%config %_sysconfdir/Tartarus/deploy/%modulename.conf

%files slice
%_datadir/Tartarus/slice/*/*

%changelog
* Sat Jul 19 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.1-alt2
- new snapshot
- improved dependencies

* Wed May 28 2008 Ivan Melnikov <imelnikov@etersoft.ru> 0.0.1-alt1
- inital build


