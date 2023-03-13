%define keepstatic 1
%define gcc_target x86_64-generic-linux
%define libstdcxx_maj 6
%define libstdcxx_full 6.0.26
%define isl_version 0.16.1
%define gccver 11
%define gccpath gcc-11.3.0
# Highest optimisation ABI we target
%define mtune haswell

# Lowest compatible ABI (must be lowest of current targets & OBS builders)
# avoton (silvermont target) && ivybridge (OBS builders) = westmere
%define march westmere

Name     : gcc11
Version  : 11.3.0
Release  : 1347
URL      : http://www.gnu.org/software/gcc/
Source0  : https://gcc.gnu.org/pub/gcc/releases/gcc-11.3.0/gcc-11.3.0.tar.xz
Source1  : https://gcc.gnu.org/pub/gcc/infrastructure/isl-0.16.1.tar.bz2
Source2  : DATESTAMP
Source3  : REVISION
Summary  : GNU cc and gcc C compilers
Group    : Development/Tools
License  : BSD-3-Clause BSL-1.0 GFDL-1.2 GFDL-1.3 GPL-2.0 GPL-3.0 LGPL-2.1 LGPL-3.0 MIT


Patch0   : gcc-stable-branch.patch
Patch1   : 0001-Fix-stack-protection-issues.patch
Patch2   : openmp-vectorize-v2.patch
Patch3   : fortran-vector-v2.patch
Patch5   : optimize.patch
Patch9   : gomp-relax.patch
Patch14  : arch-native-override.patch
Patch15  : 0001-Ignore-Werror-if-GCC_IGNORE_WERROR-environment-varia.patch
Patch16  : 0001-Always-use-z-now-when-linking-with-pie.patch
Patch19  : tune-inline.patch
Patch20  : vectorcost.patch

Patch30  : gcc-hj-latest.patch

# cves: 1xx


BuildRequires : bison
BuildRequires : flex
BuildRequires : gmp-dev
BuildRequires : libstdc++
BuildRequires : libunwind-dev
BuildRequires : mpc-dev
BuildRequires : mpfr-dev
BuildRequires : pkgconfig(zlib)
BuildRequires : sed
BuildRequires : texinfo
BuildRequires : dejagnu
BuildRequires : expect
BuildRequires : autogen
BuildRequires : guile
BuildRequires : tcl
BuildRequires : valgrind-dev
BuildRequires : libxml2-dev
BuildRequires : libxslt
BuildRequires : graphviz
BuildRequires : gdb-dev
BuildRequires : procps-ng
BuildRequires : docbook-xml docbook-utils doxygen
BuildRequires : util-linux


%description
GNU cc and gcc C compilers.

%package dev
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          devel
Requires:       %{name} = %{version}-%{release}
Requires:       gcc11-libs-math = %{version}-%{release}

%description dev
GNU cc and gcc C compilers dev files

%package libs-math
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          libs

%description libs-math
GNU cc and gcc C compilers.


%prep
%setup -q -n %{gccpath}
%patch0 -p1

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch5 -p1
%patch9 -p1

%patch14 -p1

%patch15 -p1
%patch16 -p1
%patch19 -p1
%patch20 -p1

%patch30 -p1


%build

# Live in the gcc source tree
tar xf %{SOURCE1} && ln -sf isl-%{isl_version} isl

# Update the DATESTAMP and add a revision
tee `find -name DATESTAMP` > /dev/null < %{SOURCE2}
cp %{SOURCE3} gcc/

rm -rf ../gcc-build
mkdir ../gcc-build
pushd ../gcc-build
unset CFLAGS
unset CXXFLAGS
export CFLAGS="-march=westmere -g1 -O3 -fstack-protector -Wl,-z -Wl,now -Wl,-z -Wl,relro  -Wl,-z,max-page-size=0x1000 -mtune=skylake"
export CXXFLAGS="-march=westmere -g1 -O3  -Wl,-z,max-page-size=0x1000 -mtune=skylake"
export CFLAGS_FOR_TARGET="$CFLAGS"
export CXXFLAGS_FOR_TARGET="$CXXFLAGS"
export FFLAGS_FOR_TARGET="$FFLAGS"

