#
# This file is part of Gruvi. Gruvi is free software available under the
# terms of the MIT license. See the file "LICENSE" that was provided
# together with this source file for the licensing terms.
#
# Copyright (c) 2012-2014 the Gruvi authors. See the file "AUTHORS" for a
# complete list.

from __future__ import absolute_import, print_function

import os
import sys
import sphinx
import unittest

from support import TestCase


class TestDocumentation(TestCase):

    def test_build_docs(self):
        docdir = os.path.join(self.topdir, 'docs')
        os.chdir(docdir)
        htmldir = self.tempdir
        # Add a fix for https://bitbucket.org/birkenfeld/sphinx/issue/1611
        # where sphinx.main() ignores arguments passed to it and instead uses
        # sys.argv.
        args = ['sphinx', '-b', 'html', '-nW', '.', htmldir]
        saved_argv, sys.argv = sys.argv, args
        # sphinx.main() changed behavior in version 1.2.3 and it now calls
        # exit() with the return code rather than returning it.
        try:
            ret = sphinx.main(['sphinx', '-b', 'html', '-nW', '.', htmldir])
        except SystemExit as e:
            ret = e.code
        sys.argv = saved_argv
        self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()
