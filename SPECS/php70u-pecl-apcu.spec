# IUS spec file for php56u-pecl-apcu, forked from:
#
# Fedora spec file for php-pecl-apcu
#
# Copyright (c) 2013-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?php_incldir: %global php_incldir %{_includedir}/php}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}

%global pecl_name apcu
%global with_zts  0%{?__ztsphp:1}
%global ini_name  40-%{pecl_name}.ini
%global php_base php70u

Name:           %{php_base}-pecl-apcu
Summary:        APC User Cache
Version:        5.1.3
Release:        1.ius%{?dist}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source1:        %{pecl_name}.ini
Source2:        %{pecl_name}-panel.conf
Source3:        %{pecl_name}.conf.php

License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/APCu

BuildRequires:  %{php_base}-devel
BuildRequires:  %{php_base}-pear
BuildRequires:  pcre-devel

Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
Requires:       %{php_base}(zend-abi) = %{php_zend_api}
Requires:       %{php_base}(api) = %{php_core_api}

# provide the stock name
Provides:       php-pecl-%{pecl_name} = %{version}
Provides:       php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides:       php-%{pecl_name} = %{version}
Provides:       php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{php_base}-%{pecl_name} = %{version}
Provides:       %{php_base}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides:       php-pecl(%{pecl_name}) = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:       %{php_base}-pecl(%{pecl_name}) = %{version}
Provides:       %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# Same provides than APC, this is a drop in replacement
Provides:       php-apc = %{version}
Provides:       php-apc%{?_isa} = %{version}
Provides:       php-pecl-apc = %{version}
Provides:       php-pecl-apc%{?_isa} = %{version}
Provides:       php-pecl(APC) = %{version}
Provides:       php-pecl(APC)%{?_isa} = %{version}

# conflict with the stock name
Conflicts:      php-pecl-%{pecl_name} < %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
APCu is userland caching: APC stripped of opcode caching in preparation
for the deployment of Zend OPcache as the primary solution to opcode
caching in future versions of PHP.

APCu has a revised and simplified codebase, by the time the PECL release
is available, every part of APCu being used will have received review and
where necessary or appropriate, changes.

Simplifying and documenting the API of APCu completely removes the barrier
to maintenance and development of APCu in the future, and additionally allows
us to make optimizations not possible previously because of APC's inherent
complexity.

APCu only supports userland caching (and dumping) of variables, providing an
upgrade path for the future. When O+ takes over, many will be tempted to use
3rd party solutions to userland caching, possibly even distributed solutions;
this would be a grave error. The tried and tested APC codebase provides far
superior support for local storage of PHP variables.


%package devel
Summary:       APCu developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{php_base}-devel%{?_isa}
Provides:      php-pecl-apc-devel = %{version}-%{release}
Provides:      php-pecl-apc-devel%{?_isa} = %{version}-%{release}
Provides:      php-pecl-%{pecl_name}-devel = %{version}
Provides:      php-pecl-%{pecl_name}-devel%{?_isa} = %{version}
Conflicts:     php-pecl-%{pecl_name}-devel < %{version}

%description devel
These are the files needed to compile programs using APCu.


%package panel
Summary:       APCu control panel
Group:         Applications/Internet
BuildArch:     noarch
Requires:      %{name} = %{version}-%{release}
Requires:      mod_php70u
Requires:      %{php_base}-gd
Provides:      apc-panel = %{version}-%{release}
Provides:      apcu-panel = %{version}
Conflicts:     apcu-panel < %{version}

%description panel
This package provides the APCu control panel, with Apache
configuration, available on http://localhost/apcu-panel/


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

