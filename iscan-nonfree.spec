%define ver_data 1.36.0
%define ver_main 2.30.1
%define plugindir %(gimptool-2.0 --gimpplugindir 2> /dev/null)
%define oname iscan

Name:           iscan-nonfree
Version:        %{ver_main}
Release:        1
Summary:        EPSON Image Scan! front-end for scanners and all-in-ones
License:        GPL-2.0 and AVASYSPL
Group:          System/Kernel and hardware
Url:            http://download.ebz.epson.net/dsc/search/01/search/?OSC=LX
Source0:        https://download3.ebz.epson.net/dsc/f/03/00/03/61/59/a3f8b8d60e8702a1c5bf3977d018cc2336e308a8/%{oname}_%{version}-1.tar.gz
Source1:        https://download3.ebz.epson.net/dsc/f/03/00/03/61/59/646738a219f7354bf3268897385f6ce48c0776bf/%{oname}-data_%{ver_data}-1.tar.gz
Source2:        epkowa.conf
Source100:	%{name}.rpmlintrc
# PATCH-FIX-UPSTREAM libpng15.patch (export from arch) -- Build iscan against libpng15 by giovanni
Patch0:         libpng15.patch
BuildRequires:  gettext
BuildRequires:  jpeg-devel
BuildRequires:  libtool
BuildRequires:  systemd
BuildRequires:  pkgconfig(gimp-2.0)
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:  pkgconfig(libpng16)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(sane-backends)
BuildRequires:  pkgconfig(udev)
Requires:       %{oname}-data
Requires(post): systemd
Conflicts:	sane-backends-iscan

%description
Image Scan! is a graphical scanner utility for people that do not need all
the bells and whistles provided by several of the other utilities out there
(xsane, QuiteInsane, Kooka).

At the moment it only supports SEIKO EPSON scanners and all-in-ones.
However, the scanner driver it provides can be used by any other SANE
standard compliant scanner utility.

Note that several scanners require a non-free plugin before they can be
used with this software

%package		data
Version:        1.36.0
Summary:        Image Scan! for Linux data files
Group:          System/Kernel and hardware
Requires:       libxslt
BuildArch:      noarch

%description	data
Provides the necessary support files for Image Scan! for Linux, including
device information and policy file generation logic.

Image Scan! for Linux will not function without this package.

%prep
%setup -q -n %{oname}-%{ver_main}
%setup -q -D -T -a 1 -n %{oname}-%{ver_main}

%patch0

# Fix for CXX ABI different than 1002 (export from arch)
ln -s libesmod-x86_64.c2.so non-free/libesmod-x86_64.so

%build
# Build iscan
export LDFLAGS="${LDFLAGS} -ldl -lpng16"
%configure2_5x \
  --sbindir=%{_bindir} \
  --enable-dependency-reduction \
  --enable-frontend \
  --enable-jpeg \
  --enable-tiff \
  --enable-png \
  --enable-gimp \
  --enable-static=no

%make

# Build data
cd %{oname}-data-%{ver_data}
%configure2_5x --libdir="%{_prefix}/lib"
%make
%make %{oname}-data.hwdb

%install
# iscan: install files
make DESTDIR=%{buildroot} install %{?_smp_mflags}
install -d %{buildroot}%{plugindir}/plug-ins
ln -s %{_bindir}/iscan %{buildroot}%{_libdir}/gimp/2.0/plug-ins/iscan
install -D -m 0644 backend/epkowa.conf %{buildroot}%{_sysconfdir}/sane.d/epkowa.conf
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sane.d/dll.d/epkowa.conf

find %{buildroot} \( -name \*.la -o -name \*.so  \) -exec rm {} \;

%find_lang %{oname}

# data: install files
cd %{oname}-data-%{ver_data}
make DESTDIR=%{buildroot} install %{?_smp_mflags}

install -D -m 0644 %{oname}-data.hwdb %{buildroot}/%{_udevhwdbdir}/%{oname}-data.hwdb

%post
/sbin/ldconfig
%udev_hwdb_update

%postun
/sbin/ldconfig
if [ $1 -eq 0 ]; then
	%udev_hwdb_update
fi

%files -f %{oname}.lang
%defattr(-,root,root,-)
%doc NEWS README AUTHORS COPYING
%doc non-free/AVASYSPL.en.txt
%doc doc/xinetd.sane
%dir %{_sysconfdir}/sane.d
%dir %{_sysconfdir}/sane.d/dll.d
%config %{_sysconfdir}/sane.d/epkowa.conf
%config %{_sysconfdir}/sane.d/dll.d/epkowa.conf
%{_bindir}/%{oname}
%{_bindir}/%{oname}-registry
%{_libdir}/libesmod.so*
%{_libdir}/sane/libsane-epkowa.so*
%{_libdir}/gimp/2.0/plug-ins/iscan
%{_mandir}/man1/iscan.1.*
%{_mandir}/man5/sane-epkowa.5.*
%{_mandir}/man8/iscan-registry.8.*

%files data
%defattr(-, root, root)
%doc %{oname}-data-%{ver_data}/COPYING
%doc %{oname}-data-%{ver_data}/NEWS
%doc %{oname}-data-%{ver_data}/KNOWN-PROBLEMS
%doc %{oname}-data-%{ver_data}/SUPPORTED-DEVICES
%{_prefix}/lib/iscan-data
%{_datadir}/iscan-data
%{_udevhwdbdir}/%{oname}-data.hwdb

