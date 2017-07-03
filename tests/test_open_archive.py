# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import gzip
import zipfile
import tarfile
import unittest

import fs.archive
from fs.archive.zipfs import ZipFS
from fs.archive.tarfs import TarFS
from fs.opener import _errors as errors


class TestOpenArchive(unittest.TestCase):

    def test_open_unknown_archive(self):
        with self.assertRaises(errors.Unsupported):
            with fs.archive.open_archive('mem://', 'not-an-archive.txt'):
                pass

    def test_zip(self):
        mem = fs.open_fs('mem://')
        with fs.archive.open_archive(mem, 'myzip.zip') as archive:
            self.assertIsInstance(archive, fs.archive.zipfs.ZipFS)
            archive.settext('abc.txt', 'abc')
            archive.makedir('dir')

        with fs.archive.open_archive(mem, 'myzip.zip') as archive:
            self.assertEqual(sorted(archive.listdir('/')), ['abc.txt', 'dir'])
            self.assertEqual(archive.gettext('abc.txt'), 'abc')

        with mem.openbin('myzip.zip') as myzip:
            self.assertTrue(zipfile.is_zipfile(myzip))

    def _test_tar(self, filename, arcfile, opener):

        mem = fs.open_fs('mem://')

        # Check we can write
        with fs.archive.open_archive(mem, filename) as archive:
            print(archive._saver.compression)
            self.assertIsInstance(archive, fs.archive.tarfs.TarFS)
            archive.settext('abc.txt', 'abc')
            archive.makedir('dir')

        # Check the dumped archive is a gzipped file
        with mem.openbin(filename) as mytar:
            arc = arcfile(mytar)
            arc.read()

        # Check we can open it normally
        with mem.openbin(filename) as mytar:
            tar = getattr(tarfile.TarFile, opener)(filename, fileobj=mytar)
        with mem.openbin(filename) as mytar:
            tar = tarfile.TarFile.open(filename, fileobj=mytar)

        # Check we can read it with the TarFS
        with fs.archive.open_archive(mem, filename) as archive:
            self.assertEqual(sorted(archive.listdir('/')), ['abc.txt', 'dir'])
            self.assertEqual(archive.gettext('abc.txt'), 'abc')

    def test_tar_gz(self):
        arc_gz = lambda fileobj: gzip.GzipFile(fileobj=fileobj)
        self._test_tar('mytar.tar.gz', arc_gz, 'gzopen')
        self._test_tar('mytar.tgz', arc_gz, 'gzopen')

    @unittest.skipIf(six.PY2, 'lzma not supported in Python 2')
    def test_tar_xz(self):
        import lzma
        arc_lz = lambda fileobj: lzma.LZMAFile(fileobj)
        self._test_tar('mytar.tar.xz', arc_lz, 'xzopen')
        self._test_tar('mytar.txz', arc_lz, 'xzopen')

    @unittest.skipIf(six.PY3, 'lzma not supported in Python 2 only')
    def test_tar_xz_missing(self):
        with self.assertRaises(errors.Unsupported):
            with fs.archive.open_archive('mem://', 'archive.tar.xz'):
                pass
        with self.assertRaises(errors.Unsupported):
            with fs.archive.open_archive('mem://', 'archive.txz'):
                pass