export CPATH=/usr/include
export LIBRARY_PATH=/usr/lib64

../%{gccpath}/configure \
    --program-suffix="-11" \
    --prefix=/usr \
    --with-pkgversion='Clear Linux OS for Intel Architecture'\
    --libdir=/usr/lib64 \
    --enable-libstdcxx-pch\
    --libexecdir=/usr/lib64 \
    --with-system-zlib\
    --enable-shared\
    --enable-gnu-indirect-function \
    --disable-vtable-verify \
    --enable-threads=posix\
    --enable-__cxa_atexit\
    --enable-plugin\
    --enable-ld=default\
    --enable-clocale=gnu\
    --disable-multiarch\
    --disable-multilib\
    --enable-lto\
    --disable-werror \
    --enable-linker-build-id \
    --build=%{gcc_target}\
    --target=%{gcc_target}\
    --enable-languages="c,c++" \
    --enable-bootstrap \
    --with-ppl=yes \
    --with-isl \
    --includedir=/usr/include \
    --exec-prefix=/usr \
    --with-glibc-version=2.19 \
    --disable-libunwind-exceptions \
    --with-gnu-ld \
    --with-tune=haswell \
    --with-arch=westmere \
    --enable-cet \
    --disable-libmpx \
    --with-gcc-major-version-only \
    --enable-default-pie

make -O %{?_smp_mflags} bootstrap

popd


%check
#pushd ../gcc-build
#export CHECK_TEST_FRAMEWORK=1
#make -O -k  %{?_smp_mflags} check  || :
#popd


%install
export CPATH=/usr/include
export LIBRARY_PATH=/usr/lib64

pushd ../gcc-build
%make_install
cd -

find %{buildroot}/usr/ -name libiberty.a | xargs rm -f
find %{buildroot}/usr/ -name libiberty.h | xargs rm -f

chmod a+x %{buildroot}/usr/bin
chmod a+x %{buildroot}/usr/lib64
find %{buildroot}/usr/lib64 %{buildroot}/usr/lib*/gcc -name '*.so*' -print0 | xargs -r0 chmod 755
find %{buildroot}/usr/lib64 %{buildroot}/usr/lib*/gcc -name '*.o' -print0 | xargs -r0 chmod 644

rm -rf %{buildroot}/usr/share/locale

rm -f %{buildroot}/usr/bin/abifiles.list
rm -f %{buildroot}/usr/bin/x86_64-generic-linux-gcc-tmp
rm -f %{buildroot}/usr/lib64/libatomic.so
rm -f %{buildroot}/usr/lib64/libitm.so
rm -f %{buildroot}/usr/lib64/libitm.spec
rm -f %{buildroot}/usr/lib64/libquadmath.so
rm -f %{buildroot}/usr/lib64/libstdc++.so
rm -rf %{buildroot}/usr/share/info
rm -rf %{buildroot}/usr/share/man
rm -rf %{buildroot}/usr/lib64/libsanitizer.spec

rm -f %{buildroot}/usr/lib64/libatomic.so.1
rm -f %{buildroot}/usr/lib64/libatomic.so.1.2.0
rm -f %{buildroot}/usr/lib64/libcc1.so
rm -f %{buildroot}/usr/lib64/libcc1.so.0
rm -f %{buildroot}/usr/lib64/libcc1.so.0.0.0
rm -f %{buildroot}/usr/lib64/libgcc_s.so
rm -f %{buildroot}/usr/lib64/libgomp.a
rm -f %{buildroot}/usr/lib64/libgomp.so
rm -f %{buildroot}/usr/lib64/libgomp.so.1
rm -f %{buildroot}/usr/lib64/libgomp.so.1.0.0
rm -f %{buildroot}/usr/lib64/libgomp.spec
rm -f %{buildroot}/usr/lib64/libitm.so.1
rm -f %{buildroot}/usr/lib64/libitm.so.1.0.0
rm -f %{buildroot}/usr/lib64/libquadmath.so.0
rm -f %{buildroot}/usr/lib64/libquadmath.so.0.0.0
rm -f %{buildroot}/usr/lib64/libssp.a
rm -f %{buildroot}/usr/lib64/libssp.so
rm -f %{buildroot}/usr/lib64/libssp.so.0
rm -f %{buildroot}/usr/lib64/libssp.so.0.0.0
rm -f %{buildroot}/usr/lib64/libssp_nonshared.a
rm -f %{buildroot}/usr/lib64/libstdc++.a
rm -f %{buildroot}/usr/lib64/libstdc++fs.a
rm -f %{buildroot}/usr/lib64/libsupc++.a

