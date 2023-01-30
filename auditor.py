# Copyright (c) 2010-2012 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
from swift import gettext_ as _
from random import random

from eventlet import Timeout

import swift.common.db
from swift.container.backend import ContainerBroker, DATADIR
from swift.common.utils import get_logger, audit_location_generator, \
    config_true_value, dump_recon_cache, ratelimit_sleep
from swift.common.daemon import Daemon


class ContainerAuditor(Daemon):
    """Audit containers."""

    def __init__(self, conf, logger=None):
        self.conf = conf
        self.logger = logger or get_logger(conf, log_route='container-auditor')
        self.devices = conf.get('devices', '/srv/node')
        self.mount_check = config_true_value(conf.get('mount_check', 'true'))
        self.interval = int(conf.get('interval', 1800))
        self.container_passes = 0
        self.container_failures = 0
        self.containers_running_time = 0
        self.max_containers_per_second = \
            float(conf.get('containers_per_second', 200))
        swift.common.db.DB_PREALLOCATION = \
            config_true_value(conf.get('db_preallocation', 'f'))
        self.recon_cache_path = conf.get('recon_cache_path',
                                         '/var/cache/swift')
        self.rcache = os.path.join(self.recon_cache_path, "container.recon")

    def _one_audit_pass(self, reported):
        all_locs = audit_location_generator(self.devices, DATADIR, '.db',
                                            mount_check=self.mount_check,
                                            logger=self.logger)
        for path, device, partition in all_locs:
            self.container_audit(path)
            if time.time() - reported >= 3600:  # once an hour
                self.logger.info(
                    _('Since %(time)s: Container audits: %(pass)s passed '
                      'audit, %(fail)s failed audit'),
                    {'time': time.ctime(reported),
                     'pass': self.container_passes,
                     'fail': self.container_failures})
                dump_recon_cache(
                    {'container_audits_since': reported,
                     'container_audits_passed': self.container_passes,
                     'container_audits_failed': self.container_failures},
                    self.rcache, self.logger)
                reported = time.time()
                self.container_passes = 0
                self.container_failures = 0
            self.containers_running_time = ratelimit_sleep(
                self.containers_running_time, self.max_containers_per_second)
        return reported

    def run_forever(self, *args, **kwargs):
        """Run the container audit until stopped."""
        reported = time.time()
        time.sleep(random() * self.interval)
        while True:
            self.logger.info(_('Begin container audit pass.'))
            begin = time.time()
            try:
                reported = self._one_audit_pass(reported)
            except (Exception, Timeout):
                self.logger.increment('errors')
                self.logger.exception(_('ERROR auditing'))
            elapsed = time.time() - begin
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)
            self.logger.info(
                _('Container audit pass completed: %.02fs'), elapsed)
            dump_recon_cache({'container_auditor_pass_completed': elapsed},
                             self.rcache, self.logger)

    def run_once(self, *args, **kwargs):
        """Run the container audit once."""
        self.logger.info(_('Begin container audit "once" mode'))
        begin = reported = time.time()
        self._one_audit_pass(reported)
        elapsed = time.time() - begin
        self.logger.info(
            _('Container audit "once" mode completed: %.02fs'), elapsed)
        dump_recon_cache({'container_auditor_pass_completed': elapsed},
                         self.rcache, self.logger)

    def container_audit(self, path):
        """
        Audits the given container path

        :param path: the path to a container db
        """
        start_time = time.time()
        try:
            broker = ContainerBroker(path)
            if not broker.is_deleted():
                broker.get_info()
                self.logger.increment('passes')
                self.container_passes += 1
                self.logger.debug('Audit passed for %s', broker)
        except (Exception, Timeout):
            self.logger.increment('failures')
            self.container_failures += 1
            self.logger.exception(_('ERROR Could not get container info %s'),
                                  path)
        self.logger.timing_since('timing', start_time)
