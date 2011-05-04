Name:           prelude-manager
Version:        1.0.1
Release:        %mkrel 2
Summary:        Prelude Hybrid Intrusion Detection System Manager
License:        GPLv2+
Group:          System/Servers
URL:            http://www.prelude-ids.org/
Source0:        http://www.prelude-ids.org/download/releases/%name/%{name}-%{version}.tar.gz
Source4:        prelude-manager.init
Requires:       prelude-tools
Requires(post): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  rpm-helper
Requires(preun): rpm-helper
Requires:       tcp_wrappers
BuildRequires:  automake1.8
BuildRequires:  autoconf2.5
BuildRequires:  chrpath
BuildRequires:  gnutls-devel
BuildRequires:  prelude-devel
BuildRequires:  preludedb-devel
BuildRequires:  tcp_wrappers-devel
BuildRequires:  libxml2-devel
Obsoletes:      prelude-doc <= %{version}-%{release}
Obsoletes:      prelude < %{version}-%{release}
Provides:       prelude = %{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

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
%{__perl} -pi -e "s|\@prefix\@%{_logdir}/|%{_logdir}/%{name}/|g" %{name}.conf*
%{__perl} -pi -e "s|/lib\b|/%{_lib}|g" configure.in

%build
%{_bindir}/autoreconf
%{configure2_5x} --enable-static \
                 --enable-shared \
                 --localstatedir=%{_var} \
                 --with-libprelude-prefix=%{_prefix} \
                 --with-libpreludedb-prefix=%{_prefix} \
                 --with-xml-prefix=%{_prefix} \
                 --with-xml-exec-prefix=%{_prefix}

# fix linkage to the shared wrapper libs
%{_bindir}/find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|^LIBWRAP_LIBS.*|LIBWRAP_LIBS = -L%{_libdir} -lwrap -lnsl|g"
%{_bindir}/find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|-L%{_libdir} %{_libdir}/libwrap\.a -lnsl|-L%{_libdir} -lwrap -lnsl|g"

%{make}

%install
%{__rm} -rf %{buildroot}

%{makeinstall_std}

%{__mkdir_p} %{buildroot}%{_var}/run/%{name}
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/prelude/profile/%{name}
%{__mkdir_p} %{buildroot}%{_var}/spool/%{name}/scheduler

%{__mkdir_p} %{buildroot}%{_sbindir}
%{__mv} %{buildroot}%{_bindir}/%{name} %{buildroot}%{_sbindir}/%{name}

%{_bindir}/chrpath -d %{buildroot}%{_libdir}/%{name}/reports/db.so

# install init script
%{__mkdir_p} %{buildroot}%{_initrddir}
%{__install} -m 0755 %{SOURCE4} %{buildroot}%{_initrddir}/%{name}

# fix logrotate stuff
%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__cat} > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
%{_logdir}/%{name}/prelude.log %{_logdir}/%{name}/prelude-xml.log {
    missingok
    postrotate
        [ -f %{_var}/lock/subsys/%{name} ] && %{_initrddir}/%{name} restart
    endscript
}
EOF

# make the logdir
%{__mkdir_p} %{buildroot}%{_logdir}/%{name}
/bin/touch %{buildroot}%{_logdir}/%{name}/prelude.log
/bin/touch %{buildroot}%{_logdir}/%{name}/prelude-xml.log

# fix a README.urpmi
%{__cat} > README.urpmi << EOF
If you want database support (required for prewikka),
you should install a preludedb package such as preludedb-mysql and
then do something like the following:

%{_bindir}/mysqladmin create prelude
echo "GRANT ALL PRIVILEGES ON prelude.* TO prelude@'localhost' IDENTIFIED BY 'prelude';" | %{_bindir}/mysql -h localhost
%{_bindir}/mysql -h localhost -u prelude prelude -p < %{_datadir}/libpreludedb/classic/mysql.sql
%{_bindir}/mysql -h localhost -u prelude prelude -p < %{_datadir}/libpreludedb/classic/addIndices.sql
EOF

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

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
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
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_libdir}/%{name}/reports/db.so

%files xml-plugin
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_libdir}/%{name}/reports/xmlmod.so
%{_datadir}/%{name}/xmlmod/idmef-message.dtd

%files devel
%defattr(0644,root,root,0755)
%doc AUTHORS COPYING ChangeLog HACKING.README NEWS README
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/%{name}/filters/*.a
%attr(0755,root,root) %{_libdir}/%{name}/filters/*.la
%{_libdir}/%{name}/reports/*.a
%attr(0755,root,root) %{_libdir}/%{name}/reports/*.la
%{_libdir}/%{name}/decodes/normalize.a
%attr(0755,root,root) %{_libdir}/%{name}/decodes/normalize.la
