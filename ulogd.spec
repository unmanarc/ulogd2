Summary: Userspace logging daemon for netfilter
Name: ulogd
Version: 2.0.7
Release: 2%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://www.netfilter.org/projects/%{name}/
#Source0: http://ftp.netfilter.org/pub/%{name}/%{name}-%{version}.tar.bz2
# http not allowed in COPR.
Source0: https://raw.githubusercontent.com/unmanarc/ulogd2rpm/main/%{name}-%{version}.tar.bz2
Source1: https://raw.githubusercontent.com/unmanarc/ulogd2rpm/main/ulogd.init
Patch0: https://raw.githubusercontent.com/unmanarc/ulogd2rpm/main/ulogd-rpm.patch

%define cmake cmake

%if 0%{?rhel} == 6
%define cmake cmake3
%endif

%if 0%{?rhel} == 7
%define cmake cmake3
%endif

BuildRequires: libnetfilter_conntrack-devel >= 0.0.95
BuildRequires: libnetfilter_log-devel >= 1.0.0
BuildRequires: libnfnetlink-devel >= 0.0.39
BuildRequires: libnetfilter_acct-devel >= 1.0.1 
BuildRequires: sgml-tools
BuildRequires: libmnl-devel
BuildRequires: %{cmake} gcc-c++ gcc

Requires(post): /sbin/service
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service

%description
%{name} is a logging daemon that reads event messages coming from the Netfilter
connection tracking and the Netfilter packet logging subsystem. You have to
enable support for connection tracking event delivery; ctnetlink and the NFLOG
target in your Linux kernel 2.6.x or load their respective modules. The
deprecated ULOG target (which has been superseded by NFLOG) is also supported.

%package libdbi
Summary: Libdbi framework output plugin for %{name}
Group: System Environment/Daemons
BuildRequires: libdbi-devel
Requires: %{name} = %{version}
%description libdbi
%{name}-libdbi is a libdbi output plugin for %{name}. It enables logging of
firewall information through a libdbi interface.

%package mysql
Summary: MySQL output plugin for %{name}
Group: System Environment/Daemons
BuildRequires: mysql-devel
#BuildRequires: openssl-devel
Requires: %{name} = %{version}
%description mysql
%{name}-mysql is a MySQL output plugin for %{name}. It enables logging of
firewall information into a MySQL database.

%package pgsql
Summary: PostgreSQL output plugin for %{name}
Group: System Environment/Daemons
BuildRequires: postgresql-devel
Requires: %{name} = %{version}
%description pgsql
%{name}-pgsql is a PostgreSQL output plugin for %{name}. It enables logging of
firewall information into a PostgreSQL database.

%package pcap
Summary: PCAP output plugin for %{name}
Group: System Environment/Daemons
BuildRequires: libpcap-devel
Requires: %{name} = %{version}
%description pcap
%{name}-pcap is a output plugin for %{name} that saves packet logs as PCAP
file. PCAP is a standard format that can be later analyzed by a lot of tools
such as tcpdump and wireshark.

%package sqlite
Summary: SQLITE output plugin for %{name}
Group: System Environment/Daemons
BuildRequires: sqlite-devel
Requires: %{name} = %{version}
%description sqlite
%{name}-sqlite is a SQLITE output plugin for %{name}. It enables logging of
firewall information into an SQLITE database.

%prep
%setup -q
%patch0 -p1

%{__sed} -i -e 's|/var/log/|%{_localstatedir}/log/%{name}/|g' %{name}.conf.in

%build
%configure \
   --disable-static \
   --enable-shared \
   --with-dbi-lib=%{_libdir} \
   --with-pcap-lib=%{_libdir} \
   --with-sqlite3-lib=%{_libdir}

%{__make} %{?_smp_mflags}
%{__make} %{?_smp_mflags} -C doc

%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install

%{__mkdir_p} -m 0755 %{buildroot}%{_localstatedir}/log/%{name}/

%{__mkdir_p} -m 0755 %{buildroot}%{_sysconfdir}/
%{__install} -m 0644 %{name}.conf %{buildroot}%{_sysconfdir}/

%{__mkdir_p} -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d/
%{__install} -m 0644 %{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__mkdir_p} -m 0755 %{buildroot}%{_initrddir}/
%{__install} -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

%post
/sbin/chkconfig --add %{name}
/sbin/service %{name} condrestart >/dev/null 2>&1 || :

%preun
# if we are uninstalling...
if [ "$1" = 0 ]; then
   /sbin/service %{name} stop > /dev/null 2>&1 ||:
   /sbin/chkconfig --del %{name}
fi

%postun
# if we are upgrading...
if [ "$1" -ge "1" ]; then
   /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%check
