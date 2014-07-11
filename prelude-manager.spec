Summary:	Prelude Hybrid Intrusion Detection System Manager
Name:		prelude-manager
Version:	1.0.2
Release:	9
License:	GPLv2+
Group:		System/Servers
Url:		http://www.prelude-ids.org/
Source0:	http://www.prelude-ids.org/download/releases/%{name}/%{name}-%{version}.tar.gz
Source4:	prelude-manager.init
# They removed this code and provides it only with their "enterprise" version.
# Sorry, but this is GPL, so we use the code from v1.0.1
Patch0:		prelude-manager-1.0.1-missing_relaying.diff
Patch1:		prelude-manager-automake-1.13.patch
Patch2:		prelude-manager-1.0.2-glibc-2.17.patch
BuildRequires:	chrpath
BuildRequires:	libtool
BuildRequires:	preludedb-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	pkgconfig(libprelude)
BuildRequires:	pkgconfig(libxml-2.0)
Requires:	prelude-tools
Requires:	tcp_wrappers
Requires(post,postun,pre,preun):	rpm-helper
Obsoletes:	prelude-doc < 1.0.2-7
%rename		prelude

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

#----------------------------------------------------------------------------

%package db-plugin
Summary:	Database report plugin for Prelude IDS Manager
Group:		System/Servers
Requires:	%{name} = %{EVRD}

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

%files db-plugin
%attr(0755,root,root) %{_libdir}/%{name}/reports/db.so

#----------------------------------------------------------------------------

%package xml-plugin
Summary:	XML report plugin for Prelude IDS Manager
Group:		System/Servers
Requires:	%{name} = %{EVRD}

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

%files xml-plugin
%attr(0755,root,root) %{_libdir}/%{name}/reports/xmlmod.so
%{_datadir}/%{name}/xmlmod/idmef-message.dtd

#----------------------------------------------------------------------------

%package devel
Summary:	Libraries, includes, etc. to develop Prelude IDS Manager plugins
Group:		Development/C
Requires:	%{name} = %{EVRD}
Requires:	%{name}-db-plugin = %{EVRD}
Requires:	%{name}-xml-plugin = %{EVRD}

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

%files devel
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h

#----------------------------------------------------------------------------

%prep
%setup -q
%apply_patches
perl -pi -e "s|\@prefix\@%{_logdir}/|%{_logdir}/%{name}/|g" %{name}.conf*
perl -pi -e "s|/lib\b|/%{_lib}|g" configure.in

cp %{SOURCE4} prelude-manager.init
autoreconf -fi

%build
%configure2_5x \
	--disable-static \
	--enable-shared \
	--localstatedir=%{_var} \
	--with-libprelude-prefix=%{_prefix} \
	--with-libpreludedb-prefix=%{_prefix} \
	--with-xml-prefix=%{_prefix} \
	--with-xml-exec-prefix=%{_prefix}

# fix linkage to the shared wrapper libs
find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|^LIBWRAP_LIBS.*|LIBWRAP_LIBS = -L%{_libdir} -lwrap -lnsl|g"
find -name "Makefile" | %{_bindir}/xargs %{__perl} -pi -e "s|-L%{_libdir} %{_libdir}/libwrap\.a -lnsl|-L%{_libdir} -lwrap -lnsl|g"

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

