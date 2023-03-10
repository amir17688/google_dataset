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

from io import open
import os
import re
import shutil
import six

from contextlib import contextmanager

from bareon import errors
from bareon.openstack.common import log as logging
from bareon.utils import utils

LOG = logging.getLogger(__name__)


def guess_grub2_conf(chroot=''):
    for filename in ('/boot/grub2/grub.cfg', '/boot/grub/grub.cfg'):
        if os.path.isdir(os.path.dirname(chroot + filename)):
            return filename
    raise errors.GrubUtilsError('grub2 config file not found')


def guess_grub2_default(chroot=''):
    for filename in ('/etc/default/grub', '/etc/sysconfig/grub'):
        if os.path.isfile(chroot + filename):
            return filename
    raise errors.GrubUtilsError('grub2 default config file not found')


def guess_grub2_mkconfig(chroot=''):
    for grub_mkconfig in \
            ('/sbin/grub-mkconfig', '/sbin/grub2-mkconfig',
             '/usr/sbin/grub-mkconfig', '/usr/sbin/grub2-mkconfig'):
        if os.path.isfile(chroot + grub_mkconfig):
            return grub_mkconfig
    raise errors.GrubUtilsError('grub2 mkconfig binary not found')


def guess_grub_version(chroot=''):
    grub_install = guess_grub_install(chroot=chroot)
    LOG.debug('Trying to run %s --version' % grub_install)
    cmd = [grub_install, '--version']
    if chroot:
        cmd[:0] = ['chroot', chroot]
    result = utils.execute(*cmd)
    version = 1 if result[0].find('0.97') > 0 else 2
    LOG.debug('Looks like grub version is %s' % version)
    return version


def guess_grub(chroot=''):
    for grub in ('/sbin/grub', '/usr/sbin/grub'):
        LOG.debug('Looking for grub: trying %s' % grub)
        if os.path.isfile(chroot + grub):
            LOG.debug('grub found: %s' % grub)
            return grub
    raise errors.GrubUtilsError('grub not found')


def guess_grub_install(chroot=''):
    for grub_install in ('/sbin/grub-install', '/sbin/grub2-install',
                         '/usr/sbin/grub-install', '/usr/sbin/grub2-install'):
        LOG.debug('Looking for grub-install: trying %s' % grub_install)
        if os.path.isfile(chroot + grub_install):
            LOG.debug('grub-install found: %s' % grub_install)
            return grub_install
    raise errors.GrubUtilsError('grub-install not found in tenant image')


def guess_grub1_datadir(chroot='', arch='x86_64'):
    LOG.debug('Looking for grub data directory')
    for d in os.listdir(chroot + '/usr/share/grub'):
        if arch in d:
            LOG.debug('Looks like grub data directory '
                      'is /usr/share/grub/%s' % d)
            return '/usr/share/grub/' + d
    raise errors.GrubUtilsError(
        'grub data directory not found for arch %s' % arch)


def guess_kernel(chroot='', regexp=None):
    """Tries to guess kernel by regexp

    :param chroot: Path to chroot
    :param regexp: (String) Regular expression (must have python syntax).
    Default is r'^vmlinuz.*'
    """
    kernel = utils.guess_filename(
        path=os.path.join(chroot, 'boot'),
        regexp=(regexp or r'^vmlinuz.*'))

    if kernel:
        return kernel

    raise errors.GrubUtilsError('Error while trying to find kernel: '
                                'regexp=%s' % regexp)


def guess_initrd(chroot='', regexp=None):
    """Tries to guess initrd by regexp

    :param chroot: Path to chroot
    :param regexp: (String) Regular expression (must have python syntax).
    Default is r'^(initrd|initramfs).*'
    """
    initrd = utils.guess_filename(
        path=os.path.join(chroot, 'boot'),
        regexp=(regexp or r'^(initrd|initramfs).*'))

    if initrd:
        return initrd

    raise errors.GrubUtilsError('Error while trying to find initrd: '
                                'regexp=%s' % regexp)


def grub1_install(install_devices, boot_device, chroot=''):
    match = re.search(r'(.+?)(p?)(\d*)$', boot_device)
    # Checking whether boot device is a partition
    # !!! It must be a partition not a whole disk. !!!
    if not match.group(3):
        raise errors.GrubUtilsError(
            'Error while installing legacy grub: '
            'boot device must be a partition')
    boot_disk = match.group(1)
    boot_part = str(int(match.group(3)) - 1)
    grub1_stage1(chroot=chroot)
    for install_device in install_devices:
        grub1_mbr(install_device, boot_disk, boot_part, chroot=chroot)


def grub1_mbr(install_device, boot_disk, boot_part, chroot=''):
    # The device on which we are going to install
    # stage1 needs to be mapped as hd0, otherwise system won't be able to boot.
    batch = 'device (hd0) {0}\n'.format(install_device)
    # That is much easier to use grub-install, but unfortunately
    # it is not able to install bootloader on huge disks.
    # Instead we set drive geometry manually to avoid grub register
    # overlapping. We set it so as to make grub
    # thinking that disk size is equal to 1G.
    # 130 cylinders * (16065 * 512 = 8225280 bytes) = 1G
    # We also assume that boot partition is in the beginning
    # of disk between 0 and 1G.
    batch += 'geometry (hd0) 130 255 63\n'
    if boot_disk != install_device:
        batch += 'device (hd1) {0}\n'.format(boot_disk)
        batch += 'geometry (hd1) 130 255 63\n'
        batch += 'root (hd1,{0})\n'.format(boot_part)
    else:
        batch += 'root (hd0,{0})\n'.format(boot_part)
    batch += 'setup (hd0)\n'
    batch += 'quit\n'

    with open(chroot + '/tmp/grub.batch', 'wt', encoding='utf-8') as f:
        LOG.debug('Grub batch content: \n%s' % batch)
        f.write(six.text_type(batch))

    script = 'cat /tmp/grub.batch | {0} --no-floppy --batch'.format(
        guess_grub(chroot=chroot))
    with open(chroot + '/tmp/grub.sh', 'wt', encoding='utf-8') as f:
        LOG.debug('Grub script content: \n%s' % script)
        f.write(six.text_type(script))

    os.chmod(chroot + '/tmp/grub.sh', 0o755)
    cmd = ['/tmp/grub.sh']
    if chroot:
        cmd[:0] = ['chroot', chroot]
    stdout, stderr = utils.execute(*cmd, run_as_root=True, check_exit_code=[0])
    LOG.debug('Grub script stdout: \n%s' % stdout)
    LOG.debug('Grub script stderr: \n%s' % stderr)


