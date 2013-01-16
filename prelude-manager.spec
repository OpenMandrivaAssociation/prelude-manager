Name:           prelude-manager
Version:        1.0.2
Release:        2
Summary:        Prelude Hybrid Intrusion Detection System Manager
License:        GPLv2+
Group:          System/Servers
URL:            http://www.prelude-ids.org/
Source0:        http://www.prelude-ids.org/download/releases/%name/%{name}-%{version}.tar.gz
Source4:        prelude-manager.init
# They removed this code and provides it only with their "enterprise" version.
# Sorry, but this is GPL, so we use the code from v1.0.1
Patch0:         prelude-manager-1.0.1-missing_relaying.diff
Patch1:		prelude-manager-automake-1.13.patch
Patch2:		prelude-manager-1.0.2-glibc-2.17.patch
Requires:       prelude-tools
Requires(post): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  rpm-helper
Requires(preun): rpm-helper
Requires:       tcp_wrappers
BuildRequires:  autoconf automake libtool
BuildRequires:  chrpath
BuildRequires:  gnutls-devel
BuildRequires:  prelude-devel
BuildRequires:  preludedb-devel
BuildRequires:  tcp_wrappers-devel
BuildRequires:  libxml2-devel
Obsoletes:      prelude-doc <= %{version}-%{release}
Obsoletes:      prelude < %{version}-%{release}
Provides:       prelude = %{version}-%{release}

%description
Prelude Manager is the main program of the Prelude Hybrid IDS
suite. It is a multithreaded server which handles connections from
the Prelude sensors. It is able to register local or remote
sensors, let the operator configure them remotely, receive alerts,
and store alerts in a database or any format supported by
reporting plugins, thus providing centralized logging and
analysis. It also provides relaying capabilities for failover and
replication. The IDMEF standard is used for alert representation.
Support for filtering plugins allows you to hook in different
places in the Manager to define custom criteria for alert relaying
and logging.

%package        db-plugin
Summary:        Database report plugin for Prelude IDS Manager
Group:          System/Servers
Requires:       %{name} = %{version}-%{release}

%description db-plugin
Prelude Manager is the main program of the Prelude Hybrid IDS
suite. It is a multithreaded server which handles connections from
the Prelude sensors. It is able to register local or remote
sensors, let the operator configure them remotely, receive alerts,
and store alerts in a database or any format supported by
reporting plugins, thus providing centralized logging and
analysis. It also provides relaying capabilities for failover and
replication. The IDMEF standard is used for alert representation.
Support for filtering plugins allows you to hook in different
places in the Manager to define custom criteria for alert relaying
and logging.

This plugin authorize prelude-manager to write to database

%package        xml-plugin
Summary:        XML report plugin for Prelude IDS Manager
Group:          System/Servers
Requires:       %{name} = %{version}-%{release}

%description xml-plugin
Prelude Manager is the main program of the Prelude Hybrid IDS
suite. It is a multithreaded server which handles connections from
the Prelude sensors. It is able to register local or remote
sensors, let the operator configure them remotely, receive alerts,
and store alerts in a database or any format supported by
reporting plugins, thus providing centralized logging and
analysis. It also provides relaying capabilities for failover and
replication. The IDMEF standard is used for alert representation.
Support for filtering plugins allows you to hook in different
places in the Manager to define custom criteria for alert relaying
and logging.

This plugin adds XML logging capabilities to the Prelude IDS
Manager.

%package devel
Summary:        Libraries, includes, etc. to develop Prelude IDS Manager plugins
Group:          Development/C
Requires:       %{name} = %{version}-%{release}
Requires:       %{name}-db-plugin = %{version}-%{release}
Requires:       %{name}-xml-plugin = %{version}-%{release}

%description devel
Prelude Manager is the main program of the Prelude Hybrid IDS
suite. It is a multithreaded server which handles connections from
the Prelude sensors. It is able to register local or remote
sensors, let the operator configure them remotely, receive alerts,
and store alerts in a database or any format supported by
reporting plugins, thus providing centralized logging and
analysis. It also provides relaying capabilities for failover and
replication. The IDMEF standard is used for alert representation.
Support for filtering plugins allows you to hook in different
places in the Manager to define custom criteria for alert relaying
and logging.

