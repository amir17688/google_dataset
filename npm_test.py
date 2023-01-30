# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Jayesh Kariya <jayeshk@saltstack.com>`
'''

# Import Python Libs
from __future__ import absolute_import

# Import Salt Testing Libs
from salttesting import TestCase, skipIf
from salttesting.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

from salttesting.helpers import ensure_in_syspath

ensure_in_syspath('../../')

# Import Salt Libs
from salt.modules import npm
from salt.exceptions import CommandExecutionError
import json

# Globals
npm.__salt__ = {}


@skipIf(NO_MOCK, NO_MOCK_REASON)
class NpmTestCase(TestCase):
    '''
    Test cases for salt.modules.npm
    '''
    # 'install' function tests: 1

    @patch('salt.modules.npm._check_valid_version',
           MagicMock(return_value=True))
    def test_install(self):
        '''
        Test if it install an NPM package.
        '''
        mock = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertRaises(CommandExecutionError, npm.install,
                              'coffee-script')

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error',
                                       'stdout': '{"salt": ["SALT"]}'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            mock_err = MagicMock(return_value='SALT')
            with patch.object(json, 'loads', mock_err):
                self.assertEqual(npm.install('coffee-script'), 'SALT')

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error',
                                       'stdout': '{"salt": ["SALT"]}'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            mock_err = MagicMock(side_effect=ValueError())
            with patch.object(json, 'loads', mock_err):
                self.assertEqual(npm.install('coffee-script'),
                                 '{"salt": ["SALT"]}')

    # 'uninstall' function tests: 1

    @patch('salt.modules.npm._check_valid_version',
           MagicMock(return_value=True))
    def test_uninstall(self):
        '''
        Test if it uninstall an NPM package.
        '''
        mock = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertFalse(npm.uninstall('coffee-script'))

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertTrue(npm.uninstall('coffee-script'))

    # 'list_' function tests: 1

    @patch('salt.modules.npm._check_valid_version',
           MagicMock(return_value=True))
    def test_list(self):
        '''
        Test if it list installed NPM packages.
        '''
        mock = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertRaises(CommandExecutionError, npm.list_, 'coffee-script')

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error',
                                       'stdout': '{"salt": ["SALT"]}'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            mock_err = MagicMock(return_value={'dependencies': 'SALT'})
            with patch.object(json, 'loads', mock_err):
                self.assertEqual(npm.list_('coffee-script'), 'SALT')

    # 'cache_clean' function tests: 1

    @patch('salt.modules.npm._check_valid_version',
           MagicMock(return_value=True))
    def test_cache_clean(self):
        '''
        Test if it cleans the cached NPM packages.
        '''
        mock = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertFalse(npm.cache_clean())

        mock = MagicMock(return_value={'retcode': 0})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertTrue(npm.cache_clean())

        mock = MagicMock(return_value={'retcode': 0})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertTrue(npm.cache_clean('coffee-script'))

    # 'cache_list' function tests: 1

    @patch('salt.modules.npm._check_valid_version',
           MagicMock(return_value=True))
    def test_cache_list(self):
        '''
        Test if it lists the NPM cache.
        '''
        mock = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertRaises(CommandExecutionError, npm.cache_list)

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error',
                                       'stdout': ['~/.npm']})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(npm.cache_list(), ['~/.npm'])

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error',
                                       'stdout': ''})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(npm.cache_list('coffee-script'), '')

    # 'cache_path' function tests: 1

    @patch('salt.modules.npm._check_valid_version',
           MagicMock(return_value=True))
    def test_cache_path(self):
        '''
        Test if it prints the NPM cache path.
        '''
        mock = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(npm.cache_path(), 'error')

        mock = MagicMock(return_value={'retcode': 0, 'stderr': 'error',
                                       'stdout': '/User/salt/.npm'})
        with patch.dict(npm.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(npm.cache_path(), '/User/salt/.npm')


if __name__ == '__main__':
    from integration import run_tests
    run_tests(NpmTestCase, needs_daemon=False)
atch.dict(npm.__salt__, {'npm.cache_list': mock_err}):
            comt = ('Error looking up cached packages: ')
            ret.update({'comment': comt})
            self.assertDictEqual(npm.cache_cleaned(), ret)

        with patch.dict(npm.__salt__, {'npm.cache_list': mock_err}):
            comt = ("Error looking up cached {0}: ".format(name))
            pkg_ret.update({'comment': comt})
            self.assertDictEqual(npm.cache_cleaned(name), pkg_ret)

        mock_data = {'npm.cache_list': mock_list, 'npm.cache_clean': MagicMock()}
        with patch.dict(npm.__salt__, mock_data):
            non_cached_pkg = 'salt'
            comt = ('Package {0} is not in the cache'.format(non_cached_pkg))
            pkg_ret.update({'name': non_cached_pkg, 'result': True, 'comment': comt})
            self.assertDictEqual(npm.cache_cleaned(non_cached_pkg), pkg_ret)
            pkg_ret.update({'name': name})

            with patch.dict(npm.__opts__, {'test': True}):
                comt = ('Cached packages set to be removed')
                ret.update({'result': None, 'comment': comt})
                self.assertDictEqual(npm.cache_cleaned(), ret)

            with patch.dict(npm.__opts__, {'test': True}):
                comt = ('Cached {0} set to be removed'.format(name))
                pkg_ret.update({'result': None, 'comment': comt})
                self.assertDictEqual(npm.cache_cleaned(name), pkg_ret)

            with patch.dict(npm.__opts__, {'test': False}):
                comt = ('Cached packages successfully removed')
                ret.update({'result': True, 'comment': comt,
                            'changes': {'cache': 'Removed'}})
                self.assertDictEqual(npm.cache_cleaned(), ret)

            with patch.dict(npm.__opts__, {'test': False}):
                comt = ('Cached {0} successfully removed'.format(name))
                pkg_ret.update({'result': True, 'comment': comt,
                            'changes': {name: 'Removed'}})
                self.assertDictEqual(npm.cache_cleaned(name), pkg_ret)

        mock_data = {'npm.cache_list': mock_list, 'npm.cache_clean': MagicMock(return_value=False)}
        with patch.dict(npm.__salt__, mock_data):
            with patch.dict(npm.__opts__, {'test': False}):
                comt = ('Error cleaning cached packages')
                ret.update({'result': False, 'comment': comt})
                ret['changes'] = {}
                self.assertDictEqual(npm.cache_cleaned(), ret)

            with patch.dict(npm.__opts__, {'test': False}):
                comt = ('Error cleaning cached {0}'.format(name))
                pkg_ret.update({'result': False, 'comment': comt})
                pkg_ret['changes'] = {}
                self.assertDictEqual(npm.cache_cleaned(name), pkg_ret)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(NpmTestCase, needs_daemon=False)
