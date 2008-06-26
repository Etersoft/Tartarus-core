# -*- coding: utf-8 -*-

%define tmodname Kadmin5

Version: 0.0.2
Release: eter1


Summary: Tartarus example servant
Name: Tartarus-%tmodname
Source: %tmodname-%version.tar
License: %gpl2plus
Group: System/Servers
Url: http://www.tartarus.ru

BuildArchitectures: noarch

Requires: %name-slice = %version-%release

Packager: Ivan A. Melnikov <iv@altlinux.org>
BuildRequires(pre): rpm-build-licenses

# Automatically added by buildreq on Wed May 28 2008
BuildRequires: python-base

%description
This module privides Tartarus example servant named %tmodname.

This module is built for python %__python_version.


%package slice
Group: Development/Other
Summary: Interface definisions for %tmodname

BuildArch: noarch

%description slice
Interface definisions for %name.

%prep

%setup  -q -n %tmodname-%version


%install
%__mkdir_p %buildroot/%_libdir/Tartarus/modules
%__cp -R Tartarus/* %buildroot/%_libdir/Tartarus/modules
%__mkdir_p %buildroot/%_datadir/Tartarus
%__cp -R slice %buildroot/%_datadir/Tartarus
%__mkdir_p %buildroot%_sysconfdir/Tartarus/modules
%__cp config/* %buildroot%_sysconfdir/Tartarus/modules

%files
%_libdir/Tartarus/modules/*
%_sysconfdir/Tartarus/modules/*


%files slice
%_datadir/Tartarus/slice/*/*

%changelog
* Thu Jun 26 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.2-eter1
- new version: enabling and disabling of principals implemented

* Thu Jun 05 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.1-eter1
- inital build

