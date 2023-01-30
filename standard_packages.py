from fabric.api import *

REQUIRED_SYSTEM_PACKAGES = [
    'gcc',
    'python-dev',
    'python-pip',
    'libjpeg-dev',
    'libfreetype6-dev',
    'git',
    'nginx',
    'python-virtualenv',
    'libxml2-dev',
    'libmysqlclient-dev',
    'supervisor',
    'redis-server',
    'libxml2-dev',
    'libxslt-dev',
]


def package_list():
    return ' '.join(REQUIRED_SYSTEM_PACKAGES)