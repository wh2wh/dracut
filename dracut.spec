%define dracutlibdir %{_prefix}/lib/dracut

# Variables must be defined
%define with_nbd                1

# nbd in Fedora only
%if 0%{?rhel} >= 6
%define with_nbd 0
%endif

Name: dracut
Version: xxx
Release: xxx

Summary: Initramfs generator using udev
%if 0%{?fedora} || 0%{?rhel}
Group: System Environment/Base
%endif
%if 0%{?suse_version}
Group: System/Base
%endif

# The entire source code is GPLv2+
# except install/* which is LGPLv2+
License: GPLv2+ and LGPLv2+

URL: https://dracut.wiki.kernel.org/

# Source can be generated by
# http://git.kernel.org/?p=boot/dracut/dracut.git;a=snapshot;h=%{version};sf=tgz
Source0: http://www.kernel.org/pub/linux/utils/boot/dracut/dracut-%{version}.tar.bz2

BuildRequires: bash git

%if 0%{?fedora} || 0%{?rhel}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: pkgconfig
%endif
%if 0%{?fedora}
BuildRequires: bash-completion
BuildRequires: pkgconfig
%endif

%if 0%{?suse_version}
BuildRoot: %{_tmppath}/%{name}-%{version}-build
%endif

%if 0%{?fedora} || 0%{?rhel}
BuildRequires: docbook-style-xsl docbook-dtds libxslt
%endif

%if 0%{?suse_version}
-BuildRequires: docbook-xsl-stylesheets libxslt
%endif

BuildRequires: asciidoc

%if 0%{?fedora} > 12 || 0%{?rhel}
# no "provides", because dracut does not offer
# all functionality of the obsoleted packages
Obsoletes: mkinitrd <= 6.0.93
Obsoletes: mkinitrd-devel <= 6.0.93
Obsoletes: nash <= 6.0.93
Obsoletes: libbdevid-python <= 6.0.93
%endif

%if 0%{?fedora} > 16 || 0%{?rhel} > 6
BuildRequires: systemd-units
%endif

%if 0%{?suse_version} > 9999
Obsoletes: mkinitrd < 2.6.1
Provides: mkinitrd = 2.6.1
%endif

Obsoletes: dracut-kernel < 005
Provides:  dracut-kernel = %{version}-%{release}

Obsoletes: dracut <= 029
Obsoletes: dracut-norescue
Provides:  dracut-norescue

Requires: bash >= 4
Requires: coreutils
Requires: cpio
Requires: filesystem >= 2.1.0
Requires: findutils
Requires: grep
Requires: hardlink
Requires: gzip xz
Requires: kmod
Requires: sed
Requires: kpartx
Requires: tar

%if 0%{?fedora} || 0%{?rhel} > 6
Requires: util-linux >= 2.21
Requires: systemd >= 219
Requires: procps-ng
Conflicts: grubby < 8.23
%else
Requires: udev > 166
Requires: util-linux-ng >= 2.21
%endif

%if 0%{?fedora} || 0%{?rhel} > 6
Conflicts: initscripts < 8.63-1
Conflicts: plymouth < 0.8.0-0.2009.29.09.19.1
%endif

Conflicts: mdadm < 3.2.6-14

%description
dracut contains tools to create a bootable initramfs for 2.6 Linux kernels.
Unlike existing implementations, dracut does hard-code as little as possible
into the initramfs. dracut contains various modules which are driven by the
event-based udev. Having root on MD, DM, LVM2, LUKS is supported as well as
NFS, iSCSI, NBD, FCoE with the dracut-network package.

%package network
Summary: dracut modules to build a dracut initramfs with network support
Requires: %{name} = %{version}-%{release}
Requires: iputils
Requires: iproute
Requires: dhclient
Obsoletes: dracut-generic < 008
Provides:  dracut-generic = %{version}-%{release}

%description network
This package requires everything which is needed to build a generic
all purpose initramfs with network support with dracut.

%if 0%{?fedora} || 0%{?rhel} >= 6 || 0%{?suse_version}
%package fips
Summary: dracut modules to build a dracut initramfs with an integrity check
Requires: %{name} = %{version}-%{release}
Requires: hmaccalc
%if 0%{?rhel} > 5
# For Alpha 3, we want nss instead of nss-softokn
Requires: nss
%else
Requires: nss-softokn
%endif
Requires: nss-softokn-freebl

%description fips
This package requires everything which is needed to build an
initramfs with dracut, which does an integrity check.
%endif

