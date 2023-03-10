# Copyright 2014 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import io
import mock
import six
from six import StringIO
import unittest2

from bareon import errors
from bareon.utils import grub as gu

if six.PY2:
    OPEN_FUNCTION_NAME = '__builtin__.open'
else:
    OPEN_FUNCTION_NAME = 'builtins.open'


class TestGrubUtils(unittest2.TestCase):

    @mock.patch('bareon.utils.grub.os.path.isdir')
    def test_guess_grub2_conf(self, mock_isdir):
        side_effect_values = {
            '/target/boot/grub': True,
            '/target/boot/grub2': False
        }

        def side_effect(key):
            return side_effect_values[key]

        mock_isdir.side_effect = side_effect
        self.assertEqual(gu.guess_grub2_conf('/target'),
                         '/boot/grub/grub.cfg')

        side_effect_values = {
            '/target/boot/grub': False,
            '/target/boot/grub2': True
        }
        self.assertEqual(gu.guess_grub2_conf('/target'),
                         '/boot/grub2/grub.cfg')

    @mock.patch('bareon.utils.grub.os.path.isdir', return_value=False)
    def test_guess_grub2_conf_not_found(self, mock_isdir):
        self.assertRaises(errors.GrubUtilsError, gu.guess_grub2_conf,
                          '/target')

    @mock.patch('bareon.utils.grub.os.path.isfile')
    def test_guess_grub2_default(self, mock_isfile):
        side_effect_values = {
            '/target/etc/default/grub': True,
            '/target/etc/sysconfig/grub': False
        }

        def side_effect(key):
            return side_effect_values[key]

        mock_isfile.side_effect = side_effect
        self.assertEqual(gu.guess_grub2_default('/target'),
                         '/etc/default/grub')

        side_effect_values = {
            '/target/etc/default/grub': False,
            '/target/etc/sysconfig/grub': True
        }
        self.assertEqual(gu.guess_grub2_default('/target'),
                         '/etc/sysconfig/grub')

    @mock.patch('bareon.utils.grub.os.path.isfile', return_value=False)
    def test_guess_grub2_default_not_found(self, mock_isfile):
        self.assertRaises(errors.GrubUtilsError, gu.guess_grub2_default,
                          '/target')

    @mock.patch('bareon.utils.grub.os.path.isfile', return_value=False)
    def test_guess_grub2_mkconfig_not_found(self, mock_isfile):
        self.assertRaises(errors.GrubUtilsError, gu.guess_grub2_mkconfig,
                          '/target')

    @mock.patch('bareon.utils.grub.os.path.isfile')
    def test_guess_grub2_mkconfig(self, mock_isfile):
        side_effect_values = {
            '/target/sbin/grub-mkconfig': True,
            '/target/sbin/grub2-mkconfig': False,
            '/target/usr/sbin/grub-mkconfig': False,
            '/target/usr/sbin/grub2-mkconfig': False
        }

        def side_effect(key):
            return side_effect_values[key]

        mock_isfile.side_effect = side_effect
        self.assertEqual(gu.guess_grub2_mkconfig('/target'),
                         '/sbin/grub-mkconfig')

        side_effect_values = {
            '/target/sbin/grub-mkconfig': False,
            '/target/sbin/grub2-mkconfig': True,
            '/target/usr/sbin/grub-mkconfig': False,
            '/target/usr/sbin/grub2-mkconfig': False
        }
        self.assertEqual(gu.guess_grub2_mkconfig('/target'),
                         '/sbin/grub2-mkconfig')

        side_effect_values = {
            '/target/sbin/grub-mkconfig': False,
            '/target/sbin/grub2-mkconfig': False,
            '/target/usr/sbin/grub-mkconfig': True,
            '/target/usr/sbin/grub2-mkconfig': False
        }
        self.assertEqual(gu.guess_grub2_mkconfig('/target'),
                         '/usr/sbin/grub-mkconfig')

        side_effect_values = {
            '/target/sbin/grub-mkconfig': False,
            '/target/sbin/grub2-mkconfig': False,
            '/target/usr/sbin/grub-mkconfig': False,
            '/target/usr/sbin/grub2-mkconfig': True
        }
        self.assertEqual(gu.guess_grub2_mkconfig('/target'),
                         '/usr/sbin/grub2-mkconfig')

    @mock.patch('bareon.utils.grub.guess_grub_install')
    @mock.patch('bareon.utils.grub.utils.execute')
    def test_guess_grub_version_1(self, mock_exec, mock_ggi):
        mock_ggi.return_value = '/grub_install'
        mock_exec.return_value = ('foo 0.97 bar', '')
        version = gu.guess_grub_version('/target')
        cmd = 'chroot /target /grub_install --version'.split()
        mock_exec.assert_called_once_with(*cmd)
        self.assertEqual(version, 1)

    @mock.patch('bareon.utils.grub.guess_grub_install')
    @mock.patch('bareon.utils.grub.utils.execute')
    def test_guess_grub_version_2(self, mock_exec, mock_ggi):
        mock_ggi.return_value = '/grub_install'
        mock_exec.return_value = ('foo bar', '')
        version = gu.guess_grub_version('/target')
        cmd = 'chroot /target /grub_install --version'.split()
        mock_exec.assert_called_once_with(*cmd)
        self.assertEqual(version, 2)

    @mock.patch('bareon.utils.grub.os.path.isfile')
    def test_guess_grub(self, mock_isfile):
        side_effect_values = {
            '/target/sbin/grub': True,
            '/target/usr/sbin/grub': False
        }

        def side_effect(key):
            return side_effect_values[key]

        mock_isfile.side_effect = side_effect
        self.assertEqual(gu.guess_grub('/target'),
                         '/sbin/grub')

        side_effect_values = {
            '/target/sbin/grub': False,
            '/target/usr/sbin/grub': True
        }
        self.assertEqual(gu.guess_grub('/target'),
                         '/usr/sbin/grub')

        side_effect_values = {
            '/target/sbin/grub': False,
            '/target/usr/sbin/grub': False
        }
        self.assertRaises(errors.GrubUtilsError, gu.guess_grub, '/target')

    @mock.patch('bareon.utils.grub.os.path.isfile', return_value=False)
    def test_guess_grub_install_not_found(self, mock_isfile):
        self.assertRaises(errors.GrubUtilsError, gu.guess_grub_install,
                          '/target')

    @mock.patch('bareon.utils.grub.os.path.isfile')
    def test_guess_grub_install(self, mock_isfile):
        side_effect_values = {
            '/target/sbin/grub-install': True,
            '/target/sbin/grub2-install': False,
            '/target/usr/sbin/grub-install': False,
            '/target/usr/sbin/grub2-install': False
        }

        def side_effect(key):
            return side_effect_values[key]

        mock_isfile.side_effect = side_effect
        self.assertEqual(gu.guess_grub_install('/target'),
                         '/sbin/grub-install')

        side_effect_values = {
            '/target/sbin/grub-install': False,
            '/target/sbin/grub2-install': True,
            '/target/usr/sbin/grub-install': False,
            '/target/usr/sbin/grub2-install': False
        }
        self.assertEqual(gu.guess_grub_install('/target'),
                         '/sbin/grub2-install')

        side_effect_values = {
            '/target/sbin/grub-install': False,
            '/target/sbin/grub2-install': False,
            '/target/usr/sbin/grub-install': True,
            '/target/usr/sbin/grub2-install': False
        }
        self.assertEqual(gu.guess_grub_install('/target'),
                         '/usr/sbin/grub-install')

        side_effect_values = {
            '/target/sbin/grub-install': False,
            '/target/sbin/grub2-install': False,
            '/target/usr/sbin/grub-install': False,
            '/target/usr/sbin/grub2-install': True
        }
        self.assertEqual(gu.guess_grub_install('/target'),
                         '/usr/sbin/grub2-install')

    @mock.patch('bareon.utils.grub.os.listdir')
    def test_guess_grub1_datadir_default(self, mock_listdir):
        mock_listdir.return_value = ['dir', 'x86_64_dir']
        self.assertEqual('/usr/share/grub/x86_64_dir',
                         gu.guess_grub1_datadir('/target'))

    @mock.patch('bareon.utils.grub.os.listdir')
    def test_guess_grub1_datadir_arch(self, mock_listdir):
        mock_listdir.return_value = ['dir', 'x86_64_dir', 'i386_dir']
        self.assertEqual('/usr/share/grub/i386_dir',
                         gu.guess_grub1_datadir('/target', 'i386'))

    @mock.patch('bareon.utils.grub.os.listdir')
    def test_guess_grub1_datadir_not_found(self, mock_listdir):
        mock_listdir.return_value = ['dir', 'x86_64_dir', 'i386_dir']
        self.assertRaises(errors.GrubUtilsError,
                          gu.guess_grub1_datadir, '/target', 'fake_arch')

    @mock.patch('bareon.utils.grub.utils.guess_filename')
    def test_guess_kernel(self, mock_guess):
        mock_guess.return_value = 'vmlinuz-version'
        self.assertEqual(gu.guess_kernel('/target'), 'vmlinuz-version')
        mock_guess.assert_called_once_with(
            path='/target/boot', regexp=r'^vmlinuz.*')
        mock_guess.reset_mock()

        mock_guess.return_value = 'vmlinuz-version'
        self.assertEqual(gu.guess_kernel('/target', r'^vmlinuz-version.*'),
                         'vmlinuz-version')
        mock_guess.assert_called_once_with(
            path='/target/boot', regexp=r'^vmlinuz-version.*')
        mock_guess.reset_mock()

        mock_guess.return_value = None
        self.assertRaises(errors.GrubUtilsError, gu.guess_kernel, '/target')

    @mock.patch('bareon.utils.grub.utils.guess_filename')
    def test_guess_initrd(self, mock_guess):
        mock_guess.return_value = 'initrd-version'
        self.assertEqual(gu.guess_initrd('/target'), 'initrd-version')
        mock_guess.assert_called_once_with(
            path='/target/boot', regexp=r'^(initrd|initramfs).*')
        mock_guess.reset_mock()

        mock_guess.return_value = 'initramfs-version'
        self.assertEqual(gu.guess_initrd('/target', r'^initramfs-version.*'),
                         'initramfs-version')
        mock_guess.assert_called_once_with(
            path='/target/boot', regexp=r'^initramfs-version.*')
        mock_guess.reset_mock()

        mock_guess.return_value = None
        self.assertRaises(errors.GrubUtilsError, gu.guess_initrd, '/target')

    @mock.patch('bareon.utils.grub.grub1_stage1')
    @mock.patch('bareon.utils.grub.grub1_mbr')
    def test_grub1_install(self, mock_mbr, mock_stage1):
        install_devices = ['/dev/foo', '/dev/bar']
        expected_calls_mbr = []
        for install_device in install_devices:
            expected_calls_mbr.append(
                mock.call(install_device, '/dev/foo', '0', chroot='/target'))
        gu.grub1_install(install_devices, '/dev/foo1', '/target')
        self.assertEqual(expected_calls_mbr, mock_mbr.call_args_list)
        mock_stage1.assert_called_once_with(chroot='/target')
        # should raise exception if boot_device (second argument)
        # is not a partition but a whole disk
        self.assertRaises(errors.GrubUtilsError, gu.grub1_install,
                          '/dev/foo', '/dev/foo', chroot='/target')

    @mock.patch('bareon.utils.grub.guess_grub')
    @mock.patch('bareon.utils.grub.os.chmod')
    @mock.patch('bareon.utils.grub.utils.execute')
    def test_grub1_mbr_install_differs_boot(self, mock_exec,
                                            mock_chmod, mock_guess):
        mock_guess.return_value = '/sbin/grub'
        mock_exec.return_value = ('stdout', 'stderr')

        # install_device != boot_disk
        batch = 'device (hd0) /dev/foo\n'
        batch += 'geometry (hd0) 130 255 63\n'
        batch += 'device (hd1) /dev/bar\n'
        batch += 'geometry (hd1) 130 255 63\n'
        batch += 'root (hd1,0)\n'
        batch += 'setup (hd0)\n'
        batch += 'quit\n'
        script = 'cat /tmp/grub.batch | /sbin/grub --no-floppy --batch'

        mock_open = mock.mock_open()
        with mock.patch('bareon.utils.grub.open', new=mock_open,
                        create=True):
            gu.grub1_mbr('/dev/foo', '/dev/bar', '0', chroot='/target')
        self.assertEqual(
            mock_open.call_args_list,
            [mock.call('/target/tmp/grub.batch', 'wt', encoding='utf-8'),
             mock.call('/target/tmp/grub.sh', 'wt', encoding='utf-8')]
        )
        mock_open_file = mock_open()
        self.assertEqual(
            mock_open_file.write.call_args_list,
            [mock.call(batch), mock.call(script)]
        )
        mock_chmod.assert_called_once_with('/target/tmp/grub.sh', 0o755)
        mock_exec.assert_called_once_with(
            'chroot', '/target', '/tmp/grub.sh',
            run_as_root=True, check_exit_code=[0])

    @mock.patch('bareon.utils.grub.guess_grub')
    @mock.patch('bareon.utils.grub.os.chmod')
    @mock.patch('bareon.utils.grub.utils.execute')
    def test_grub1_mbr_install_same_as_boot(self, mock_exec,
                                            mock_chmod, mock_guess):
        mock_guess.return_value = '/sbin/grub'
        mock_exec.return_value = ('stdout', 'stderr')

        # install_device == boot_disk
        batch = 'device (hd0) /dev/foo\n'
        batch += 'geometry (hd0) 130 255 63\n'
        batch += 'root (hd0,0)\n'
        batch += 'setup (hd0)\n'
        batch += 'quit\n'
        script = 'cat /tmp/grub.batch | /sbin/grub --no-floppy --batch'

        mock_open = mock.mock_open()
        with mock.patch('bareon.utils.grub.open', new=mock_open,
                        create=True):
            gu.grub1_mbr('/dev/foo', '/dev/foo', '0', chroot='/target')
        self.assertEqual(
            mock_open.call_args_list,
            [mock.call('/target/tmp/grub.batch', 'wt', encoding='utf-8'),
             mock.call('/target/tmp/grub.sh', 'wt', encoding='utf-8')]
        )
        mock_open_file = mock_open()
        self.assertEqual(
            mock_open_file.write.call_args_list,
            [mock.call(batch), mock.call(script)]
        )
        mock_chmod.assert_called_once_with('/target/tmp/grub.sh', 0o755)
        mock_exec.assert_called_once_with(
            'chroot', '/target', '/tmp/grub.sh',
            run_as_root=True, check_exit_code=[0])

    @mock.patch('bareon.utils.grub.shutil.copy')
    @mock.patch('bareon.utils.grub.guess_grub1_datadir',
                return_value='/fake_datadir')
    @mock.patch('bareon.utils.grub.os.remove')
    @mock.patch('bareon.utils.grub.os.listdir')
    def test_grub1_stage1(self, mock_listdir, mock_remove, mock_datadir,
                          mock_copy):
        mock_listdir.side_effect = [['stage1', 'stage2', 'e2fs_stage_1_5',
                                     'fat_stage1_5'],
                                    ['stage1', 'stage2', 'e2fs_stage_1_5',
                                     'fat_stage1_5', 'jfs_stage1_5']]
        gu.grub1_stage1(chroot='/target')
        mock_datadir.assert_called_once_with(chroot='/target')
        expected_remove_calls = [
            mock.call('/target/boot/grub/stage1'),
            mock.call('/target/boot/grub/stage2'),
            mock.call('/target/boot/grub/fat_stage1_5')]
        self.assertEqual(expected_remove_calls, mock_remove.call_args_list)
        expected_copy_calls = [
            mock.call('/target/fake_datadir/stage1',
                      '/target/boot/grub/stage1'),
            mock.call('/target/fake_datadir/stage2',
                      '/target/boot/grub/stage2'),
            mock.call('/target/fake_datadir/fat_stage1_5',
                      '/target/boot/grub/fat_stage1_5'),
            mock.call('/target/fake_datadir/jfs_stage1_5',
                      '/target/boot/grub/jfs_stage1_5')]
        self.assertEqual(expected_copy_calls, mock_copy.call_args_list)

    @mock.patch('bareon.utils.grub.guess_kernel')
    @mock.patch('bareon.utils.grub.guess_initrd')
    def test_grub1_cfg_kernel_initrd_are_not_set(self, mock_initrd,
                                                 mock_kernel):
        mock_kernel.return_value = 'kernel-version'
        mock_initrd.return_value = 'initrd-version'
        config = """
default=0
timeout=5
title Default (kernel-version)
    kernel /kernel-version kernel-params
    initrd /initrd-version
    """

        mock_open = mock.mock_open()
        with mock.patch('bareon.utils.grub.open', new=mock_open,
                        create=True):
            gu.grub1_cfg(chroot='/target', kernel_params='kernel-params')
        mock_open.assert_called_once_with('/target/boot/grub/grub.conf', 'wt',
                                          encoding='utf-8')
        mock_open_file = mock_open()
        mock_open_file.write.assert_called_once_with(config)

    def test_grub1_cfg_kernel_initrd_are_set(self):
        config = """
default=0
timeout=10
title Default (kernel-version-set)
    kernel /kernel-version-set kernel-params
    initrd /initrd-version-set
    """

        mock_open = mock.mock_open()
        with mock.patch('bareon.utils.grub.open', new=mock_open,
                        create=True):
            gu.grub1_cfg(kernel='kernel-version-set',
                         initrd='initrd-version-set',
                         chroot='/target', kernel_params='kernel-params',
                         grub_timeout=10)
        mock_open.assert_called_once_with('/target/boot/grub/grub.conf', 'wt',
                                          encoding='utf-8')
        mock_open_file = mock_open()
        mock_open_file.write.assert_called_once_with(config)

    @mock.patch('bareon.utils.grub.utils.execute')
    @mock.patch('bareon.utils.grub.guess_grub_install')
    def test_grub2_install(self, mock_guess_grub, mock_exec):
        mock_guess_grub.return_value = '/sbin/grub'
        expected_calls = [
            mock.call('chroot', '/target', '/sbin/grub', '/dev/foo',
                      run_as_root=True, check_exit_code=[0]),
            mock.call('chroot', '/target', '/sbin/grub', '/dev/bar',
                      run_as_root=True, check_exit_code=[0])
        ]
        gu.grub2_install(['/dev/foo', '/dev/bar'], chroot='/target')
        self.assertEqual(mock_exec.call_args_list, expected_calls)

    @unittest2.skip("Fix after cray rebase")
    @mock.patch('bareon.utils.grub.guess_grub2_conf')
    @mock.patch('bareon.utils.grub.guess_grub2_mkconfig')
    @mock.patch('bareon.utils.grub.utils.execute')
    @mock.patch('bareon.utils.grub.guess_grub2_default')
    def test_grub2_cfg(self, mock_def, mock_exec, mock_mkconfig, mock_conf):
        mock_def.return_value = '/etc/default/grub'
        mock_mkconfig.return_value = '/sbin/grub-mkconfig'
        mock_conf.return_value = '/boot/grub/grub.cfg'

        orig_content = """foo
GRUB_CMDLINE_LINUX="kernel-params-orig"
bar"""

        with mock.patch('bareon.utils.grub.open',
                        new=mock.mock_open(read_data=orig_content),
                        create=True) as mock_open:
            mock_open.return_value = mock.MagicMock(spec=io.IOBase)
            handle = mock_open.return_value.__enter__.return_value
            handle.__iter__.return_value = StringIO(orig_content)
            gu.grub2_cfg(kernel_params='kernel-params-new', chroot='/target',
                         grub_timeout=10)

            self.assertEqual(
                mock_open.call_args_list,
                [mock.call('/target/etc/default/grub'),
                 mock.call('/target/etc/default/grub', 'wt', encoding='utf-8')]
            )

        gu.grub2_cfg(kernel_params='kernel-params-new', chroot='/target',
                     grub_timeout=10)

        mock_exec.assert_called_once_with('chroot', '/target',
                                          '/sbin/grub-mkconfig',
                                          '-o', '/boot/grub/grub.cfg',
                                          run_as_root=True)
