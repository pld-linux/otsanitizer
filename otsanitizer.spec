# Upstream name is "ots", but this package name is already occupied by Open Text Summarizer project.
# Library is renamed (from upstream libots.a to libotsanitizer.*) to avoid conflict with ots package.
#
# Conditional build:
%bcond_without	static_libs	# static library
%bcond_without	tests		# unit and fuzz testing
#
Summary:	OpenType Sanitizer
Summary(pl.UTF-8):	OpenType Sanitizer - narzędzie poprawiające fonty OpenType
Name:		otsanitizer
Version:	6.1.1
Release:	1
License:	BSD
Group:		Libraries
#Source0Download: https://github.com/khaledhosny/ots/releases
Source0:	https://github.com/khaledhosny/ots/releases/download/v%{version}/ots-%{version}.tar.gz
# Source0-md5:	8b6653d7fe0a72f67466d23690e33141
Patch0:		ots-system-libs.patch
URL:		https://github.com/khaledhosny/ots
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake >= 1:1.11
BuildRequires:	freetype-devel >= 2
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	libtool >= 2:2
BuildRequires:	lz4-devel
BuildRequires:	pkgconfig >= 1:0.20
BuildRequires:	woff2-devel
BuildRequires:	zlib-devel
%if %{with tests}
BuildRequires:	gtest-devel
BuildRequires:	libasan-devel
BuildRequires:	libubsan-devel
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The OpenType Sanitizer (OTS) parses and serializes OpenType files
(OTF, TTF) and WOFF and WOFF2 font files, validating them and
sanitizing them as it goes.

%description -l pl.UTF-8
OpenType Sanitizer (OTS) analizuje i serializuje pliki fontów OpenType
(OTF, TTF) oraz WOFF/WOFF2, sprawdzając ich poprawność i naprawiając
niektóre błędy.

%package devel
Summary:	Header files for OpenType Sanitizer library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki OpenType Sanitizer
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	freetype-devel >= 2
Requires:	lz4-devel
Requires:	woff2-devel
Requires:	zlib-devel

%description devel
Header files for OpenType Sanitizer library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki OpenType Sanitizer.

%package static
Summary:	Static OpenType Sanitizer library
Summary(pl.UTF-8):	Statyczna biblioteka OpenType Sanitizer
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static OpenType Sanitizer library.

%description static -l pl.UTF-8
Statyczna biblioteka OpenType Sanitizer.

%prep
%setup -q -n ots-%{version}
%patch0 -p1

# extend blacklist by PLD supplied fonts known to cause test failures
cat >>tests/BLACKLIST.txt <<EOF
# LiTE package; cmap: Bad cmap subtable; Failed to parse table
whiterabbit.ttf
EOF

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
%if %{without tests}
	ax_cv_check_cflags___fsanitize_address=no \
	ax_cv_check_cflags___fsanitize_undefined=no \
%endif
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static}
%{__make}

%if %{with tests}
%{__make} check || (cat test-suite.log && false)
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE README docs/{DesignDoc,HowToFix}.md
%attr(755,root,root) %{_bindir}/ots-idempotent
%attr(755,root,root) %{_bindir}/ots-perf
%attr(755,root,root) %{_bindir}/ots-sanitize
%attr(755,root,root) %{_bindir}/ots-side-by-side
%attr(755,root,root) %{_bindir}/ots-validator-checker
%attr(755,root,root) %{_libdir}/libotsanitizer.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libotsanitizer.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libotsanitizer.so
%{_libdir}/libotsanitizer.la
%{_includedir}/ots

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libotsanitizer.a
%endif
