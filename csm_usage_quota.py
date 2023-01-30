# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class CsmUsageQuota(Model):
    """
    Usage of the quota resource

    :param unit: Units of measurement for the quota resourse
    :type unit: str
    :param next_reset_time: Next reset time for the resource counter
    :type next_reset_time: datetime
    :param current_value: The current value of the resource counter
    :type current_value: long
    :param limit: The resource limit
    :type limit: long
    :param name: Quota name
    :type name: :class:`LocalizableString
     <azure.mgmt.web.models.LocalizableString>`
    """ 

    _attribute_map = {
        'unit': {'key': 'unit', 'type': 'str'},
        'next_reset_time': {'key': 'nextResetTime', 'type': 'iso-8601'},
        'current_value': {'key': 'currentValue', 'type': 'long'},
        'limit': {'key': 'limit', 'type': 'long'},
        'name': {'key': 'name', 'type': 'LocalizableString'},
    }

    def __init__(self, unit=None, next_reset_time=None, current_value=None, limit=None, name=None):
        self.unit = unit
        self.next_reset_time = next_reset_time
        self.current_value = current_value
        self.limit = limit
        self.name = name