%files
/usr/bin/%{gcc_target}-gcc-ar-11
/usr/bin/%{gcc_target}-gcc-ranlib-11
/usr/bin/%{gcc_target}-gcc-nm-11
/usr/bin/%{gcc_target}-gcc-11
/usr/bin/%{gcc_target}-c++-11
/usr/bin/%{gcc_target}-gcc-%{gccver}
/usr/bin/gcc-11
#/usr/bin/cc-11
/usr/bin/gcc-ar-11
/usr/bin/gcc-nm-11
/usr/bin/gcc-ranlib-11
/usr/bin/gcov-11
/usr/bin/gcov-tool-11
/usr/bin/cpp-11
/usr/bin/gcov-dump-11

#/usr/lib/cpp-11
/usr/bin/lto-dump-11
#/usr/lib64/libvtv*
/usr/lib64/gcc/%{gcc_target}/%{gccver}/include-fixed/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/install-tools/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/include/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/lto1
/usr/lib64/gcc/%{gcc_target}/%{gccver}/lto-wrapper
/usr/lib64/gcc/%{gcc_target}/%{gccver}/collect2
/usr/lib64/gcc/%{gcc_target}/%{gccver}/cc1plus
/usr/lib64/gcc/%{gcc_target}/%{gccver}/liblto_plugin.so
/usr/lib64/gcc/%{gcc_target}/%{gccver}/cc1
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/gtype.state
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/*.so.*
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/include/
/usr/lib64/gcc/%{gcc_target}/%{gccver}/g++-mapper-server
/usr/share/gcc-%{gccver}
%exclude /usr/lib64/*.a
%exclude /usr/lib64/*.o




#gfortran

#g++
/usr/bin/%{gcc_target}-g++-11
/usr/bin/c++-11
/usr/bin/g++-11

# gcc-dev
/usr/lib64/gcc/%{gcc_target}/%{gccver}/liblto_plugin.so
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/*.so

%files dev
# libgcc-s-dev
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/libgcc.a
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtendS.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/libgcc_eh.a
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtprec32.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtend.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtbegin.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtprec80.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtfastmath.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtbeginS.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtprec64.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/crtbeginT.o
/usr/lib64/gcc/x86_64-generic-linux/%{gccver}/libgcov.a
/usr/lib64/gcc/%{gcc_target}/%{gccver}/include/ssp
# gcc-plugin-dev
/usr/lib64/gcc/%{gcc_target}/%{gccver}/plugin/gengtype

# libstdc++
/usr/include/c++/*
%exclude /usr/lib64/libasan.so
%exclude /usr/lib64/libasan.so.6
%exclude /usr/lib64/libasan.so.6.0.0
%exclude /usr/lib64/libgcc_s.so.1
%exclude /usr/lib64/liblsan.so
%exclude /usr/lib64/liblsan.so.0
%exclude /usr/lib64/liblsan.so.0.0.0
%exclude /usr/lib64/libstdc++.so.6
%exclude /usr/lib64/libstdc++.so.6.0.29
%exclude /usr/lib64/libstdc++.so.6.0.29-gdb.py
%exclude /usr/lib64/libtsan.so
%exclude /usr/lib64/libtsan.so.0
%exclude /usr/lib64/libtsan.so.0.0.0
%exclude /usr/lib64/libubsan.so
%exclude /usr/lib64/libubsan.so.1
%exclude /usr/lib64/libubsan.so.1.0.0





#avx2

#avx512
# %exclude /usr/lib64/haswell/avx512_1/libgcc_s.so.1

%files libs-math

#avx2

#avx512