Install this package if you want to build Prelude IDS Manager
Plugins.

%prep

%setup -q
%apply_patches
%{__perl} -pi -e "s|\@prefix\@%{_logdir}/|%{_logdir}/%{name}/|g" %{name}.conf*
%{__perl} -pi -e "s|/lib\b|/%{_lib}|g" configure.in

cp %{SOURCE4} prelude-manager.init

%build
autoreconf -fi
%configure2_5x \
    --disable-static \
    --enable-shared \
    --localstatedir=%{_var} \
    --with-libprelude-prefix=%{_prefix} \
    --with-libpreludedb-prefix=%{_prefix} \
    --with-xml-prefix=%{_prefix} \
    --with-xml-exec-prefix=%{_prefix}

# fix linkage to the shared wrapper libs
%{_bindir}/find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|^LIBWRAP_LIBS.*|LIBWRAP_LIBS = -L%{_libdir} -lwrap -lnsl|g"
%{_bindir}/find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|-L%{_libdir} %{_libdir}/libwrap\.a -lnsl|-L%{_libdir} -lwrap -lnsl|g"

%make

%install

%makeinstall_std

install -d %{buildroot}%{_var}/run/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}
install -d %{buildroot}%{_sysconfdir}/prelude/profile/%{name}
install -d %{buildroot}%{_var}/spool/%{name}/scheduler

install -d %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/%{name} %{buildroot}%{_sbindir}/%{name}

%{_bindir}/chrpath -d %{buildroot}%{_libdir}/%{name}/reports/db.so

# install init script
install -d %{buildroot}%{_initrddir}
install -m0755 prelude-manager.init %{buildroot}%{_initrddir}/%{name}

# fix logrotate stuff
install -d %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
%{_logdir}/%{name}/prelude.log %{_logdir}/%{name}/prelude-xml.log {
    missingok
    postrotate
        [ -f %{_var}/lock/subsys/%{name} ] && %{_initrddir}/%{name} restart
    endscript
}
EOF

# make the logdir
install -d %{buildroot}%{_logdir}/%{name}
/bin/touch %{buildroot}%{_logdir}/%{name}/prelude.log
/bin/touch %{buildroot}%{_logdir}/%{name}/prelude-xml.log

# fix a README.urpmi
cat > README.urpmi << EOF
If you want database support (required for prewikka),
you should install a preludedb package such as preludedb-mysql and
then do something like the following:

%{_bindir}/mysqladmin create prelude
echo "GRANT ALL PRIVILEGES ON prelude.* TO prelude@'localhost' IDENTIFIED BY 'prelude';" | %{_bindir}/mysql -h localhost
%{_bindir}/mysql -h localhost -u prelude prelude -p < %{_datadir}/libpreludedb/classic/mysql.sql
%{_bindir}/mysql -h localhost -u prelude prelude -p < %{_datadir}/libpreludedb/classic/addIndices.sql
EOF

