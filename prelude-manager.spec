Name:           prelude-manager
Version:        0.9.8
Release:        %mkrel 1
Summary:        Prelude Hybrid Intrusion Detection System Manager
License:        GPL
Group:          System/Servers
URL:            http://www.prelude-ids.org/
Source0:        http://www.prelude-ids.org/download/releases/%{name}-%{version}.tar.gz
Source1:        http://www.prelude-ids.org/download/releases/%{name}-%{version}.tar.gz.sig
Source2:        http://www.prelude-ids.org/download/releases/%{name}-%{version}.tar.gz.md5
Source3:        http://www.prelude-ids.org/download/releases/%{name}-%{version}.txt
Source4:        prelude-manager.init
Requires:       prelude-tools
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:       tcp_wrappers
BuildRequires:  automake1.8
BuildRequires:  autoconf2.5
BuildRequires:  chrpath
BuildRequires:  libgnutls-devel
BuildRequires:  libprelude-devel
BuildRequires:  libpreludedb-devel
BuildRequires:  libxml2-devel
BuildRequires:  tcp_wrappers-devel
Obsoletes:      prelude >= 0.4.2
Obsoletes:      prelude-doc
Provides:       prelude = %{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Requires:       %{name} = %{version}

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
Requires:       %{name} = %{version}

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
Requires:       %{name} = %{version}

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
export WANT_AUTOCONF_2_5=1
%{_bindir}/autoreconf

%{configure2_5x} \
    --enable-static \
    --enable-shared \
    --localstatedir=%{_var} \
    --with-libprelude-prefix=%{_prefix} \
    --with-libgnutls-prefix=%{_prefix} \
    --with-libpreludedb-prefix=%{_prefix} \
    --with-xml-prefix=%{_prefix} \
    --with-xml-exec-prefix=%{_prefix} 

# fix linkage to the shared wrapper libs
%{_bindir}/find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|^LIBWRAP_LIBS.*|LIBWRAP_LIBS = -L%{_libdir} -lwrap -lnsl|g"
%{_bindir}/find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|-L%{_libdir} %{_libdir}/libwrap\.a -lnsl|-L%{_libdir} -lwrap -lnsl|g"

%{make}

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_libdir}/%{name}/decodes
%{__mkdir_p} %{buildroot}%{_var}/run/%{name}

%{makeinstall_std}

%{_bindir}/chrpath -d %{buildroot}%{_libdir}/%{name}/reports/db.so 

# install init script
%{__mkdir_p} %{buildroot}%{_initrddir}
%{__install} -m 0755 %{SOURCE4} %{buildroot}%{_initrddir}/%{name}

# fix logrotate stuff
%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__cat} > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
%{_logdir}/%{name}/prelude.log {
    missingok
    postrotate
        [ -f %{_var}/lock/subsys/%{name} ] && %{_initrddir}/%{name} restart
    endscript
}
EOF

# make the logdir
%{__mkdir_p} %{buildroot}%{_logdir}/%{name}
/bin/touch %{buildroot}%{_logdir}/%{name}/prelude.log

# fix a README.urpmi
%{__cat} > README.urpmi << EOF
In order to start the prelude-manager service you must configure 
it first. This is not done automatically. To make a basic file 
configuration please run:

prelude-adduser add prelude-manager --uid 0 --gid 0

Additionally, if you want database support (required for prewikka),
you should install a preludedb package such as preludedb-mysql and
then do something like the following:

%{_bindir}/mysqladmin create prelude
echo "GRANT ALL PRIVILEGES ON prelude.* TO prelude@'localhost' IDENTIFIED BY 'prelude';" | %{_bindir}/mysql -h localhost
%{_bindir}/mysql -h localhost -u prelude prelude -p < %{_datadir}/libpreludedb/classic/mysql.sql
EOF

%post
%_post_service %{name}
/bin/touch %{_logdir}/prelude-manager/prelude.log

%preun
%_preun_service %{name}

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog HACKING.README NEWS README README.urpmi
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/%{name}/*.conf
%attr(0755,root,root) %{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/%{name}
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/decodes
%dir %{_libdir}/%{name}/filters
%dir %{_libdir}/%{name}/reports
%{_libdir}/%{name}/filters/idmef-criteria.so
%{_libdir}/%{name}/reports/debug.so
%{_libdir}/%{name}/reports/relaying.so
%{_libdir}/%{name}/reports/textmod.so
%{_libdir}/%{name}/decodes/normalize.so
%attr(0750,root,root) %dir %{_var}/spool/%{name}
%dir %{_logdir}/%{name}
%dir %{_var}/run/%{name}
%ghost %attr(0664,root,root) %{_logdir}/%{name}/prelude.log

%files db-plugin
%defattr(-,root,root)
%{_libdir}/%{name}/reports/db.so

%files xml-plugin
%defattr(-,root,root)
%{_libdir}/%{name}/reports/xmlmod.so
%{_datadir}/%{name}/xmlmod/idmef-message.dtd

%files devel
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog HACKING.README NEWS README
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/%{name}/filters/*.a
%{_libdir}/%{name}/filters/*.la
%{_libdir}/%{name}/reports/*.a
%{_libdir}/%{name}/reports/*.la
%{_libdir}/%{name}/decodes/normalize.a
%{_libdir}/%{name}/decodes/normalize.la


