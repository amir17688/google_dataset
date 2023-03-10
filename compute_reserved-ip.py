# Copyright (c) 2016 SUSE.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
In order to maintain access to a specific public IP address, a reservation can
be made. Reservations are identified by a user-defined name.

usage: azurectl compute reserved-ip -h | --help
       azurectl compute reserved-ip create --name=<reserved-ip-name>
       azurectl compute reserved-ip list
       azurectl compute reserved-ip show --name=<reserved-ip-name>
       azurectl compute reserved-ip delete --name=<reserved-ip-name>
       azurectl compute reserved-ip help

commands:
    create
        add a new IP address reservation in the default or specified region
        (use the global --region argument)
    delete
        release a reserved IP address
    list
        list IP addresses reserved within this account
    show
        list information about a single IP address reservation

options:
    --name=<reserved-ip-name>
        name of the reserved IP address
"""
# project
from base import CliTask
from ..account.service import AzureAccount
from ..utils.collector import DataCollector
from ..utils.output import DataOutput
from ..instance.reserved_ip import ReservedIp
from ..help import Help


class ComputeReservedIpTask(CliTask):
    """
        Process image commands
    """
    def process(self):
        self.manual = Help()
        if self.__help():
            return

        self.result = DataCollector()
        self.out = DataOutput(
            self.result,
            self.global_args['--output-format'],
            self.global_args['--output-style']
        )

        self.load_config()

        self.account = AzureAccount(self.config)
        self.reserved_ip = ReservedIp(self.account)

        if self.command_args['list']:
            self.__list()
        if self.command_args['show']:
            self.__show()
        if self.command_args['create']:
            self.__create()
        if self.command_args['delete']:
            self.__delete()

    def __help(self):
        if self.command_args['help']:
            self.manual.show('azurectl::compute::reserved_ip')
        else:
            return False
        return self.manual

    def __list(self):
        self.result.add('reserved_ips', self.reserved_ip.list())
        self.out.display()

    def __show(self):
        self.result.add(
            'reserved_ip',
            self.reserved_ip.show(self.command_args['--name'])
        )
        self.out.display()

    def __create(self):
        self.result.add(
            'reserved_ip:' + self.command_args['--name'],
            self.reserved_ip.create(
                self.command_args['--name'],
                self.config.get_region_name()
            )
        )
        self.out.display()

    def __delete(self):
        self.result.add(
            'reserved_ip:' + self.command_args['--name'],
            self.reserved_ip.delete(
                self.command_args['--name'],
            )
        )
        self.out.display()
