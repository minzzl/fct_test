user@user-VirtualBox:~/work/e2fsprogs-1.42.11$ sudo make install
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: 'util/subst.conf' is up to date.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: 'lib/config.h' is up to date.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11'
	SUBST lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: 'lib/ext2fs/ext2_types.h' is up to date.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: 'lib/blkid/blkid_types.h' is up to date.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: 'lib/uuid/uuid_types.h' is up to date.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/et'
	SUBST compile_et
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/et'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/ext2fs'
	SUBST ext2_err.et
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/ext2fs'
making all in lib/et
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/et'
	SUBST compile_et
	SUBST ../../lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/et'
making all in lib/ss
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/ss'
	SUBST mk_cmds
	SUBST ../../lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/ss'
making all in lib/e2p
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/e2p'
	SUBST ../../lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/e2p'
making all in lib/uuid
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/uuid'
	SUBST ../../lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/uuid'
making all in lib/blkid
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/blkid'
	SUBST ../../lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/blkid'
making all in lib/quota
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/quota'
	SUBST ../../lib/dirpaths.h
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/quota'
making all in lib/ext2fs
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/ext2fs'
	SUBST ../../lib/dirpaths.h
	SUBST ext2_err.et
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/ext2fs'
making all in intl
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/intl'
make[1]: Nothing to be done for 'all'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/intl'
making install in e2fsck
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/e2fsck'
	SUBST ../lib/dirpaths.h
	MKINSTALLDIRS /home/user/work/newrootfs/rootfs/sbin /home/user/work/newrootfs/rootfs/share/man/man8
	INSTALL /home/user/work/newrootfs/rootfs/sbin/e2fsck
	LINK /home/user/work/newrootfs/rootfs/sbin/fsck.ext2
	LINK /home/user/work/newrootfs/rootfs/sbin/fsck.ext3
	LINK /home/user/work/newrootfs/rootfs/sbin/fsck.ext4
	LINK /home/user/work/newrootfs/rootfs/sbin/fsck.ext4dev
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/e2fsck.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man5/e2fsck.conf.5
	LINK /home/user/work/newrootfs/rootfs/share/man/man8/fsck.ext2.8
	LINK /home/user/work/newrootfs/rootfs/share/man/man8/fsck.ext3.8
	LINK /home/user/work/newrootfs/rootfs/share/man/man8/fsck.ext4.8
	LINK /home/user/work/newrootfs/rootfs/share/man/man8/fsck.ext4dev.8
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/e2fsck'
making install in debugfs
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/debugfs'
	SUBST ../lib/dirpaths.h
	MKINSTALLDIRS /home/user/work/newrootfs/rootfs/sbin /home/user/work/newrootfs/rootfs/share/man/man8
	INSTALL /home/user/work/newrootfs/rootfs/sbin/debugfs
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/debugfs.8
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/debugfs'
making install in misc
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/misc'
	SUBST ../lib/dirpaths.h
	MKINSTALLDIRS /home/user/work/newrootfs/rootfs/sbin /home/user/work/newrootfs/rootfs/sbin /home/user/work/newrootfs/rootfs/bin /home/user/work/newrootfs/rootfs/share/man/man1 /home/user/work/newrootfs/rootfs/share/man/man8 /home/user/work/newrootfs/rootfs/lib /home/user/work/newrootfs/rootfs/etc
	INSTALL /home/user/work/newrootfs/rootfs/sbin/mke2fs
	INSTALL /home/user/work/newrootfs/rootfs/sbin/badblocks
	INSTALL /home/user/work/newrootfs/rootfs/sbin/tune2fs
	INSTALL /home/user/work/newrootfs/rootfs/sbin/dumpe2fs
	INSTALL /home/user/work/newrootfs/rootfs/sbin/blkid
	INSTALL /home/user/work/newrootfs/rootfs/sbin/logsave
	INSTALL /home/user/work/newrootfs/rootfs/sbin/e2image
	INSTALL /home/user/work/newrootfs/rootfs/sbin/fsck
	INSTALL /home/user/work/newrootfs/rootfs/sbin/e2undo
	INSTALL /home/user/work/newrootfs/rootfs/sbin/mklost+found
	INSTALL /home/user/work/newrootfs/rootfs/sbin/filefrag
	INSTALL /home/user/work/newrootfs/rootfs/sbin/e2freefrag
	INSTALL /home/user/work/newrootfs/rootfs/sbin/uuidd
	INSTALL /home/user/work/newrootfs/rootfs/sbin/e4defrag
	LINK /home/user/work/newrootfs/rootfs/sbin/mkfs.ext2
	LINK /home/user/work/newrootfs/rootfs/sbin/mkfs.ext3
	LINK /home/user/work/newrootfs/rootfs/sbin/mkfs.ext4
	LINK /home/user/work/newrootfs/rootfs/sbin/mkfs.ext4dev
	LINK /home/user/work/newrootfs/rootfs/sbin/findfs
	INSTALL /home/user/work/newrootfs/rootfs/bin/chattr
	INSTALL /home/user/work/newrootfs/rootfs/bin/lsattr
	INSTALL /home/user/work/newrootfs/rootfs/bin/uuidgen
	INSTALL /home/user/work/newrootfs/rootfs/lib/e2initrd_helper
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/tune2fs.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/mklost+found.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/mke2fs.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/dumpe2fs.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/badblocks.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/e2label.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/findfs.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/blkid.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/e2image.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/logsave.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/filefrag.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/e2freefrag.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/e2undo.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/uuidd.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/e4defrag.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/fsck.8
	LINK mkfs.ext2.8
	LINK mkfs.ext3.8
	LINK mkfs.ext4.8
	LINK mkfs.ext4dev.8
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man1/chattr.1
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man1/lsattr.1
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man1/uuidgen.1
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man5/mke2fs.conf.5
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man5/ext4.5
	LINK ext2.5
	LINK ext3.5
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/misc'
making install in resize
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/resize'
	SUBST ../lib/dirpaths.h
	MKINSTALLDIRS /home/user/work/newrootfs/rootfs/sbin /home/user/work/newrootfs/rootfs/share/man/man8
	INSTALL /home/user/work/newrootfs/rootfs/sbin/resize2fs
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/man/man8/resize2fs.8
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/resize'
making install in tests/progs
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/tests/progs'
make[1]: Nothing to be done for 'install'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/tests/progs'
making install in po
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/po'
/bin/sh ../config/mkinstalldirs /home/user/work/newrootfs/rootfs/share
installing ca.gmo as /home/user/work/newrootfs/rootfs/share/locale/ca/LC_MESSAGES/e2fsprogs.mo
installing cs.gmo as /home/user/work/newrootfs/rootfs/share/locale/cs/LC_MESSAGES/e2fsprogs.mo
installing de.gmo as /home/user/work/newrootfs/rootfs/share/locale/de/LC_MESSAGES/e2fsprogs.mo
installing eo.gmo as /home/user/work/newrootfs/rootfs/share/locale/eo/LC_MESSAGES/e2fsprogs.mo
installing es.gmo as /home/user/work/newrootfs/rootfs/share/locale/es/LC_MESSAGES/e2fsprogs.mo
installing fr.gmo as /home/user/work/newrootfs/rootfs/share/locale/fr/LC_MESSAGES/e2fsprogs.mo
installing id.gmo as /home/user/work/newrootfs/rootfs/share/locale/id/LC_MESSAGES/e2fsprogs.mo
installing it.gmo as /home/user/work/newrootfs/rootfs/share/locale/it/LC_MESSAGES/e2fsprogs.mo
installing nl.gmo as /home/user/work/newrootfs/rootfs/share/locale/nl/LC_MESSAGES/e2fsprogs.mo
installing pl.gmo as /home/user/work/newrootfs/rootfs/share/locale/pl/LC_MESSAGES/e2fsprogs.mo
installing sv.gmo as /home/user/work/newrootfs/rootfs/share/locale/sv/LC_MESSAGES/e2fsprogs.mo
installing tr.gmo as /home/user/work/newrootfs/rootfs/share/locale/tr/LC_MESSAGES/e2fsprogs.mo
installing uk.gmo as /home/user/work/newrootfs/rootfs/share/locale/uk/LC_MESSAGES/e2fsprogs.mo
installing vi.gmo as /home/user/work/newrootfs/rootfs/share/locale/vi/LC_MESSAGES/e2fsprogs.mo
installing zh_CN.gmo as /home/user/work/newrootfs/rootfs/share/locale/zh_CN/LC_MESSAGES/e2fsprogs.mo
if test "e2fsprogs" = "gettext-tools"; then \
  /bin/sh ../config/mkinstalldirs /home/user/work/newrootfs/rootfs/share/gettext/po; \
  for file in Makefile.in.in remove-potcdate.sin quot.sed boldquot.sed en@quot.header en@boldquot.header insert-header.sin Rules-quot   Makevars.template; do \
    /usr/bin/install -c -m 644 ./$file \
		    /home/user/work/newrootfs/rootfs/share/gettext/po/$file; \
  done; \
  for file in Makevars; do \
    rm -f /home/user/work/newrootfs/rootfs/share/gettext/po/$file; \
  done; \
