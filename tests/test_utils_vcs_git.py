# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for Git interactions"""

__revision__ = "$Id$"

import tarfile
from os import chdir, path
from shutil import rmtree
from subprocess import call
from tempfile import mkdtemp

from invenio_base.globals import cfg
from invenio_testing import InvenioTestCase
from invenio_utils.vcs.git import harvest_repo


class GitHarvestTest(InvenioTestCase):
    """Test harvesting of Git respo"""

    def setUp(self):

        from invenio_utils.vcs.git import git_exists, get_which_git
        if not git_exists():
            from unittest import SkipTest
            raise SkipTest("Git not found. It probably needs installing.")

        self.which_git = get_which_git()

        self.path = path.join(mkdtemp(dir=cfg['CFG_TMPDIR']), '')
        self.archive_dir = path.join(mkdtemp(dir=cfg['CFG_TMPDIR']), '')
        self.archive_path = path.join(self.archive_dir, 'test.tar.gz')

        call([self.which_git, 'init', self.path])
        chdir(self.path)

        # Setup git user config.
        call([self.which_git, 'config', 'user.name', 'Invenio Software'])
        call([self.which_git, 'config', 'user.email',
              'info@inveniosoftware.org'])

        call(['touch', self.path + 'test.txt'])
        call([self.which_git, 'add', self.path + 'test.txt'])
        call([self.which_git, 'commit', '-m', 'Initial Commit'])
        call([self.which_git, 'tag', 'v0.1'])

        call(['touch', self.path + 'test2.txt'])
        call([self.which_git, 'add', self.path + 'test2.txt'])
        call([self.which_git, 'commit', '-m', 'second Commit'])
        call([self.which_git, 'tag', 'v0.2'])

        call(['touch', self.path + 'test3.txt'])
        call([self.which_git, 'add', self.path + 'test3.txt'])
        call([self.which_git, 'commit', '-m', 'third Commit'])
        call([self.which_git, 'tag', 'v0.3'])

    def tearDown(self):
        rmtree(self.path)

    def test_harvest_with_tag_v0_1(self):
        """Test harvesting of tag v0.1"""
        harvest_repo(self.path, self.archive_path, tag='v0.1')
        fs_list = tarfile.open(self.archive_path).getnames()
        self.assertTrue('test.txt' in fs_list)
        self.assertFalse('test2.txt' in fs_list)
        self.assertFalse('test3.txt' in fs_list)

    def test_harvest_with_tag_v0_2(self):
        """Test harvesting of tag v0.2"""
        harvest_repo(self.path, self.archive_path, tag='v0.2')
        fs_list = tarfile.open(self.archive_path).getnames()
        self.assertTrue('test.txt' in fs_list)
        self.assertTrue('test2.txt' in fs_list)
        self.assertFalse('test3.txt' in fs_list)

    def test_harvest_with_tag_v0_3(self):
        """Test harvesting of tag v0.3"""
        harvest_repo(self.path, self.archive_path, tag='v0.3')
        fs_list = tarfile.open(self.archive_path).getnames()
        self.assertTrue('test.txt' in fs_list)
        self.assertTrue('test2.txt' in fs_list)
        self.assertTrue('test3.txt' in fs_list)

    def test_harvest_without_tag(self):
        """Test harvesting of HEAD"""
        harvest_repo(self.path, self.archive_path)
        fs_list = tarfile.open(self.archive_path).getnames()
        self.assertTrue('test.txt' in fs_list)
        self.assertTrue('test2.txt' in fs_list)
        self.assertTrue('test3.txt' in fs_list)