cd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_APCU_VERSION/{s/.* "//;s/".*$//;p}' php_apc.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi
cd ..

%if %{with_zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif

# Fix path to configuration file
sed -e s:apc.conf.php:%{_sysconfdir}/apcu-panel/conf.php:g \
    -i  NTS/apc.php


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{SOURCE1} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{SOURCE1} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Install the Control Panel
# Pages
install -D -m 644 -p NTS/apc.php  \
        %{buildroot}%{_datadir}/apcu-panel/index.php
# Apache config
install -D -m 644 -p %{SOURCE2} \
        %{buildroot}%{_sysconfdir}/httpd/conf.d/apcu-panel.conf
# Panel config
install -D -m 644 -p %{SOURCE3} \
        %{buildroot}%{_sysconfdir}/apcu-panel/conf.php

# Test & Documentation
cd NTS
for i in $(grep 'role="test"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
cd NTS

# Check than both extensions are reported (BC mode)
%{_bindir}/php -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apcu'
%{_bindir}/php -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apc$'

# Upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php

%if %{with_zts}
cd ../ZTS

%{__ztsphp}    -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apcu'
%{__ztsphp}    -n -d extension_dir=modules -d extension=apcu.so -m | grep 'apc$'

# Upstream test suite for ZTS extension
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%{php_ztsextdir}/%{pecl_name}.so
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%endif


%files devel
%doc %{pecl_testdir}/%{pecl_name}
%{php_incldir}/ext/%{pecl_name}

%if %{with_zts}
%{php_ztsincldir}/ext/%{pecl_name}
%endif


%files panel
# Need to restrict access, as it contains a clear password
%attr(550,apache,root) %dir %{_sysconfdir}/apcu-panel
%config(noreplace) %{_sysconfdir}/apcu-panel/conf.php
%config(noreplace) %{_sysconfdir}/httpd/conf.d/apcu-panel.conf
%{_datadir}/apcu-panel


%changelog
* Mon Feb 08 2016 Carl George <carl.george@rackspace.com> - 5.1.3-1.ius
- Latest upstream
- Port from Fedora to IUS

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec  7 2015 Remi Collet <remi@fedoraproject.org> - 4.0.10-1
- Update to 4.0.10 (stable)

* Fri Nov 20 2015 Remi Collet <remi@fedoraproject.org> - 4.0.8-1
- Update to 4.0.8

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Oct 27 2014 Remi Collet <remi@fedoraproject.org> - 4.0.7-1
- Update to 4.0.7

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 4.0.6-2
- rebuild for https://fedoraproject.org/wiki/Changes/Php56

* Thu Jun 12 2014 Remi Collet <remi@fedoraproject.org> - 4.0.6-1
- Update to 4.0.6 (beta)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 23 2014 Remi Collet <remi@fedoraproject.org> - 4.0.4-2
- add numerical prefix to extension configuration file

* Sat Mar 01 2014 Remi Collet <remi@fedoraproject.org> - 4.0.4-1
- Update to 4.0.4 (beta)

* Mon Jan 27 2014 Remi Collet <remi@fedoraproject.org> - 4.0.3-1
- Update to 4.0.3 (beta)
- install doc in pecl doc_dir
- install tests in pecl test_dir (in devel)
- cleanup SCL stuff

* Mon Jan 13 2014 Remi Collet <rcollet@redhat.com> - 4.0.2-3
- EPEL-7 build

* Mon Sep 16 2013 Remi Collet <rcollet@redhat.com> - 4.0.2-2
- fix perm on config dir
- improve SCL compatibility
- always provides php-pecl-apc-devel and apc-panel

* Mon Sep 16 2013 Remi Collet <remi@fedoraproject.org> - 4.0.2-1
- Update to 4.0.2

* Sat Jul 27 2013 Remi Collet <remi@fedoraproject.org> - 4.0.1-3
- restore APC serializers ABI (patch merged upstream)

* Mon Jul 15 2013 Remi Collet <rcollet@redhat.com> - 4.0.1-2
- adapt for SCL

* Tue Apr 30 2013 Remi Collet <remi@fedoraproject.org> - 4.0.1-1
- Update to 4.0.1
- add missing scriptlet
- fix Conflicts

* Thu Apr 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-2
- fix segfault when used from command line

* Wed Mar 27 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-1
- first pecl release
- rename from php-apcu to php-pecl-apcu

* Tue Mar 26 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.4.git4322fad
- new snapshot (test before release)

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.3.git647cb2b
- new snapshot with our pull request
- allow to run test suite simultaneously on 32/64 arch
- build warning free

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.2.git6d20302
- new snapshot with full APC compatibility

* Sat Mar 23 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.1.git44e8dd4
- initial package, version 4.0.0