file managers
        # can find all diskfile locations regardless of policy -- so for now
        # just use Policy-0's manager.
        all_locs = (self.diskfile_router[POLICIES[0]]
                    .object_audit_location_generator(
                        device_dirs=device_dirs,
                        auditor_type=self.auditor_type))
        for location in all_locs:
            loop_time = time.time()
            self.failsafe_object_audit(location)
            self.logger.timing_since('timing', loop_time)
            self.files_running_time = ratelimit_sleep(
                self.files_running_time, self.max_files_per_second)
            self.total_files_processed += 1
            now = time.time()
            if now - self.last_logged >= self.log_time:
                self.logger.info(_(
                    'Object audit (%(type)s). '
                    'Since %(start_time)s: Locally: %(passes)d passed, '
                    '%(quars)d quarantined, %(errors)d errors, '
                    'files/sec: %(frate).2f, bytes/sec: %(brate).2f, '
                    'Total time: %(total).2f, Auditing time: %(audit).2f, '
                    'Rate: %(audit_rate).2f') % {
                        'type': '%s%s' % (self.auditor_type, description),
                        'start_time': time.ctime(reported),
                        'passes': self.passes, 'quars': self.quarantines,
                        'errors': self.errors,
                        'frate': self.passes / (now - reported),
                        'brate': self.bytes_processed / (now - reported),
                        'total': (now - begin), 'audit': time_auditing,
                        'audit_rate': time_auditing / (now - begin)})
                cache_entry = self.create_recon_nested_dict(
                    'object_auditor_stats_%s' % (self.auditor_type),
                    device_dirs,
                    {'errors': self.errors, 'passes': self.passes,
                     'quarantined': self.quarantines,
                     'bytes_processed': self.bytes_processed,
                     'start_time': reported, 'audit_time': time_auditing})
                dump_recon_cache(cache_entry, self.rcache, self.logger)
                reported = now
                total_quarantines += self.quarantines
                total_errors += self.errors
                self.passes = 0
                self.quarantines = 0
                self.errors = 0
                self.bytes_processed = 0
                self.last_logged = now
            time_auditing += (now - loop_time)
        # Avoid divide by zero during very short runs
        elapsed = (time.time() - begin) or 0.000001
        self.logger.info(_(
            'Object audit (%(type)s) "%(mode)s" mode '
            'completed: %(elapsed).02fs. Total quarantined: %(quars)d, '
            'Total errors: %(errors)d, Total files/sec: %(frate).2f, '
            'Total bytes/sec: %(brate).2f, Auditing time: %(audit).2f, '
            'Rate: %(audit_rate).2f') % {
                'type': '%s%s' % (self.auditor_type, description),
                'mode': mode, 'elapsed': elapsed,
                'quars': total_quarantines + self.quarantines,
                'errors': total_errors + self.errors,
                'frate': self.total_files_processed / elapsed,
                'brate': self.total_bytes_processed / elapsed,
                'audit': time_auditing, 'audit_rate': time_auditing / elapsed})
        if self.stats_sizes:
            self.logger.info(
                _('Object audit stats: %s') % json.dumps(self.stats_buckets))

        # Unset remaining partitions to not skip them in the next run
        diskfile.clear_auditor_status(self.devices, self.auditor_type)

    def record_stats(self, obj_size):
        """
        Based on config's object_size_stats will keep track of how many objects
        fall into the specified ranges. For example with the following:

        object_size_stats = 10, 100, 1024

        and your system has 3 objects of sizes: 5, 20, and 10000 bytes the log
        will look like: {"10": 1, "100": 1, "1024": 0, "OVER": 1}
        """
        for size in self.stats_sizes:
            if obj_size <= size:
                self.stats_buckets[size] += 1
                break
        else:
            self.stats_buckets["OVER"] += 1

    def failsafe_object_audit(self, location):
        """
        Entrypoint to object_audit, with a failsafe generic exception handler.
        """
        try:
            self.object_audit(location)
        except (Exception, Timeout):
            self.logger.increment('errors')
            self.errors += 1
            self.logger.exception(_('ERROR Trying to audit %s'), location)

    def object_audit(self, location):
        """
        Audits the given object location.

        :param location: an audit location
                         (from diskfile.object_audit_location_generator)
        """
        def raise_dfq(msg):
            raise DiskFileQuarantined(msg)

        diskfile_mgr = self.diskfile_router[location.policy]
        # this method doesn't normally raise errors, even if the audit
        # location does not exist; if this raises an unexpected error it
        # will get logged in failsafe
        df = diskfile_mgr.get_diskfile_from_audit_location(location)
        reader = None
        try:
            with df.open():
                metadata = df.get_metadata()
                obj_size = int(metadata['Content-Length'])
                if self.stats_sizes:
                    self.record_stats(obj_size)
                if obj_size and not self.zero_byte_only_at_fps:
                    reader = df.reader(_quarantine_hook=raise_dfq)
            if reader:
                with closing(reader):
                    for chunk in reader:
                        chunk_len = len(chunk)
                        self.bytes_running_time = ratelimit_sleep(
                            self.bytes_running_time,
                            self.max_bytes_per_second,
                            incr_by=chunk_len)
                        self.bytes_processed += chunk_len
                        self.total_bytes_processed += chunk_len
        except DiskFileNotExist:
            pass
        except DiskFileQuarantined as err:
            self.quarantines += 1
            self.logger.error(_('ERROR Object %(obj)s failed audit and was'
                                ' quarantined: %(err)s'),
                              {'obj': location, 'err': err})
        self.passes += 1
        # _ondisk_info attr is initialized to None and filled in by open
        ondisk_info_dict = df._ondisk_info or {}
        if 'unexpected' in ondisk_info_dict:
            is_rsync_tempfile = lambda fpath: RE_RSYNC_TEMPFILE.match(
                os.path.basename(fpath))
            rsync_tempfile_paths = filter(is_rsync_tempfile,
                                          ondisk_info_dict['unexpected'])
            mtime = time.time() - self.rsync_tempfile_timeout
            unlink_paths_older_than(rsync_tempfile_paths, mtime)


