# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import tarfile

from .._utils import import_from_names

lzma = import_from_names('lzma', 'backports.lzma')


class TarFile(tarfile.TarFile):

    OPEN_METH = {
        "tar": "taropen",
        "gz": "gzopen",
        "bz2": "bz2open",
    }

    if six.PY3:
        OPEN_METH["xz"] = "xzopen"

    if lzma is not None:
        OPEN_METH["xzopen"] = "xzopen"

        @classmethod
        def xzopen(cls, name, mode="r", fileobj=None, preset=None, **kwargs):
            """Open lzma compressed tar archive name for reading or writing.
               Appending is not allowed.

               Backported from `Python 3.6
               <https://github.com/python/cpython/blob/3.6/Lib/tarfile.py>`_
            """
            if mode not in ("r", "w", "x"):
                raise ValueError("mode must be 'r', 'w' or 'x'")

            fileobj = lzma.LZMAFile(fileobj or name, mode, preset=preset)

            try:
                t = cls.taropen(name, mode, fileobj, **kwargs)
            except (lzma.LZMAError, EOFError):
                fileobj.close()
                if mode == 'r':
                    raise tarfile.ReadError("not an lzma file")
                raise
            except:
                fileobj.close()
                raise
            t._extfileobj = False
            return t
