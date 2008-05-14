# -*- coding: utf-8 -*-

%define tart_module Kadmin5

Version: 0.0.1
Release: alt0

%setup_python_module Tartarus-%tart_module

Summary: Tartarus example servant
Name: %packagename
Source: %modulename-%version.tar.gz
License: %gpl2plus
Group: Development/Python/Modules
Prefix: %_prefix
Url: http://tartarus.ru

BuildArchitectures: noarch

Requires: %modulename-slice = %version-%release

# Automatically added by buildreq on Fri Mar 21 2008
BuildRequires: python-devel

%description
This module privides Tartarus example servant named %tart_module

This module is built for python %__python_version


%package -n %modulename-slice
Group: Development/Other
Summary: Interface definisions for %modulename

BuildArchitectures: noarch

%description -n %modulename-slice
Interface definisions for %modulename.

%prep

%setup  -q -n %modulename-%version


%install
%__mkdir_p %buildroot/%_libdir/Tartarus/modules
%__cp -R Tartarus/* %buildroot/%_libdir/Tartarus/modules
%__mkdir_p %buildroot/%_datadir/Tartarus
%__cp -R slice %buildroot/%_datadir/Tartarus

%files
%_libdir/Tartarus/modules/*
%doc README 

%files -n %modulename-slice
%_datadir/Tartarus/slice/*/*

%changelog
* Fri Apr 14 2008 Ivan Melnikov <imelnikov@etersoft.ru> 0.0.1-alt0
- inital build

