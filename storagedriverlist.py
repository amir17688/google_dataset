# Copyright 2016 iNuron NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
VDiskList module
"""
from ovs.dal.datalist import DataList
from ovs.dal.hybrids.storagedriver import StorageDriver


class StorageDriverList(object):
    """
    This StorageDriverList class contains various lists regarding to the StorageDriver class
    """

    @staticmethod
    def get_storagedrivers():
        """
        Returns a list of all StorageDrivers
        """
        return DataList(StorageDriver, {'type': DataList.where_operator.AND,
                                        'items': []})

    @staticmethod
    def get_by_storagedriver_id(storagedriver_id):
        """
        Returns a list of all StorageDrivers based on a given storagedriver_id
        """
        storagedrivers = DataList(StorageDriver, {'type': DataList.where_operator.AND,
                                                  'items': [('storagedriver_id', DataList.operator.EQUALS, storagedriver_id)]})
        if len(storagedrivers) > 0:
            return storagedrivers[0]
        return None

    @staticmethod
    def get_storagedrivers_by_storagerouter(machineguid):
        """
        Returns a list of all StorageDrivers for Storage Router
        """
        return DataList(StorageDriver, {'type': DataList.where_operator.AND,
                                        'items': [('storagerouter_guid', DataList.operator.EQUALS, machineguid)]})
