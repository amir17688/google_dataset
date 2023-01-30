# Copyright (c) 2013 Mirantis Inc.
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

from oslo_config import cfg

import sahara.exceptions as e
import sahara.service.validations.edp.base as b
from sahara.swift import utils as su

CONF = cfg.CONF


def check_job_binary(data, **kwargs):
    job_binary_url = data.get("url", None)
    extra = data.get("extra", {})

    if job_binary_url:
        if job_binary_url.startswith("internal-db"):
            internal_uid = job_binary_url.replace(
                "internal-db://", '')
            b.check_job_binary_internal_exists(internal_uid)

        if job_binary_url.startswith(su.SWIFT_INTERNAL_PREFIX):
            if not kwargs.get('job_binary_id', None):
                # Should not be checked during job binary update
                if (not extra.get("user") or not extra.get("password")) and (
                        not CONF.use_domain_for_proxy_users):
                    raise e.BadJobBinaryException()
