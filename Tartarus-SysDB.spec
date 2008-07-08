# -*- coding: utf-8 -*-

%define modulename SysDB

Version: 0.0.1
Release: alt1


Summary: Tartarus example servant
Name: Tartarus-%modulename
Source: %name-%version.tar
License: %gpl2plus
Group: System/Servers
Url: http://www.tartarus.ru
Packager: Ivan A. Melnikov <iv@altlinux.org>
BuildArchitectures: noarch

Requires: %name-slice = %version-%release, Tartarus


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
%__mkdir_p %buildroot/%_libdir/Tartarus/modules
%__cp -R Tartarus/* %buildroot/%_libdir/Tartarus/modules
%__mkdir_p %buildroot/%_datadir/Tartarus
%__cp -R slice %buildroot/%_datadir/Tartarus

%files
%_libdir/Tartarus/modules/*
#doc README 

%files slice
%dir %_datadir/Tartarus/slice/%modulename
%_datadir/Tartarus/slice/%modulename/*

%changelog