%package fips-aesni
Summary: dracut modules to build a dracut initramfs with an integrity check with aesni-intel
Requires: %{name}-fips = %{version}-%{release}

%description fips-aesni
This package requires everything which is needed to build an
initramfs with dracut, which does an integrity check and adds the aesni-intel kernel module.

%package caps
Summary: dracut modules to build a dracut initramfs which drops capabilities
Requires: %{name} = %{version}-%{release}
Requires: libcap

%description caps
This package requires everything which is needed to build an
initramfs with dracut, which drops capabilities.

%package config-generic
Summary: dracut configuration to turn off hostonly image generation
Requires: %{name} = %{version}-%{release}
Obsoletes: dracut-nohostonly
Provides:  dracut-nohostonly

%description config-generic
This package provides the configuration to turn off the host specific initramfs
generation with dracut and generates a generic image by default.

%package config-rescue
Summary: dracut configuration to turn on rescue image generation
Requires: %{name} = %{version}-%{release}
Obsoletes: dracut <= 029

%description config-rescue
This package provides the configuration to turn on the rescue initramfs
generation with dracut.

%package tools
Summary: dracut tools to build the local initramfs
Requires: %{name} = %{version}-%{release}

%description tools
This package contains tools to assemble the local initrd and host configuration.

%prep
%setup -q -n %{name}-%{version}

%if %{defined PATCH1}
git init
git config user.email "dracut-maint@redhat.com"
git config user.name "Fedora dracut team"
git add .
git commit -a -q -m "%{version} baseline."

# Apply all the patches.
git am -p1 %{patches}
git tag %{version}
%endif

%build
%configure --systemdsystemunitdir=%{_unitdir} --bashcompletiondir=$(pkg-config --variable=completionsdir bash-completion) --libdir=%{_prefix}/lib

make %{?_smp_mflags}

%install
%if 0%{?fedora} || 0%{?rhel}
rm -rf -- $RPM_BUILD_ROOT
%endif
make %{?_smp_mflags} install \
     DESTDIR=$RPM_BUILD_ROOT \
     libdir=%{_prefix}/lib

echo "DRACUT_VERSION=%{version}-%{release}" > $RPM_BUILD_ROOT/%{dracutlibdir}/dracut-version.sh

%if 0%{?fedora} == 0 && 0%{?rhel} == 0 && 0%{?suse_version} == 0
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/01fips
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/02fips-aesni
%endif

%if %{defined _unitdir}
# for systemd, better use systemd-bootchart
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/00bootchart
%endif

# we do not support dash in the initramfs
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/00dash

# remove gentoo specific modules
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/50gensplash

%if %{defined _unitdir}
# with systemd IMA and selinux modules do not make sense
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/96securityfs
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/97masterkey
rm -fr -- $RPM_BUILD_ROOT/%{dracutlibdir}/modules.d/98integrity
%endif

mkdir -p $RPM_BUILD_ROOT/boot/dracut
mkdir -p $RPM_BUILD_ROOT/var/lib/dracut/overlay
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log
touch $RPM_BUILD_ROOT%{_localstatedir}/log/dracut.log
mkdir -p $RPM_BUILD_ROOT%{_sharedstatedir}/initramfs

%if 0%{?fedora} || 0%{?rhel} || 0%{?suse_version}
install -m 0644 dracut.conf.d/fedora.conf.example $RPM_BUILD_ROOT%{dracutlibdir}/dracut.conf.d/01-dist.conf
install -m 0644 dracut.conf.d/fips.conf.example $RPM_BUILD_ROOT%{dracutlibdir}/dracut.conf.d/40-fips.conf
%endif

%if 0%{?suse_version}
install -m 0644 dracut.conf.d/suse.conf.example   $RPM_BUILD_ROOT%{dracutlibdir}/dracut.conf.d/01-dist.conf
%endif

%if 0%{?fedora} <= 12 && 0%{?rhel} < 6 && 0%{?suse_version} <= 9999
rm -f -- $RPM_BUILD_ROOT%{_bindir}/mkinitrd
rm -f -- $RPM_BUILD_ROOT%{_bindir}/lsinitrd
%endif

%if 0%{?fedora} || 0%{?rhel} > 6
# FIXME: remove after F19
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/kernel/postinst.d
install -m 0755 51-dracut-rescue-postinst.sh $RPM_BUILD_ROOT%{_sysconfdir}/kernel/postinst.d/51-dracut-rescue-postinst.sh

