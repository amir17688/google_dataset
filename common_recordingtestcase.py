#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
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
#--------------------------------------------------------------------------
from contextlib import contextmanager
import copy
import inspect
import json
import os
import os.path
import time
import vcr
import zlib

from .common_extendedtestcase import ExtendedTestCase


class TestMode(object):
    none = 'None' # this will be for unit test, no need for any recordings
    playback = 'Playback'
    record = 'Record'
    run_live_no_record = 'RunLiveNoRecord'

    @staticmethod
    def is_playback(mode):
        return mode.lower() == TestMode.playback.lower()

    @staticmethod
    def need_recordingfile(mode):
        mode_lower = mode.lower()
        return mode_lower == TestMode.playback.lower() or mode_lower == TestMode.record.lower()

    @staticmethod
    def need_real_credentials(mode):
        mode_lower = mode.lower()
        return mode_lower == TestMode.run_live_no_record.lower() or mode_lower == TestMode.record.lower()


class RecordingTestCase(ExtendedTestCase):

    def __init__(self, *args, **kwargs):
        super(RecordingTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        super(RecordingTestCase, self).setUp()

        self.init_test_mode()

        # example of qualified test name:
        # test_mgmt_network.test_public_ip_addresses
        _, filename = os.path.split(inspect.getsourcefile(type(self)))
        name, _ = os.path.splitext(filename)
        self.qualified_test_name = '{0}.{1}'.format(
            name,
            self._testMethodName,
        )

    def init_test_mode(self):
        try:
            path = os.path.join(self.working_folder, 'testsettings_local.json')
            with open(path) as testsettings_local_file:
                test_settings = json.load(testsettings_local_file)
            self.test_mode = test_settings['mode']
        except:
            pass
        
        if getattr(self, 'test_mode', None) is None:
            self.test_mode = TestMode.playback

    def sleep(self, seconds):
        if not self.is_playback():
            time.sleep(seconds)

    def is_playback(self):
        return TestMode.is_playback(self.test_mode)

    def recording(self):
        if TestMode.need_recordingfile(self.test_mode):
            cassette_name = '{0}.yaml'.format(self.qualified_test_name)

            my_vcr = vcr.VCR(
                before_record_request = self._scrub_sensitive_request_info,
                before_record_response = self._scrub_sensitive_response_info,
                record_mode = 'none' if TestMode.is_playback(self.test_mode) else 'all'
            )

            self.assertIsNotNone(self.working_folder)
            return my_vcr.use_cassette(
                os.path.join(self.working_folder, 'recordings', cassette_name),
                filter_headers=['authorization'],
            )
        else:
            return self._nop_context_manager()

    def get_resource_name(self, name):
        # Append a suffix to the name, based on the fully qualified test name
        # We use a checksum of the test name so that each test gets different
        # resource names, but each test will get the same name on repeat runs,
        # which is needed for playback.
        # Most resource names have a length limit, so we use a crc32
        self.checksum = zlib.adler32(self.qualified_test_name.encode()) & 0xffffffff
        name = '{}{}'.format(name, hex(self.checksum)[2:])
        if name.endswith('L'):
            name = name[:-1]
        return name

    def _scrub_sensitive_request_info(self, request):
        if not TestMode.is_playback(self.test_mode):
            request.uri = self._scrub(request.uri)
            if request.body is not None:
                request.body = self._scrub(request.body)
        return request

    def _scrub_sensitive_response_info(self, response):
        if not TestMode.is_playback(self.test_mode):
            # We need to make a copy because vcr doesn't make one for us.
            # Without this, changing the contents of the dicts would change
            # the contents returned to the caller - not just the contents
            # getting saved to disk. That would be a problem with headers
            # such as 'location', often used in the request uri of a
            # subsequent service call.
            response = copy.deepcopy(response)
            headers = response.get('headers')
            if headers:
                for name, val in headers.items():
                    for i in range(len(val)):
                        val[i] = self._scrub(val[i])
                    if name.lower() == 'retry-after':
                        val[:] = ['0']
            body = response.get('body')
            if body:
                body_str = body.get('string')
                if body_str:
                    response['body']['string'] = self._scrub(body_str)

        return response

    def _scrub(self, val):
        return val

    def _scrub_using_dict(self, val, real_to_fake_dict):
        replacements = list(real_to_fake_dict.keys())

        # if we have 'val1' and 'val10', we want 'val10' to be replaced first
        replacements.sort(reverse=True)

        for real_val in replacements:
            if real_val:
                fake_val = real_to_fake_dict[real_val]
                if real_val != fake_val:
                    if isinstance(val, bytes):
                        val = val.replace(real_val.encode(), fake_val.encode())
                    else:
                        val = val.replace(real_val, fake_val)

        return val

    @contextmanager
    def _nop_context_manager(self):
        yield


def record(test):
    def recording_test(self):
        with self.recording():
            test(self)
    recording_test.__name__ = test.__name__
    return recording_test
