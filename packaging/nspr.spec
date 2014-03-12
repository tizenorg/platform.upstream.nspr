Name:           nspr
Version:        4.10.2
Release:        0
License:        MPL-2.0
Summary:        Netscape Portable Runtime
Url:            http://www.mozilla.org/projects/nspr/
Group:          Base/Libraries
Source:         ftp://ftp.mozilla.org/pub/nspr/releases/v%{version}/src/nspr-%{version}.tar.bz2
Source1:        baselibs.conf
Source1001: 	nspr.manifest
BuildRequires:  gcc-c++
BuildRequires:  pkg-config
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
NSPR provides platform independence for non-GUI operating system
facilities. These facilities include threads, thread synchronization,
normal file and network I/O, interval timing and calendar time, basic
memory management (malloc and free), and shared library linking.

%package devel
Summary:        Netscape Portable Runtime development files
Group:          Base/Development
Requires:       nspr = %{version}

%description devel
NSPR provides platform independence for non-GUI operating system
facilities. These facilities include threads, thread synchronization,
normal file and network I/O, interval timing and calendar time, basic
memory management (malloc and free), and shared library linking.

%prep
%setup -n nspr-%{version} -q
cp %{SOURCE1001} .

%build
# set buildtime to "last-modification-time"
modified="$(sed -n '/^----/n;s/ - .*$//;p;q' "%{_sourcedir}/%{name}.changes")"
BUILD_STRING="$(date -u -d "${modified}" "+%%F %%T")"
BUILD_TIME="$(date -u -d "${modified}" "+%%s000000")"
#
cd nspr
export CFLAGS="%{optflags}"
./configure --enable-optimize="$CFLAGS" \
            --disable-debug \
%ifarch x86_64 aarch64
	    --enable-64bit \
%endif
	    --libdir=%{_libdir} \
	    --includedir=%{_includedir}/nspr4 \
	    --prefix=%{_prefix}
make SH_DATE="$BUILD_STRING" SH_NOW="$BUILD_TIME" %{?_smp_mflags}
%check
# Run test suite
perl ./pr/tests/runtests.pl 2>&1 | tee output.log
TEST_FAILURES=`grep -c FAILED ./output.log` || :
if [ $TEST_FAILURES -ne 0 ]; then
  echo "error: test suite returned failure(s)"
  exit 1
fi
echo "test suite completed"


%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/nspr
mkdir -p %{buildroot}%{_libdir}/pkgconfig
mkdir -p %{buildroot}%{_includedir}/nspr4
cp nspr/config/nspr-config %{buildroot}%{_bindir}/
cp nspr/config/nspr.pc %{buildroot}%{_libdir}/pkgconfig
cp -L nspr/dist/lib/*.so %{buildroot}%{_libdir}
cp -L nspr/dist/lib/*.a  %{buildroot}%{_libdir}/nspr/
cp -rL nspr/dist/include/nspr/* %{buildroot}%{_includedir}/nspr4/
# #31667
chmod -x %{buildroot}%{_includedir}/nspr4/prvrsion.h

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%manifest %{name}.manifest
%defattr(-, root, root)
%{_libdir}/*.so

%files devel
%manifest %{name}.manifest
%defattr(-, root, root)
%{_bindir}/nspr-config
%{_libdir}/pkgconfig/nspr.pc
%{_includedir}/nspr4/
%exclude %{_includedir}/nspr4/md/*
%{_libdir}/nspr/

%changelog