echo 'hostonly="no"' > $RPM_BUILD_ROOT%{dracutlibdir}/dracut.conf.d/02-generic-image.conf
echo 'dracut_rescue_image="yes"' > $RPM_BUILD_ROOT%{dracutlibdir}/dracut.conf.d/02-rescue.conf
%endif

%if 0%{?fedora} || 0%{?rhel} || 0%{?suse_version}
> $RPM_BUILD_ROOT/etc/system-fips
%endif

# create compat symlink
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
ln -sr $RPM_BUILD_ROOT%{_bindir}/dracut $RPM_BUILD_ROOT%{_sbindir}/dracut

%clean
rm -rf -- $RPM_BUILD_ROOT

%files
%defattr(-,root,root,0755)
%doc README HACKING TODO COPYING AUTHORS NEWS dracut.html dracut.png dracut.svg
%{_bindir}/dracut
# compat symlink
%{_sbindir}/dracut
%{_datadir}/bash-completion/completions/dracut
%{_datadir}/bash-completion/completions/lsinitrd
%if 0%{?fedora} > 12 || 0%{?rhel} >= 6 || 0%{?suse_version} > 9999
%{_bindir}/mkinitrd
%{_bindir}/lsinitrd
%endif
%dir %{dracutlibdir}
%dir %{dracutlibdir}/modules.d
%{dracutlibdir}/dracut-init.sh
%{dracutlibdir}/dracut-functions.sh
%{dracutlibdir}/dracut-functions
%{dracutlibdir}/dracut-version.sh
%{dracutlibdir}/dracut-logger.sh
%{dracutlibdir}/dracut-initramfs-restore
%{dracutlibdir}/dracut-install
%{dracutlibdir}/skipcpio
%config(noreplace) %{_sysconfdir}/dracut.conf
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel}
%{dracutlibdir}/dracut.conf.d/01-dist.conf
%endif
%dir %{_sysconfdir}/dracut.conf.d
%dir %{dracutlibdir}/dracut.conf.d
%{_datadir}/pkgconfig/dracut.pc
%{_mandir}/man8/dracut.8*
%{_mandir}/man8/*service.8*
%if 0%{?fedora} > 12 || 0%{?rhel} >= 6 || 0%{?suse_version} > 9999
%{_mandir}/man8/mkinitrd.8*
%{_mandir}/man1/lsinitrd.1*
%endif
%{_mandir}/man7/dracut.kernel.7*
%{_mandir}/man7/dracut.cmdline.7*
%{_mandir}/man7/dracut.modules.7*
%{_mandir}/man7/dracut.bootup.7*
%{_mandir}/man5/dracut.conf.5*
%if %{defined _unitdir}
%{dracutlibdir}/modules.d/00systemd-bootchart
%else
%{dracutlibdir}/modules.d/00bootchart
%endif
%{dracutlibdir}/modules.d/00bash
%{dracutlibdir}/modules.d/03modsign
%{dracutlibdir}/modules.d/03rescue
%{dracutlibdir}/modules.d/04watchdog
%{dracutlibdir}/modules.d/05busybox
%{dracutlibdir}/modules.d/10i18n
%{dracutlibdir}/modules.d/30convertfs
%{dracutlibdir}/modules.d/45url-lib
%{dracutlibdir}/modules.d/50drm
%{dracutlibdir}/modules.d/50plymouth
%{dracutlibdir}/modules.d/80cms
%{dracutlibdir}/modules.d/90bcache
%{dracutlibdir}/modules.d/90btrfs
%{dracutlibdir}/modules.d/90crypt
%{dracutlibdir}/modules.d/90dm
%{dracutlibdir}/modules.d/90dmraid
%{dracutlibdir}/modules.d/90dmsquash-live
%{dracutlibdir}/modules.d/90dmsquash-live-ntfs
%{dracutlibdir}/modules.d/90kernel-modules
%{dracutlibdir}/modules.d/90lvm
%{dracutlibdir}/modules.d/90mdraid
%{dracutlibdir}/modules.d/90multipath
%{dracutlibdir}/modules.d/90multipath-hostonly
%{dracutlibdir}/modules.d/90qemu
%{dracutlibdir}/modules.d/91crypt-gpg
%{dracutlibdir}/modules.d/91crypt-loop
%{dracutlibdir}/modules.d/95debug
%{dracutlibdir}/modules.d/95resume
%{dracutlibdir}/modules.d/95rootfs-block
%{dracutlibdir}/modules.d/95dasd
%{dracutlibdir}/modules.d/95dasd_mod
%{dracutlibdir}/modules.d/95fstab-sys
%{dracutlibdir}/modules.d/95zfcp
%{dracutlibdir}/modules.d/95terminfo
%{dracutlibdir}/modules.d/95udev-rules
%{dracutlibdir}/modules.d/95virtfs
%if %{undefined _unitdir}
%{dracutlibdir}/modules.d/96securityfs
%{dracutlibdir}/modules.d/97masterkey
%{dracutlibdir}/modules.d/98integrity
%endif
%{dracutlibdir}/modules.d/97biosdevname
%{dracutlibdir}/modules.d/98ecryptfs
%{dracutlibdir}/modules.d/98pollcdrom
%{dracutlibdir}/modules.d/98selinux
%{dracutlibdir}/modules.d/98syslog
%{dracutlibdir}/modules.d/98systemd
%{dracutlibdir}/modules.d/98usrmount
%{dracutlibdir}/modules.d/99base
%{dracutlibdir}/modules.d/99fs-lib
%{dracutlibdir}/modules.d/99img-lib
%{dracutlibdir}/modules.d/99shutdown
%attr(0644,root,root) %ghost %config(missingok,noreplace) %{_localstatedir}/log/dracut.log
%dir %{_sharedstatedir}/initramfs
%if %{defined _unitdir}
%{_unitdir}/dracut-shutdown.service
%{_unitdir}/shutdown.target.wants/dracut-shutdown.service
%{_unitdir}/dracut-cmdline.service
%{_unitdir}/dracut-initqueue.service
%{_unitdir}/dracut-mount.service
%{_unitdir}/dracut-pre-mount.service
%{_unitdir}/dracut-pre-pivot.service
%{_unitdir}/dracut-pre-trigger.service
%{_unitdir}/dracut-pre-udev.service
%{_unitdir}/initrd.target.wants/dracut-cmdline.service
%{_unitdir}/initrd.target.wants/dracut-initqueue.service
%{_unitdir}/initrd.target.wants/dracut-mount.service
%{_unitdir}/initrd.target.wants/dracut-pre-mount.service
%{_unitdir}/initrd.target.wants/dracut-pre-pivot.service
%{_unitdir}/initrd.target.wants/dracut-pre-trigger.service
%{_unitdir}/initrd.target.wants/dracut-pre-udev.service

%endif
%if 0%{?fedora} || 0%{?rhel} > 6
%{_prefix}/lib/kernel/install.d/50-dracut.install
%endif

%files network
%defattr(-,root,root,0755)
%{dracutlibdir}/modules.d/40network
%{dracutlibdir}/modules.d/95fcoe
%{dracutlibdir}/modules.d/95iscsi
%{dracutlibdir}/modules.d/90livenet
%{dracutlibdir}/modules.d/90qemu-net
%{dracutlibdir}/modules.d/95cifs
%{dracutlibdir}/modules.d/95nbd
%{dracutlibdir}/modules.d/95nfs
%{dracutlibdir}/modules.d/95ssh-client
%{dracutlibdir}/modules.d/45ifcfg
%{dracutlibdir}/modules.d/95znet
%{dracutlibdir}/modules.d/95fcoe-uefi
%{dracutlibdir}/modules.d/99uefi-lib

%if 0%{?fedora} || 0%{?rhel} || 0%{?suse_version}
%files fips
%defattr(-,root,root,0755)
%{dracutlibdir}/modules.d/01fips
%{dracutlibdir}/dracut.conf.d/40-fips.conf
%config(missingok) /etc/system-fips
%endif

%files fips-aesni
%defattr(-,root,root,0755)
%doc COPYING
%{dracutlibdir}/modules.d/02fips-aesni

%files caps
%defattr(-,root,root,0755)
%{dracutlibdir}/modules.d/02caps

%files tools
%defattr(-,root,root,0755)
%{_mandir}/man8/dracut-catimages.8*
%{_bindir}/dracut-catimages
%dir /boot/dracut
%dir /var/lib/dracut
%dir /var/lib/dracut/overlay

%files config-generic
%defattr(-,root,root,0755)
%{dracutlibdir}/dracut.conf.d/02-generic-image.conf

%files config-rescue
%defattr(-,root,root,0755)
%{dracutlibdir}/dracut.conf.d/02-rescue.conf
%if 0%{?fedora} || 0%{?rhel} > 6
%{_prefix}/lib/kernel/install.d/51-dracut-rescue.install
%{_sysconfdir}/kernel/postinst.d/51-dracut-rescue-postinst.sh
%endif

%changelog