rm -f %{buildroot}%{_libdir}/%{name}/filters/*.*a
rm -f %{buildroot}%{_libdir}/%{name}/reports/*.*a
rm -f %{buildroot}%{_libdir}/%{name}/decodes/*.*a

%post
%create_ghostfile %{_logdir}/prelude-manager/prelude.log prelude-manager prelude-manager 640
%create_ghostfile %{_logdir}/prelude-manager/prelude-xml.log prelude-manager prelude-manager 640
[ ! -f %{_sysconfdir}/prelude/profile/%{name}/analyzerid ] && [ -x %{_bindir}/prelude-adduser ] && \
  %{_bindir}/prelude-adduser add prelude-manager --uid `%{__id} -u prelude-manager` --gid `%{__id} -g prelude-manager` >/dev/null 2>&1 || :
%_post_service %{name}

%preun
%_preun_service %{name}

%pre
%_pre_useradd prelude-manager %{_localstatedir}/lib/%{name} /bin/false

%postun
%_postun_userdel prelude-manager

%files
%doc AUTHORS COPYING ChangeLog HACKING.README NEWS README README.urpmi
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0755,root,root) %{_sbindir}/%{name}
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/decodes
%dir %{_libdir}/%{name}/filters
%dir %{_libdir}/%{name}/reports
%attr(0755,root,root) %{_libdir}/%{name}/filters/idmef-criteria.so
%attr(0755,root,root) %{_libdir}/%{name}/filters/thresholding.so
%attr(0755,root,root) %{_libdir}/%{name}/reports/debug.so
%attr(0755,root,root) %{_libdir}/%{name}/reports/relaying.so
%attr(0755,root,root) %{_libdir}/%{name}/reports/smtp.so
%attr(0755,root,root) %{_libdir}/%{name}/reports/textmod.so
%attr(0755,root,root) %{_libdir}/%{name}/decodes/normalize.so
%attr(0750,prelude-manager,prelude-manager) %dir %{_var}/spool/%{name}
%attr(0750,prelude-manager,prelude-manager) %dir %{_var}/spool/%{name}/scheduler
%dir %attr(0750,prelude-manager,prelude-manager) %{_logdir}/%{name}
%dir %attr(0750,prelude-manager,prelude-manager) %{_var}/run/%{name}
%ghost %attr(0640,prelude-manager,prelude-manager) %{_logdir}/%{name}/prelude.log
%ghost %attr(0640,prelude-manager,prelude-manager) %{_logdir}/%{name}/prelude-xml.log
%dir %attr(0750,prelude-manager,prelude-manager) %{_localstatedir}/lib/%{name}
%dir %attr(0750,prelude-manager,prelude-manager) %{_sysconfdir}/prelude/profile/%{name}
%dir %{_sysconfdir}/%{name}
%attr(0640,root,prelude-manager) %config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_mandir}/man1/prelude-manager.1*

%files db-plugin
%attr(0755,root,root) %{_libdir}/%{name}/reports/db.so

%files xml-plugin
%attr(0755,root,root) %{_libdir}/%{name}/reports/xmlmod.so
%{_datadir}/%{name}/xmlmod/idmef-message.dtd

%files devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h


%changelog
* Tue Jul 17 2012 Oden Eriksson <oeriksson@mandriva.com> 1.0.2-1
+ Revision: 810011
- bump release
- typo
- the previous patch was incomplete
- 1.0.2

* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.1-2
+ Revision: 667823
- mass rebuild

* Sat Nov 27 2010 Funda Wang <fwang@mandriva.org> 1.0.1-1mdv2011.0
+ Revision: 601782
- update to new version 1.0.1

* Sun Apr 25 2010 Funda Wang <fwang@mandriva.org> 1.0.0-1mdv2010.1
+ Revision: 538664
- New version 1.0.0

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9.15-2mdv2010.1
+ Revision: 523722
- rebuilt for 2010.1

* Sat Jul 11 2009 Frederik Himpe <fhimpe@mandriva.org> 0.9.15-1mdv2010.0
+ Revision: 394824
- update to new version 0.9.15

* Sat May 30 2009 Funda Wang <fwang@mandriva.org> 0.9.14.2-2mdv2010.0
+ Revision: 381472
- use pkgconfig to detect gnutls

* Sat Aug 30 2008 Jérôme Soyer <saispo@mandriva.org> 0.9.14.2-1mdv2009.0
+ Revision: 277552
- New release

* Wed Aug 06 2008 Funda Wang <fwang@mandriva.org> 0.9.14.1-1mdv2009.0
+ Revision: 264154
- New version 0.9.14.1

* Fri Jul 18 2008 Funda Wang <fwang@mandriva.org> 0.9.14-1mdv2009.0
+ Revision: 238170
- add missing file
- New version 0.9.14

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 0.9.11-2mdv2009.0
+ Revision: 225059
- rebuild

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Tue Feb 05 2008 Funda Wang <fwang@mandriva.org> 0.9.11-1mdv2008.1
+ Revision: 162771
- New version 0.9.11

* Tue Jan 22 2008 Funda Wang <fwang@mandriva.org> 0.9.10-3mdv2008.1
+ Revision: 156064
- rebuild against latest gnutls

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Oct 30 2007 David Walluck <walluck@mandriva.org> 0.9.10-2mdv2008.1
+ Revision: 103867
- fix BuildRequires

  + Jérôme Soyer <saispo@mandriva.org>
    - New release

* Sat Aug 04 2007 David Walluck <walluck@mandriva.org> 0.9.9-1mdv2008.0
+ Revision: 58857
- 0.9.9

* Sat Jun 23 2007 David Walluck <walluck@mandriva.org> 0.9.8-6mdv2008.0
+ Revision: 43507
- fix call to prelude-adduser

* Wed May 16 2007 David Walluck <walluck@mandriva.org> 0.9.8-5mdv2008.0
+ Revision: 27435
- create /var/spool/prelude-manager/scheduler
- fix prelude-manager location in prelude-manager.init
- fix prelude obsoletes version
- require on release
- devel package requires %%{name}-db-plugin and %%{name}-xml-plugin
- create %%{_sysconfdir}/prelude/profile/%%{name}
- run %%{_bindir}/prelude-adduser in %%post if necessary

* Wed May 16 2007 David Walluck <walluck@mandriva.org> 0.9.8-4mdv2008.0
+ Revision: 27271
- add requires on rpm-helper where needed
- give full path to prelude-adduser in README.urpmi

* Wed May 16 2007 David Walluck <walluck@mandriva.org> 0.9.8-3mdv2008.0
+ Revision: 27268
- fix spelling and LSB-compliance in prelude-manager.init
- add ghost prelude-xml.log
- set strict permissions in file list
- move prelude-manager to %%{_sbindir}
- don't run prelude-manager as root but as prelude-manager user
- update install notes in README.urpmi

* Wed May 02 2007 David Walluck <walluck@mandriva.org> 0.9.8-1mdv2008.0
+ Revision: 20614
- add new threshold filter
- 0.9.8

* Fri Mar 16 2007 David Walluck <walluck@mandriva.org> 0.9.7.2-1mdv2007.1
+ Revision: 145271
- 0.9.7.2

* Sun Jan 07 2007 David Walluck <walluck@mandriva.org> 0.9.7.1-1mdv2007.1
+ Revision: 105102
- 0.9.7.1

* Sun Oct 22 2006 David Walluck <walluck@mandriva.org> 0.9.6.1-4mdv2007.1
+ Revision: 71650
- update README.urpmi
- add database notes to README.urpmi

* Thu Oct 19 2006 David Walluck <walluck@mandriva.org> 0.9.6.1-2mdv2007.1
+ Revision: 71047
- fix build
- 0.9.6.1
- Import prelude-manager

* Fri Jun 16 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.5-1mdv2007.0
- 0.9.5 (Major bugfixes)

* Thu Mar 30 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.4.1-1mdk
- 0.9.4.1 (Major bugfixes)

* Sat Mar 18 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.4-1mdk
- 0.9.4 (Major bugfixes)

* Thu Feb 09 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.3-2mdk
- fix deps (#21080)

* Thu Feb 09 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.3-1mdk
- 0.9.3 (Major bugfixes)

* Tue Jan 31 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.2-1mdk
- 0.9.2 (Major bugfixes)

* Wed Jan 11 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.1-2mdk
- fix deps

* Tue Jan 10 2006 Oden Eriksson <oeriksson@mandriva.com> 0.9.1-1mdk
- 0.9.1

* Sun Nov 13 2005 Oden Eriksson <oeriksson@mandriva.com> 0.8.10-5mdk
- rebuilt against openssl-0.9.8a

* Sun Oct 30 2005 Oden Eriksson <oeriksson@mandriva.com> 0.8.10-4mdk
- rebuilt against MySQL-5.0.15

* Thu Apr 21 2005 Oden Eriksson <oeriksson@mandriva.com> 0.8.10-3mdk
- rebuilt against new postgresql libs

* Tue Jan 25 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 0.8.10-2mdk
- rebuilt against MySQL-4.1.x and PostgreSQL-8.x system libs
- fix conflicting declaration with MySQL-4.1.x
- fix deps

* Tue Jul 27 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.8.10-1mdk
- 0.8.10
- add docs
- drop P0 & P1 (fixed upstream)
