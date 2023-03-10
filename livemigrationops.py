# Copyright 2012 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Management class for live migration VM operations.
"""

import nova.conf
from nova.objects import migrate_data as migrate_data_obj
from os_win import utilsfactory
from oslo_log import log as logging
from oslo_utils import excutils

from hyperv.nova import block_device_manager
from hyperv.nova import imagecache
from hyperv.nova import pathutils
from hyperv.nova import serialconsoleops
from hyperv.nova import vmops
from hyperv.nova import volumeops

LOG = logging.getLogger(__name__)
CONF = nova.conf.CONF


class LiveMigrationOps(object):
    def __init__(self):
        self._livemigrutils = utilsfactory.get_livemigrationutils()
        self._pathutils = pathutils.PathUtils()
        self._vmops = vmops.VMOps()
        self._volumeops = volumeops.VolumeOps()
        self._serial_console_ops = serialconsoleops.SerialConsoleOps()
        self._imagecache = imagecache.ImageCache()
        self._block_dev_man = block_device_manager.BlockDeviceInfoManager()

    def live_migration(self, context, instance_ref, dest, post_method,
                       recover_method, block_migration=False,
                       migrate_data=None):
        LOG.debug("live_migration called", instance=instance_ref)
        instance_name = instance_ref["name"]

        try:
            self._vmops.copy_vm_dvd_disks(instance_name, dest)

            # We must make sure that the console log workers are stopped,
            # otherwise we won't be able to delete / move VM log files.
            self._serial_console_ops.stop_console_handler(instance_name)

            self._pathutils.copy_vm_console_logs(instance_name, dest)
            self._livemigrutils.live_migrate_vm(instance_name,
                                                dest)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.debug("Calling live migration recover_method "
                          "for instance: %s", instance_name)
                recover_method(context, instance_ref, dest, block_migration)

        LOG.debug("Calling live migration post_method for instance: %s",
                  instance_name)
        post_method(context, instance_ref, dest, block_migration)

    def pre_live_migration(self, context, instance, block_device_info,
                           network_info):
        LOG.debug("pre_live_migration called", instance=instance)
        self._livemigrutils.check_live_migration_config()

        if CONF.use_cow_images:
            boot_from_volume = self._block_dev_man.is_boot_from_volume(
                block_device_info)
            if not boot_from_volume and instance.image_ref:
                self._imagecache.get_cached_image(context, instance)

        self._volumeops.connect_volumes(block_device_info)

        disk_path_mapping = self._volumeops.get_disk_path_mapping(
            block_device_info)
        if disk_path_mapping:
            # We create a planned VM, ensuring that volumes will remain
            # attached after the VM is migrated.
            self._livemigrutils.create_planned_vm(instance.name,
                                                  instance.host,
                                                  disk_path_mapping)

    def post_live_migration(self, context, instance, block_device_info):
        self._volumeops.disconnect_volumes(block_device_info)
        self._pathutils.get_instance_dir(instance.name,
                                         create_dir=False,
                                         remove_dir=True)

    def post_live_migration_at_destination(self, ctxt, instance_ref,
                                           network_info, block_migration):
        LOG.debug("post_live_migration_at_destination called",
                  instance=instance_ref)
        self._vmops.post_start_vifs(instance_ref, network_info)

    def check_can_live_migrate_destination(self, ctxt, instance_ref,
                                           src_compute_info, dst_compute_info,
                                           block_migration=False,
                                           disk_over_commit=False):
        LOG.debug("check_can_live_migrate_destination called", instance_ref)
        return migrate_data_obj.HyperVLiveMigrateData()

    def check_can_live_migrate_destination_cleanup(self, ctxt,
                                                   dest_check_data):
        LOG.debug("check_can_live_migrate_destination_cleanup called")

    def check_can_live_migrate_source(self, ctxt, instance_ref,
                                      dest_check_data):
        LOG.debug("check_can_live_migrate_source called", instance_ref)
        return dest_check_data
