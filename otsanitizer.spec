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
Version:	8.0.0
Release:	1
License:	BSD
Group:		Libraries
#Source0Download: https://github.com/khaledhosny/ots/releases
Source0:	https://github.com/khaledhosny/ots/releases/download/v%{version}/ots-%{version}.tar.xz
# Source0-md5:	6ee945656c3622b207edc676f9bb696c
Patch0:		ots-system-libs.patch
URL:		https://github.com/khaledhosny/ots
BuildRequires:	freetype-devel >= 2
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	libbrotli-devel
BuildRequires:	lz4-devel
BuildRequires:	meson
BuildRequires:	ninja >= 1.5
BuildRequires:	pkgconfig >= 1:0.20
BuildRequires:	tar >= 1:1.22
BuildRequires:	woff2-devel
BuildRequires:	xz
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
%patch0 -p1 -b .orig

# extend blacklist by PLD supplied fonts known to cause test failures
cat >>tests/BLACKLIST.txt <<EOF
# LiTE package; cmap: Bad cmap subtable; Failed to parse table
whiterabbit.ttf
# fonts-TTF-Google-Droid; Layout: Bad lookup index 8 for lookup 1; Failed to parse feature table 12; GSUB: Failed to parse feature list table; Failed to parse table
DroidNaskh-Bold.ttf
EOF

%build
%meson build

%ninja_build -C build

%if %{with tests}
ninja -C build -v test
%endif

%install
rm -rf $RPM_BUILD_ROOT

%ninja_install -C build

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE README.md docs/{DesignDoc,HowToFix}.md
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
%{_includedir}/ots

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libotsanitizer.a
%endif