def grub1_stage1(chroot=''):
    LOG.debug('Installing grub stage1 files')
    for f in os.listdir(chroot + '/boot/grub'):
        if f in ('stage1', 'stage2') or 'stage1_5' in f:
            LOG.debug('Removing: %s' % chroot + os.path.join('/boot/grub', f))
            os.remove(chroot + os.path.join('/boot/grub', f))
    grub1_datadir = guess_grub1_datadir(chroot=chroot)
    for f in os.listdir(chroot + grub1_datadir):
        if f in ('stage1', 'stage2') or 'stage1_5' in f:
            LOG.debug('Copying %s from %s to /boot/grub' % (f, grub1_datadir))
            shutil.copy(chroot + os.path.join(grub1_datadir, f),
                        chroot + os.path.join('/boot/grub', f))


def grub1_cfg(kernel=None, initrd=None,
              kernel_params='', chroot='', grub_timeout=5):

    if not kernel:
        kernel = guess_kernel(chroot=chroot)
    if not initrd:
        initrd = guess_initrd(chroot=chroot)

    config = """
default=0
timeout={grub_timeout}
title Default ({kernel})
    kernel /{kernel} {kernel_params}
    initrd /{initrd}
    """.format(kernel=kernel, initrd=initrd,
               kernel_params=kernel_params,
               grub_timeout=grub_timeout)
    with open(chroot + '/boot/grub/grub.conf', 'wt', encoding='utf-8') as f:
        f.write(six.text_type(config))


def grub2_install(install_devices, chroot='', boot_root='', lvm_boot=False):
    grub_install = guess_grub_install(chroot=chroot)
    for install_device in install_devices:
        cmd = [grub_install, install_device]
        if lvm_boot:
            cmd.append('--modules="lvm"')
        if boot_root:
            cmd.append('--boot-directory={}/boot'.format(boot_root))
        elif chroot:
            cmd[:0] = ['chroot', chroot]

        utils.execute(*cmd, run_as_root=True, check_exit_code=[0])


def grub2_cfg(kernel_params='', chroot='', grub_timeout=5, lvm_boot=False):
    with grub2_prepare(kernel_params, chroot, grub_timeout, lvm_boot):
        cmd = [guess_grub2_mkconfig(chroot), '-o', guess_grub2_conf(chroot)]
        if chroot:
            cmd[:0] = ['chroot', chroot]
        utils.execute(*cmd, run_as_root=True)


def grub2_cfg_bundled(kernel_params='', chroot='', grub_timeout=5,
                      lvm_boot=False):
    # NOTE(oberezovskyi): symlink is required because of grub2-probe fails
    # to find device with root partition of fuel agent.
    # It's actuall in the ram and "device" is "rootfs"
    os.symlink(chroot, '/tmp/rootfs')

    with grub2_prepare(kernel_params, chroot, grub_timeout, lvm_boot):
        # NOTE(oberezovskyi): required to prevent adding boot entries for
        # ramdisk
        os.remove('/etc/grub.d/10_linux')

        cmd = [guess_grub2_mkconfig(), '-o', chroot + '/boot/grub2/grub.cfg']
        utils.execute(*cmd, run_as_root=True, cwd='/tmp/')
        os.remove('/tmp/rootfs')


@contextmanager
def grub2_prepare(kernel_params='', chroot='', grub_timeout=5, lvm_boot=False):
    old_env = os.environ.copy()
    os.environ['GRUB_DISABLE_SUBMENU'] = 'y'
    os.environ['GRUB_CMDLINE_LINUX_DEFAULT'] = kernel_params
    os.environ['GRUB_CMDLINE_LINUX'] = kernel_params
    os.environ['GRUB_HIDDEN_TIMEOUT'] = str(grub_timeout)
    os.environ['GRUB_RECORDFAIL_TIMEOUT'] = str(grub_timeout)
    os.environ['GRUB_DISABLE_OS_PROBER'] = 'true'
    os.environ['GRUB_DISABLE_LINUX_UUID'] = 'true'
    os.environ['GRUB_DISABLE_RECOVERY'] = 'true'

    if lvm_boot:
        os.environ['GRUB_PRELOAD_MODULES'] = 'lvm'

    if os.path.isfile(os.path.join(chroot, 'boot/grub/grub.conf')):
        os.remove(os.path.join(chroot, 'boot/grub/grub.conf'))

    yield

    os.environ = old_env


def guess_grub_cfg(chroot=''):
    for grub_cfg in ('grub/grub.cfg', 'grub2/grub.cfg'):
        if os.path.isfile(os.path.join(chroot, grub_cfg)):
            return grub_cfg
    raise errors.GrubUtilsError('grub2 mkconfig binary not found')
