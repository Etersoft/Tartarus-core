# -*- coding: utf-8 -*-

%define srvname tartarus-srv1

Version: 0.0.3
Release: alt3

%setup_python_module Tartarus

Summary: Tartarus framework for python
Name: %packagename
Source: %modulename-%version.tar
License: %gpl2plus
Group: Development/Python
Prefix: %_prefix
Url: http://tartarus.org
Packager: Ivan A. Melnikov <iv@altlinux.org>

BuildArch: noarch

Requires: python-module-Ice

BuildRequires(pre): rpm-build-licenses
# Automatically added by buildreq on Fri Mar 21 2008
BuildRequires: python-devel

%description
This module provides basic environment for Tartarus moudles written in python.

This module is built for python %__python_version


%package -n %srvname
Group: System/Servers
Summary: Tartarus for Python
Requires: %name = %version
Provides: Tartarus

%description -n %srvname
Install %srvname if you need to run tartarus servants written in python.


%prep

%setup  -q -n %modulename-%version


%install
%__mkdir_p  %buildroot%python_sitelibdir
%__cp -Rp  Tartarus %buildroot%python_sitelibdir
%__mkdir_p  %buildroot%_sbindir
%__cp %srvname %buildroot%_sbindir
%__mkdir_p %buildroot%_sysconfdir/Tartarus/modules
%__mkdir_p %buildroot%_sysconfdir/Tartarus/deploy
%__cp config/* %buildroot%_sysconfdir/Tartarus
%__mkdir_p %buildroot%_initdir
%__cp -p init/* %buildroot%_initdir

%post -n %srvname
%post_service Tartarus

%preun -n %srvname
%preun_service Tartarus


%files
%python_sitelibdir/*

%files -n %srvname
%_sbindir/*
%dir %_sysconfdir/Tartarus
%dir %_sysconfdir/Tartarus/modules
%dir %_sysconfdir/Tartarus/deploy
%config %_sysconfdir/Tartarus/Tartarus-deploy.conf
%config(noreplace) %_sysconfdir/Tartarus/Tartarus.conf
%_initdir/Tartarus

%changelog
* Fri Sep 12 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.3-alt3
- new snapshot
  - added support for deffered plugins initialization
  - added all-or-nothing behaviour to deploy mode module loader

* Wed Sep 10 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.3-alt1
- new snapshot
- fixed build dependencies

* Wed Jul 09 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.2-eter2
- new snapshot:
    - added Tartarus.db submodule
    - many bugfixes
- added special configuration for deployment

* Fri Jun 27 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.2-eter1
- new snapshot:
    - improvements in daemon code
    - better scheme of module loading
- configuration files updated

* Thu Jun 05 2008 Ivan A. Melnikov <iv@altlinux.org> 0.0.1-eter1
- inital build



