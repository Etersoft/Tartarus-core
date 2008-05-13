# -*- coding: utf-8 -*-

%define srvname tartarus-srv1

Version: 0.0.1
Release: eter0

%setup_python_module Tartarus

Summary: Tartarus framework for python
Name: %packagename
Source: %modulename-%version.tar
License: %gpl2plus
Group: Development/Python/Modules
Prefix: %_prefix
Url: http://tartarus.org

BuildArchitectures: noarch


# Automatically added by buildreq on Fri Mar 21 2008
BuildRequires: python-devel

%description
This module provides basic environment for Tartarus moudles written in python.

This module is built for python %__python_version


%package -n %srvname
Group: System/Servers
Summary: Tartarus for Python

%description -n %srvname
Install %srvname if you need to run tartarus servants written in python.


%prep

%setup  -q -n %modulename-%version

#build
#__python setup.py build

%install
#__python setup.py install --root=%buildroot --optimize=2 --record=INSTALLED_FILES
%__mkdir_p  %buildroot%python_sitelibdir
%__cp -Rp  Tartarus %buildroot%python_sitelibdir
%__mkdir_p  %buildroot%_sbindir
%__cp %srvname %buildroot%_sbindir

%files
%python_sitelibdir/*
#files -f INSTALLED_FILES
#doc README README.ru

%files -n %srvname
%_sbindir/*

%changelog


