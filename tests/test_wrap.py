# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import datetime

from fs import errors
from fs.test import FSTestCases
from fs.wrap import WrapReadOnly
from fs.memoryfs import MemoryFS

from fs.archive.wrap import WrapWritable



class TestWrapWritable(FSTestCases, unittest.TestCase):


    def assertDatetimeEqual(self, d1, d2):
        self.assertEqual(
            d1.timestamp(),
            d2.timestamp()
        )


    def make_fs(self):
        src_fs = MemoryFS()
        src_fs.makedirs('foo/bar')
        src_fs.settext('root.txt', 'root file')
        src_fs.setbytes('foo/nested.bin', b'nested file')
        wrapped_fs = WrapWritable(WrapReadOnly(src_fs))
        wrapped_fs.remove('root.txt')
        wrapped_fs.remove('foo/nested.bin')
        wrapped_fs.removedir('foo/bar')
        wrapped_fs.removedir('foo')
        return wrapped_fs


    def test_makedir(self):
        super(TestWrapWritable, self).test_makedir()
        self.assertRaises(errors.ResourceNotFound, self.fs.makedir, 'abc/def')
        self.fs.touch('abc')
        self.assertRaises(errors.DirectoryExpected, self.fs.makedir, 'abc/def')



    def test_setinfo_wrapped(self):

        now = datetime.datetime.now()
        src_fs = MemoryFS()
        src_fs.settext('test.txt', 'test file')
        src_fs.setinfo('test.txt', {'details':
            {'modified': now.timestamp(), 'accessed': now.timestamp()}
        })
        self.assertDatetimeEqual(src_fs.getdetails('test.txt').modified, now)

        wrapped_fs = WrapWritable(WrapReadOnly(src_fs))
        self.assertDatetimeEqual(
            wrapped_fs.getdetails('test.txt').modified,
            now
        )
        self.assertDatetimeEqual(
            wrapped_fs.getdetails('test.txt').accessed,
            now
        )

        now2 = datetime.datetime.now()
        wrapped_fs.setinfo('test.txt', {'details':
            {'modified': now2.timestamp()}
        })

        print(src_fs.getdetails('test.txt').raw)
        print(wrapped_fs.getdetails('test.txt').raw)

        self.assertDatetimeEqual(
            wrapped_fs.getdetails('test.txt').accessed,
            src_fs.getdetails('test.txt').accessed
        )
        self.assertDatetimeEqual(
            wrapped_fs.getdetails('test.txt').modified,
            now2
        )



    def test_openbin_wrapped(self):
        src_fs = MemoryFS()
        src_fs.settext('test.txt', 'this is a test')
        wrapped_fs = WrapWritable(WrapReadOnly(src_fs))

        with wrapped_fs.openbin('test.txt', 'r+') as f:
            self.assertEqual(f.read(), b'this is a test')
            f.seek(0)
            f.write(b'test should work')
            f.seek(0)
        self.assertEqual(wrapped_fs.gettext('test.txt'), 'test should work')