%{__make} %{?_smp_mflags} check

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(0755,root,root,0755)
%{_sbindir}/%{name}
%{_initrddir}/%{name}
%{_libdir}/%{name}
%defattr(0644,root,root,0755)
%doc COPYING
%doc AUTHORS README
%doc doc/%{name}.txt doc/%{name}.ps doc/%{name}.html
%doc %{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_localstatedir}/log/%{name}
%exclude %{_libdir}/%{name}/*.la
%exclude %{_libdir}/%{name}/%{name}_output_DBI.so
%exclude %{_libdir}/%{name}/%{name}_output_MYSQL.so
%exclude %{_libdir}/%{name}/%{name}_output_PGSQL.so
%exclude %{_libdir}/%{name}/%{name}_output_PCAP.so
%exclude %{_libdir}/%{name}/%{name}_output_SQLITE3.so

%files libdbi
%defattr(0755,root,root,0755)
%{_libdir}/%{name}/%{name}_output_DBI.so
%defattr(0644,root,root,0755)
%doc COPYING

%files mysql
%defattr(0755,root,root,0755)
%{_libdir}/%{name}/%{name}_output_MYSQL.so
%defattr(0644,root,root,0755)
%doc COPYING

%files pgsql
%defattr(0755,root,root,0755)
%{_libdir}/%{name}/%{name}_output_PGSQL.so
%defattr(0644,root,root,0755)
%doc COPYING

%files pcap
%defattr(0755,root,root,0755)
%{_libdir}/%{name}/%{name}_output_PCAP.so
%defattr(0644,root,root,0755)
%doc COPYING

%files sqlite
%defattr(0755,root,root,0755)
%{_libdir}/%{name}/%{name}_output_SQLITE3.so
%defattr(0644,root,root,0755)
%doc COPYING

%changelog
* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Sep 22 2015 Martin Preisler <mpreisle@redhat.com> 2.0.5-1
- new upstream release

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Apr 15 2014 Martin Preisler <mpreisle@redhat.com> 2.0.4-1
- new upstream release

* Mon Jan 27 2014 Martin Preisler <mpreisle@redhat.com> 2.0.3-2
- rebuilt because of libdbi ABI break

* Fri Nov 29 2013 Martin Preisler <mpreisle@redhat.com> 2.0.3-1
- update version

* Tue Sep 24 2013 Martin Preisler <mpreisle@redhat.com> 2.0.2-2
- added accidentaly removed dist suffix in release
- fixed up bogus dates in changelog

* Mon Sep 09 2013 Martin Preisler <mpreisle@redhat.com> 2.0.2-1
- update version

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-5.beta4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-4.beta4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-3.beta4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-2.beta4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Nov 23 2011 Stephen Beahm <stephenbeahm@comcast.net> - 2.0.0-1.beta4
- update version.
- spec review.
- (rebased on top of the remaining 1.24 changes, original date was Nov 16 2010)

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 1.24-15
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.24-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.24-13
- rebuilt with new openssl

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.24-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.24-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 24 2009 Aurelien Bompard <abompard@fedoraproject.org> 1.24-10
- rebuild for mysql

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.24-9
- Autorebuild for GCC 4.3

* Wed Jan 9 2008 Leopold Aichinger <linuxtrainer@gmx.at> 1.24-8
- Support for libpcap added

* Thu Dec 06 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.24-7
- Rebuild for deps

* Tue Aug 14 2007 Aurelien Bompard <abompard@fedoraproject.org> 1.24-5
- Fix the deprecated way of getting the DSO initializers run, causing
  builds to fails with rpm-build > 4.4.2.1-3 (new find-debuginfo.sh script)

* Sat Jul 14 2007 Aurelien Bompard <abompard@fedoraproject.org> 1.24-4
- add patch to fix bug 247345
- update URL
- fix initscript (bug 247083)
- unmark init script as %%config (Fedora policy)

* Sat Dec 09 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.24-3
- rebuild

* Thu Aug 31 2006 Aurelien Bompard <abompard@fedoraproject.org> 1.24-2
- rebuild

* Wed Feb 22 2006 Aurelien Bompard <gauret[AT]free.fr> 1.24-1
- version 1.24
- drop patch3 (applied upstream)
- drop patch4 (upstream uses mysql-config to detect libdir now)
- drop patch5 (applied upstream)

* Tue Feb 21 2006 Aurelien Bompard <gauret[AT]free.fr> 1.23-3
- rebuild for FC5

* Sun Jul 24 2005 Aurelien Bompard <gauret[AT]free.fr> 1.23-2
- compress rotated logs
- start after mysql in the init process
- use dist tag

* Tue Apr 19 2005 Aurelien Bompard <gauret[AT]free.fr> 1.23-1.fc4
- version 1.23
- change release tag for FC4
- add patch for GCC4 (upstream bug #323)

* Thu Apr 07 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Wed Mar 09 2005 Aurelien Bompard <gauret[AT]free.fr> 1.22-1
- version 1.22
- add gpg signature to sources

* Sun Feb 20 2005 Aurelien Bompard <gauret[AT]free.fr> 1.21-1
- version 1.21

* Fri Dec 17 2004 Michael Schwendt <mschwendt[AT]users.sf.net> 1.02-8
- revise x86_64 patch to remove more hardcoded /lib badness

* Fri Dec 17 2004 Michael Schwendt <mschwendt[AT]users.sf.net> 1.02-7
- x86_64, patch configure to look for mysql/pgsql below %%_libdir.
- delete undefined %%epoch in mysql/pgsql sub package dep.

* Sun Oct 31 2004 Aurelien Bompard <gauret[AT]free.fr> 1.02-6
- apply Michael Schwendt's suggestions in bug 1598

* Wed Oct 20 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.02-0.fdr.5
- enable MySQL and PostgreSQL in subpackages
- add man page from Debian

* Wed Oct 06 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.02-0.fdr.4
- apply QA suggestions (bug 1598)

* Sat Jul 10 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.02-0.fdr.3
- disable parallel builds
- add chkconfig to Requires(pre,post)
- set the right mode for /etc/logrotate.d/ulogd
- rotate weekly

* Sun May 16 2004 Aurelien Bompard <gauret[AT]free.fr> 0:1.02-0.fdr.2
- Add Epoch: 0