else \
  : ; \
fi
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/po'
making install-shlibs in lib/et
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/et'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/et'
making install-shlibs in lib/ss
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/ss'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/ss'
making install-shlibs in lib/e2p
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/e2p'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/e2p'
making install-shlibs in lib/uuid
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/uuid'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/uuid'
making install-shlibs in lib/blkid
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/blkid'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/blkid'
making install-shlibs in lib/quota
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/quota'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/quota'
making install-shlibs in lib/ext2fs
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/lib/ext2fs'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/lib/ext2fs'
making install-shlibs in intl
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/intl'
make[1]: Nothing to be done for 'install-shlibs'.
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/intl'
make[1]: Entering directory '/home/user/work/e2fsprogs-1.42.11/doc'
	TEXI2DVI libext2fs.dvi
You don't have a working TeX binary (tex) installed anywhere in
your PATH, and texi2dvi cannot proceed without one.  If you want to use
this script, you'll need to install TeX (if you don't have it) or change
your PATH or TEX environment variable (if you do).  See the --help
output for more details.

For information about obtaining TeX, please see http://tug.org/texlive,
or do a web search for TeX and your operating system or distro.

On Debian you can install a working TeX system with
  apt-get install texlive
Makefile:331: recipe for target 'libext2fs.dvi' failed
make[1]: [libext2fs.dvi] Error 1 (ignored)
	MKINSTALLDIRS /home/user/work/newrootfs/rootfs/share/info
	INSTALL_DATA /home/user/work/newrootfs/rootfs/share/info/libext2fs.info
	GZIP /home/user/work/newrootfs/rootfs/share/info/libext2fs.info*
make[1]: Leaving directory '/home/user/work/e2fsprogs-1.42.11/doc'
