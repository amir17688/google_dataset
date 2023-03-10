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
Celery entry point module
"""
from __future__ import absolute_import

import sys
sys.path.append('/opt/OpenvStorage')

import os
from kombu import Queue
from celery import Celery
from celery.signals import task_postrun, worker_process_init
from ovs.lib.messaging import MessageController
from ovs.log.logHandler import LogHandler
from ovs.extensions.storage.persistentfactory import PersistentFactory
from ovs.extensions.storage.volatilefactory import VolatileFactory
from ovs.extensions.generic.system import System
from ovs.extensions.db.etcd.configuration import EtcdConfiguration

memcache_servers = EtcdConfiguration.get('/ovs/framework/memcache|endpoints')
rmq_servers = EtcdConfiguration.get('/ovs/framework/messagequeue|endpoints')

unique_id = System.get_my_machine_id()

include = []
path = '/'.join([os.path.dirname(__file__), 'lib'])
for filename in os.listdir(path):
    if os.path.isfile('/'.join([path, filename])) and filename.endswith('.py') and filename != '__init__.py':
        name = filename.replace('.py', '')
        include.append('ovs.lib.{0}'.format(name))

celery = Celery('ovs', include=include)

# http://docs.celeryproject.org/en/latest/configuration.html#cache-backend-settings
celery.conf.CELERY_RESULT_BACKEND = "cache+memcached://{0}/".format(';'.join(memcache_servers))
celery.conf.BROKER_URL = ';'.join(['{0}://{1}:{2}@{3}//'.format(EtcdConfiguration.get('/ovs/framework/messagequeue|protocol'),
                                                                EtcdConfiguration.get('/ovs/framework/messagequeue|user'),
                                                                EtcdConfiguration.get('/ovs/framework/messagequeue|password'),
                                                                server)
                                   for server in rmq_servers])
celery.conf.BROKER_CONNECTION_MAX_RETRIES = 5
celery.conf.BROKER_HEARTBEAT = 10
celery.conf.BROKER_HEARTBEAT_CHECKRATE = 2
celery.conf.CELERY_DEFAULT_QUEUE = 'ovs_generic'
celery.conf.CELERY_QUEUES = tuple([Queue('ovs_generic', routing_key='generic.#'),
                                   Queue('ovs_masters', routing_key='masters.#'),
                                   Queue('ovs_{0}'.format(unique_id), routing_key='sr.{0}.#'.format(unique_id))])
celery.conf.CELERY_DEFAULT_EXCHANGE = 'generic'
celery.conf.CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
celery.conf.CELERY_DEFAULT_ROUTING_KEY = 'generic.default'
celery.conf.CELERYD_PREFETCH_MULTIPLIER = 1  # This makes sure that the workers won't be pre-fetching tasks, this to prevent deadlocks
celery.conf.CELERYBEAT_SCHEDULE = {}

loghandler = LogHandler.get('celery', name='celery')


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """
    Hook for celery postrun event
    """
    _ = sender, task, args, kwargs, kwds
    try:
        MessageController.fire(MessageController.Type.TASK_COMPLETE, task_id)
    except Exception as ex:
        loghandler.error('Caught error during postrun handler: {0}'.format(ex))


@worker_process_init.connect
def worker_process_init_handler(args=None, kwargs=None, **kwds):
    """
    Hook for process init
    """
    _ = args, kwargs, kwds
    VolatileFactory.store = None
    PersistentFactory.store = None


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2 and sys.argv[1] == 'clear_cache':
        from ovs.lib.helpers.decorators import ENSURE_SINGLE_KEY

        cache = PersistentFactory.get_client()
        for key in cache.prefix(ENSURE_SINGLE_KEY):
            cache.delete(key)