class ObjectAuditor(Daemon):
    """Audit objects."""

    def __init__(self, conf, **options):
        self.conf = conf
        self.logger = get_logger(conf, log_route='object-auditor')
        self.devices = conf.get('devices', '/srv/node')
        self.concurrency = int(conf.get('concurrency', 1))
        self.conf_zero_byte_fps = int(
            conf.get('zero_byte_files_per_second', 50))
        self.recon_cache_path = conf.get('recon_cache_path',
                                         '/var/cache/swift')
        self.rcache = os.path.join(self.recon_cache_path, "object.recon")
        self.interval = int(conf.get('interval', 30))

    def _sleep(self):
        time.sleep(self.interval)

    def clear_recon_cache(self, auditor_type):
        """Clear recon cache entries"""
        dump_recon_cache({'object_auditor_stats_%s' % auditor_type: {}},
                         self.rcache, self.logger)

    def run_audit(self, **kwargs):
        """Run the object audit"""
        mode = kwargs.get('mode')
        zero_byte_only_at_fps = kwargs.get('zero_byte_fps', 0)
        device_dirs = kwargs.get('device_dirs')
        worker = AuditorWorker(self.conf, self.logger, self.rcache,
                               self.devices,
                               zero_byte_only_at_fps=zero_byte_only_at_fps)
        worker.audit_all_objects(mode=mode, device_dirs=device_dirs)

    def fork_child(self, zero_byte_fps=False, **kwargs):
        """Child execution"""
        pid = os.fork()
        if pid:
            return pid
        else:
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            if zero_byte_fps:
                kwargs['zero_byte_fps'] = self.conf_zero_byte_fps
            try:
                self.run_audit(**kwargs)
            except Exception as e:
                self.logger.exception(
                    _("ERROR: Unable to run auditing: %s") % e)
            finally:
                sys.exit()

    def audit_loop(self, parent, zbo_fps, override_devices=None, **kwargs):
        """Parallel audit loop"""
        self.clear_recon_cache('ALL')
        self.clear_recon_cache('ZBF')
        once = kwargs.get('mode') == 'once'
        kwargs['device_dirs'] = override_devices
        if parent:
            kwargs['zero_byte_fps'] = zbo_fps
            self.run_audit(**kwargs)
        else:
            pids = set()
            if self.conf_zero_byte_fps:
                zbf_pid = self.fork_child(zero_byte_fps=True, **kwargs)
                pids.add(zbf_pid)
            if self.concurrency == 1:
                # Audit all devices in 1 process
                pids.add(self.fork_child(**kwargs))
            else:
                # Divide devices amongst parallel processes set by
                # self.concurrency.  Total number of parallel processes
                # is self.concurrency + 1 if zero_byte_fps.
                parallel_proc = self.concurrency + 1 if \
                    self.conf_zero_byte_fps else self.concurrency
                device_list = list(override_devices) if override_devices else \
                    listdir(self.devices)
                shuffle(device_list)
                while device_list:
                    pid = None
                    if len(pids) == parallel_proc:
                        pid = os.wait()[0]
                        pids.discard(pid)

                    if self.conf_zero_byte_fps and pid == zbf_pid and once:
                        # If we're only running one pass and the ZBF scanner
                        # finished, don't bother restarting it.
                        zbf_pid = -100
                    elif self.conf_zero_byte_fps and pid == zbf_pid:
                        # When we're running forever, the ZBF scanner must
                        # be restarted as soon as it finishes.
                        kwargs['device_dirs'] = override_devices
                        # sleep between ZBF scanner forks
                        self._sleep()
                        zbf_pid = self.fork_child(zero_byte_fps=True, **kwargs)
                        pids.add(zbf_pid)
                    else:
                        kwargs['device_dirs'] = [device_list.pop()]
                        pids.add(self.fork_child(**kwargs))
            while pids:
                pid = os.wait()[0]
                # ZBF scanner must be restarted as soon as it finishes
                # unless we're in run-once mode
                if self.conf_zero_byte_fps and pid == zbf_pid and \
                   len(pids) > 1 and not once:
                    kwargs['device_dirs'] = override_devices
                    # sleep between ZBF scanner forks
                    self._sleep()
                    zbf_pid = self.fork_child(zero_byte_fps=True, **kwargs)
                    pids.add(zbf_pid)
                pids.discard(pid)

    def run_forever(self, *args, **kwargs):
        """Run the object audit until stopped."""
        # zero byte only command line option
        zbo_fps = kwargs.get('zero_byte_fps', 0)
        parent = False
        if zbo_fps:
            # only start parent
            parent = True
        kwargs = {'mode': 'forever'}

        while True:
            try:
                self.audit_loop(parent, zbo_fps, **kwargs)
            except (Exception, Timeout) as err:
                self.logger.exception(_('ERROR auditing: %s'), err)
            self._sleep()

    def run_once(self, *args, **kwargs):
        """Run the object audit once"""
        # zero byte only command line option
        zbo_fps = kwargs.get('zero_byte_fps', 0)
        override_devices = list_from_csv(kwargs.get('devices'))
        # Remove bogus entries and duplicates from override_devices
        override_devices = list(
            set(listdir(self.devices)).intersection(set(override_devices)))
        parent = False
        if zbo_fps:
            # only start parent
            parent = True
        kwargs = {'mode': 'once'}

        try:
            self.audit_loop(parent, zbo_fps, override_devices=override_devices,
                            **kwargs)
        except (Exception, Timeout) as err:
            self.logger.exception(_('ERROR auditing: %s'), err)
