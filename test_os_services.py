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

from novaclient.tests.functional.v2.legacy import test_os_services


class TestOsServicesNovaClientV211(test_os_services.TestOsServicesNovaClient):
    """Functional tests for os-services attributes, microversion 2.11"""

    COMPUTE_API_VERSION = "2.11"

    def test_os_services_force_down_force_up(self):
        for serv in self.client.services.list():
            host = self._get_column_value_from_single_row_table(
                self.nova('service-list --binary %s' % serv.binary), 'Host')
            service = self.nova('service-force-down %s %s'
                                % (host, serv.binary))
            self.addCleanup(self.nova, 'service-force-down --unset',
                            params="%s %s" % (host, serv.binary))
            status = self._get_column_value_from_single_row_table(
                service, 'Forced down')
            self.assertEqual('True', status)
            service = self.nova('service-force-down --unset %s %s'
                                % (host, serv.binary))
            status = self._get_column_value_from_single_row_table(
                service, 'Forced down')
            self.assertEqual('False', status)
s="%s %s" % (host, serv.binary))
            status = self._get_column_value_from_single_row_table(
                service, 'Status')
            self.assertEqual('disabled', status)
            service = self.nova('service-enable %s %s' % (host, serv.binary))
            status = self._get_column_value_from_single_row_table(
                service, 'Status')
            self.assertEqual('enabled', status)

    def test_os_service_disable_log_reason(self):
        for serv in self.client.services.list():
            host = self._get_column_value_from_single_row_table(
                self.nova('service-list --binary %s' % serv.binary), 'Host')
            service = self.nova('service-disable --reason test_disable %s %s'
                                % (host, serv.binary))
            self.addCleanup(self.nova, 'service-enable',
                            params="%s %s" % (host, serv.binary))
            status = self._get_column_value_from_single_row_table(
                service, 'Status')
            log_reason = self._get_column_value_from_single_row_table(
                service, 'Disabled Reason')
            self.assertEqual('disabled', status)
            self.assertEqual('test_disable', log_reason)
