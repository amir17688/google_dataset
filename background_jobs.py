from __future__ import unicode_literals
import redis
from rq import Connection, Queue, Worker
from frappe.utils import cstr
from collections import defaultdict
import frappe
import os, socket

logger = frappe.get_logger(__name__)

default_timeout = 300
queue_timeout = {
	'long': 1500,
	'default': 300,
	'short': 300
}

def enqueue(method, queue='default', timeout=300, event=None,
	async=True, job_name=None, **kwargs):
	'''
		Enqueue method to be executed using a background worker

		:param method: method string or method object
		:param queue: should be either long, default or short
		:param timeout: should be set according to the functions
		:param event: this is passed to enable clearing of jobs from queues
		:param async: if async=False, the method is executed immediately, else via a worker
		:param job_name: can be used to name an enqueue call, which can be used to prevent duplicate calls
		:param kwargs: keyword arguments to be passed to the method
	'''
	q = get_queue(queue)
	if not timeout:
		timeout = queue_timeout.get(queue) or 300

	return q.enqueue_call(execute_job, timeout=timeout,
		kwargs={
			"site": frappe.local.site,
			"method": method,
			"event": event,
			"job_name": job_name or cstr(method),
			"kwargs":kwargs
		})

def execute_job(site, method, event, job_name, kwargs):
	'''Executes job in a worker, performs commit/rollback and logs if there is any error'''
	from frappe.utils.scheduler import log
	frappe.connect(site)

	if isinstance(method, basestring):
		method_name = method
		method = frappe.get_attr(method)
	else:
		method_name = cstr(method)

	try:
		method(**kwargs)
	except:
		frappe.db.rollback()
		log(method_name)
		raise
	else:
		frappe.db.commit()
	finally:
		frappe.destroy()

def start_worker(queue=None):
	'''Wrapper to start rq worker. Connects to redis and monitors these queues.'''
	with frappe.init_site():
		# empty init is required to get redis_queue from common_site_config.json
		redis_connection = get_redis_conn()

	with Connection(redis_connection):
		queues = get_queue_list(queue)
		Worker(queues, name=get_worker_name(queue)).work()

def get_worker_name(queue):
	'''When limiting worker to a specific queue, also append queue name to default worker name'''
	name = None

	if queue:
		# hostname.pid is the default worker name
		name = '{hostname}.{pid}.{queue}'.format(
			hostname=socket.gethostname(),
			pid=os.getpid(),
			queue=queue)

	return name

def get_jobs(site=None, queue=None, key='method'):
	'''Gets jobs per queue or per site or both'''
	jobs_per_site = defaultdict(list)
	for queue in get_queue_list(queue):
		q = get_queue(queue)

		for job in q.jobs:
			if site is None:
				# get jobs for all sites
				jobs_per_site[job.kwargs['site']].append(job.kwargs[key])

			elif job.kwargs['site'] == site:
				# get jobs only for given site
				jobs_per_site[site].append(job.kwargs[key])

	return jobs_per_site

def get_queue_list(queue_list=None):
	'''Defines possible queues. Also wraps a given queue in a list after validating.'''
	default_queue_list = queue_timeout.keys()
	if queue_list:
		if isinstance(queue_list, basestring):
			queue_list = [queue_list]

		for queue in queue_list:
			validate_queue(queue, default_queue_list)

		return queue_list

	else:
		return default_queue_list

def get_queue(queue):
	'''Returns a Queue object tied to a redis connection'''
	validate_queue(queue)

	return Queue(queue, connection=get_redis_conn())

def validate_queue(queue, default_queue_list=None):
	if not default_queue_list:
		default_queue_list = queue_timeout.keys()

	if queue not in default_queue_list:
		frappe.throw("Queue should be one of {0}".format(', '.join(default_queue_list)))

def get_redis_conn():
	if not hasattr(frappe.local, 'conf'):
		raise Exception('You need to call frappe.init')

	elif not frappe.local.conf.redis_queue:
		raise Exception('redis_queue missing in common_site_config.json')

	return redis.from_url(frappe.local.conf.redis_queue)

