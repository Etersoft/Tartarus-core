Version: 0.0.1
Release: alt1

%setup_python_module Tartarus-System

Summary: Tartarus System utils for python
Name: %packagename
Source: %modulename-%version.tar
License: %gpl2plus
Group: Development/Python
Url: http://tartarus.org
Packager: Evgeny Sinelnikov <sin@altlinux.ru>


Requires: python-module-Ice
Provides: Tartarus-system = %version-%release

BuildRequires(pre): rpm-build-licenses
BuildRequires: python-devel

%description
This module provides basic system utilities for Tartarus modules written in python.

This module is built for python %__python_version


%prep

%setup  -q -n %modulename-%version

%install
%__mkdir_p  %buildroot%python_sitelibdir/Tartarus
%__cp -Rp System %buildroot%python_sitelibdir/Tartarus


%files
%python_sitelibdir/*

%changelog
* Fri Oct 17 2008 Evgeny Sinelnikov <sin@altlinux.ru> 0.0.1-alt1
- Initial first build

