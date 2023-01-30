from __future__ import absolute_import
from __future__ import unicode_literals

import datetime

import docker
from docker.errors import NotFound

from .. import mock
from .. import unittest
from compose.config.config import Config
from compose.config.types import VolumeFromSpec
from compose.const import LABEL_SERVICE
from compose.container import Container
from compose.project import Project
from compose.service import ImageType
from compose.service import Service


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.mock_client = mock.create_autospec(docker.Client)

    def test_from_config(self):
        config = Config(
            version=None,
            services=[
                {
                    'name': 'web',
                    'image': 'busybox:latest',
                },
                {
                    'name': 'db',
                    'image': 'busybox:latest',
                },
            ],
            networks=None,
            volumes=None,
        )
        project = Project.from_config(
            name='composetest',
            config_data=config,
            client=None,
        )
        self.assertEqual(len(project.services), 2)
        self.assertEqual(project.get_service('web').name, 'web')
        self.assertEqual(project.get_service('web').options['image'], 'busybox:latest')
        self.assertEqual(project.get_service('db').name, 'db')
        self.assertEqual(project.get_service('db').options['image'], 'busybox:latest')
        self.assertFalse(project.networks.use_networking)

    def test_from_config_v2(self):
        config = Config(
            version=2,
            services=[
                {
                    'name': 'web',
                    'image': 'busybox:latest',
                },
                {
                    'name': 'db',
                    'image': 'busybox:latest',
                },
            ],
            networks=None,
            volumes=None,
        )
        project = Project.from_config('composetest', config, None)
        self.assertEqual(len(project.services), 2)
        self.assertTrue(project.networks.use_networking)

    def test_get_service(self):
        web = Service(
            project='composetest',
            name='web',
            client=None,
            image="busybox:latest",
        )
        project = Project('test', [web], None)
        self.assertEqual(project.get_service('web'), web)

    def test_get_services_returns_all_services_without_args(self):
        web = Service(
            project='composetest',
            name='web',
            image='foo',
        )
        console = Service(
            project='composetest',
            name='console',
            image='foo',
        )
        project = Project('test', [web, console], None)
        self.assertEqual(project.get_services(), [web, console])

    def test_get_services_returns_listed_services_with_args(self):
        web = Service(
            project='composetest',
            name='web',
            image='foo',
        )
        console = Service(
            project='composetest',
            name='console',
            image='foo',
        )
        project = Project('test', [web, console], None)
        self.assertEqual(project.get_services(['console']), [console])

    def test_get_services_with_include_links(self):
        db = Service(
            project='composetest',
            name='db',
            image='foo',
        )
        web = Service(
            project='composetest',
            name='web',
            image='foo',
            links=[(db, 'database')]
        )
        cache = Service(
            project='composetest',
            name='cache',
            image='foo'
        )
        console = Service(
            project='composetest',
            name='console',
            image='foo',
            links=[(web, 'web')]
        )
        project = Project('test', [web, db, cache, console], None)
        self.assertEqual(
            project.get_services(['console'], include_deps=True),
            [db, web, console]
        )

    def test_get_services_removes_duplicates_following_links(self):
        db = Service(
            project='composetest',
            name='db',
            image='foo',
        )
        web = Service(
            project='composetest',
            name='web',
            image='foo',
            links=[(db, 'database')]
        )
        project = Project('test', [web, db], None)
        self.assertEqual(
            project.get_services(['web', 'db'], include_deps=True),
            [db, web]
        )

    def test_use_volumes_from_container(self):
        container_id = 'aabbccddee'
        container_dict = dict(Name='aaa', Id=container_id)
        self.mock_client.inspect_container.return_value = container_dict
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=None,
                services=[{
                    'name': 'test',
                    'image': 'busybox:latest',
                    'volumes_from': [VolumeFromSpec('aaa', 'rw', 'container')]
                }],
                networks=None,
                volumes=None,
            ),
        )
        assert project.get_service('test')._get_volumes_from() == [container_id + ":rw"]

    def test_use_volumes_from_service_no_container(self):
        container_name = 'test_vol_1'
        self.mock_client.containers.return_value = [
            {
                "Name": container_name,
                "Names": [container_name],
                "Id": container_name,
                "Image": 'busybox:latest'
            }
        ]
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=None,
                services=[
                    {
                        'name': 'vol',
                        'image': 'busybox:latest'
                    },
                    {
                        'name': 'test',
                        'image': 'busybox:latest',
                        'volumes_from': [VolumeFromSpec('vol', 'rw', 'service')]
                    }
                ],
                networks=None,
                volumes=None,
            ),
        )
        assert project.get_service('test')._get_volumes_from() == [container_name + ":rw"]

    def test_use_volumes_from_service_container(self):
        container_ids = ['aabbccddee', '12345']

        project = Project.from_config(
            name='test',
            client=None,
            config_data=Config(
                version=None,
                services=[
                    {
                        'name': 'vol',
                        'image': 'busybox:latest'
                    },
                    {
                        'name': 'test',
                        'image': 'busybox:latest',
                        'volumes_from': [VolumeFromSpec('vol', 'rw', 'service')]
                    }
                ],
                networks=None,
                volumes=None,
            ),
        )
        with mock.patch.object(Service, 'containers') as mock_return:
            mock_return.return_value = [
                mock.Mock(id=container_id, spec=Container)
                for container_id in container_ids]
            assert (
                project.get_service('test')._get_volumes_from() ==
                [container_ids[0] + ':rw']
            )

    def test_events(self):
        services = [Service(name='web'), Service(name='db')]
        project = Project('test', services, self.mock_client)
        self.mock_client.events.return_value = iter([
            {
                'status': 'create',
                'from': 'example/image',
                'id': 'abcde',
                'time': 1420092061,
                'timeNano': 14200920610000002000,
            },
            {
                'status': 'attach',
                'from': 'example/image',
                'id': 'abcde',
                'time': 1420092061,
                'timeNano': 14200920610000003000,
            },
            {
                'status': 'create',
                'from': 'example/other',
                'id': 'bdbdbd',
                'time': 1420092061,
                'timeNano': 14200920610000005000,
            },
            {
                'status': 'create',
                'from': 'example/db',
                'id': 'ababa',
                'time': 1420092061,
                'timeNano': 14200920610000004000,
            },
            {
                'status': 'destroy',
                'from': 'example/db',
                'id': 'eeeee',
                'time': 1420092061,
                'timeNano': 14200920610000004000,
            },
        ])

        def dt_with_microseconds(dt, us):
            return datetime.datetime.fromtimestamp(dt).replace(microsecond=us)

        def get_container(cid):
            if cid == 'eeeee':
                raise NotFound(None, None, "oops")
            if cid == 'abcde':
                name = 'web'
                labels = {LABEL_SERVICE: name}
            elif cid == 'ababa':
                name = 'db'
                labels = {LABEL_SERVICE: name}
            else:
                labels = {}
                name = ''
            return {
                'Id': cid,
                'Config': {'Labels': labels},
                'Name': '/project_%s_1' % name,
            }

        self.mock_client.inspect_container.side_effect = get_container

        events = project.events()

        events_list = list(events)
        # Assert the return value is a generator
        assert not list(events)
        assert events_list == [
            {
                'type': 'container',
                'service': 'web',
                'action': 'create',
                'id': 'abcde',
                'attributes': {
                    'name': 'project_web_1',
                    'image': 'example/image',
                },
                'time': dt_with_microseconds(1420092061, 2),
                'container': Container(None, {'Id': 'abcde'}),
            },
            {
                'type': 'container',
                'service': 'web',
                'action': 'attach',
                'id': 'abcde',
                'attributes': {
                    'name': 'project_web_1',
                    'image': 'example/image',
                },
                'time': dt_with_microseconds(1420092061, 3),
                'container': Container(None, {'Id': 'abcde'}),
            },
            {
                'type': 'container',
                'service': 'db',
                'action': 'create',
                'id': 'ababa',
                'attributes': {
                    'name': 'project_db_1',
                    'image': 'example/db',
                },
                'time': dt_with_microseconds(1420092061, 4),
                'container': Container(None, {'Id': 'ababa'}),
            },
        ]

    def test_net_unset(self):
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=None,
                services=[
                    {
                        'name': 'test',
                        'image': 'busybox:latest',
                    }
                ],
                networks=None,
                volumes=None,
            ),
        )
        service = project.get_service('test')
        self.assertEqual(service.network_mode.id, None)
        self.assertNotIn('NetworkMode', service._get_container_host_config({}))

    def test_use_net_from_container(self):
        container_id = 'aabbccddee'
        container_dict = dict(Name='aaa', Id=container_id)
        self.mock_client.inspect_container.return_value = container_dict
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=None,
                services=[
                    {
                        'name': 'test',
                        'image': 'busybox:latest',
                        'network_mode': 'container:aaa'
                    },
                ],
                networks=None,
                volumes=None,
            ),
        )
        service = project.get_service('test')
        self.assertEqual(service.network_mode.mode, 'container:' + container_id)

    def test_use_net_from_service(self):
        container_name = 'test_aaa_1'
        self.mock_client.containers.return_value = [
            {
                "Name": container_name,
                "Names": [container_name],
                "Id": container_name,
                "Image": 'busybox:latest'
            }
        ]
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=None,
                services=[
                    {
                        'name': 'aaa',
                        'image': 'busybox:latest'
                    },
                    {
                        'name': 'test',
                        'image': 'busybox:latest',
                        'network_mode': 'service:aaa'
                    },
                ],
                networks=None,
                volumes=None,
            ),
        )

        service = project.get_service('test')
        self.assertEqual(service.network_mode.mode, 'container:' + container_name)

    def test_uses_default_network_true(self):
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=2,
                services=[
                    {
                        'name': 'foo',
                        'image': 'busybox:latest'
                    },
                ],
                networks=None,
                volumes=None,
            ),
        )

        assert 'default' in project.networks.networks

    def test_uses_default_network_false(self):
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=2,
                services=[
                    {
                        'name': 'foo',
                        'image': 'busybox:latest',
                        'networks': {'custom': None}
                    },
                ],
                networks={'custom': {}},
                volumes=None,
            ),
        )

        assert 'default' not in project.networks.networks

    def test_container_without_name(self):
        self.mock_client.containers.return_value = [
            {'Image': 'busybox:latest', 'Id': '1', 'Name': '1'},
            {'Image': 'busybox:latest', 'Id': '2', 'Name': None},
            {'Image': 'busybox:latest', 'Id': '3'},
        ]
        self.mock_client.inspect_container.return_value = {
            'Id': '1',
            'Config': {
                'Labels': {
                    LABEL_SERVICE: 'web',
                },
            },
        }
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version=None,
                services=[{
                    'name': 'web',
                    'image': 'busybox:latest',
                }],
                networks=None,
                volumes=None,
            ),
        )
        self.assertEqual([c.id for c in project.containers()], ['1'])

    def test_down_with_no_resources(self):
        project = Project.from_config(
            name='test',
            client=self.mock_client,
            config_data=Config(
                version='2',
                services=[{
                    'name': 'web',
                    'image': 'busybox:latest',
                }],
                networks={'default': {}},
                volumes={'data': {}},
            ),
        )
        self.mock_client.remove_network.side_effect = NotFound(None, None, 'oops')
        self.mock_client.remove_volume.side_effect = NotFound(None, None, 'oops')

        project.down(ImageType.all, True)
        self.mock_client.remove_image.assert_called_once_with("busybox:latest")
], self.client)
        project.start()
        self.assertEqual(len(project.containers()), 0)

        project.up(['web'])
        self.assertEqual(len(project.containers()), 2)
        self.assertEqual(len(web.containers()), 1)
        self.assertEqual(len(db.containers()), 1)
        self.assertEqual(len(console.containers()), 0)

    def test_project_up_starts_depends(self):
        project = Project.from_config(
            name='composetest',
            config_data=build_config({
                'console': {
                    'image': 'busybox:latest',
                    'command': ["top"],
                },
                'data': {
                    'image': 'busybox:latest',
                    'command': ["top"]
                },
                'db': {
                    'image': 'busybox:latest',
                    'command': ["top"],
                    'volumes_from': ['data'],
                },
                'web': {
                    'image': 'busybox:latest',
                    'command': ["top"],
                    'links': ['db'],
                },
            }),
            client=self.client,
        )
        project.start()
        self.assertEqual(len(project.containers()), 0)

        project.up(['web'])
        self.assertEqual(len(project.containers()), 3)
        self.assertEqual(len(project.get_service('web').containers()), 1)
        self.assertEqual(len(project.get_service('db').containers()), 1)
        self.assertEqual(len(project.get_service('data').containers()), 1)
        self.assertEqual(len(project.get_service('console').containers()), 0)

    def test_project_up_with_no_deps(self):
        project = Project.from_config(
            name='composetest',
            config_data=build_config({
                'console': {
                    'image': 'busybox:latest',
                    'command': ["top"],
                },
                'data': {
                    'image': 'busybox:latest',
                    'command': ["top"]
                },
                'db': {
                    'image': 'busybox:latest',
                    'command': ["top"],
                    'volumes_from': ['data'],
                },
                'web': {
                    'image': 'busybox:latest',
                    'command': ["top"],
                    'links': ['db'],
                },
            }),
            client=self.client,
        )
        project.start()
        self.assertEqual(len(project.containers()), 0)

        project.up(['db'], start_deps=False)
        self.assertEqual(len(project.containers(stopped=True)), 2)
        self.assertEqual(len(project.get_service('web').containers()), 0)
        self.assertEqual(len(project.get_service('db').containers()), 1)
        self.assertEqual(len(project.get_service('data').containers()), 0)
        self.assertEqual(len(project.get_service('data').containers(stopped=True)), 1)
        self.assertEqual(len(project.get_service('console').containers()), 0)

    def test_unscale_after_restart(self):
        web = self.create_service('web')
        project = Project('composetest', [web], self.client)

        project.start()

        service = project.get_service('web')
        service.scale(1)
        self.assertEqual(len(service.containers()), 1)
        service.scale(3)
        self.assertEqual(len(service.containers()), 3)
        project.up()
        service = project.get_service('web')
        self.assertEqual(len(service.containers()), 3)
        service.scale(1)
        self.assertEqual(len(service.containers()), 1)
        project.up()
        service = project.get_service('web')
        self.assertEqual(len(service.containers()), 1)
        # does scale=0 ,makes any sense? after recreating at least 1 container is running
        service.scale(0)
        project.up()
        service = project.get_service('web')
        self.assertEqual(len(service.containers()), 1)

    @v2_only()
    def test_project_up_networks(self):
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top',
                'networks': {
                    'foo': None,
                    'bar': None,
                    'baz': {'aliases': ['extra']},
                },
            }],
            volumes={},
            networks={
                'foo': {'driver': 'bridge'},
                'bar': {'driver': None},
                'baz': {},
            },
        )

        project = Project.from_config(
            client=self.client,
            name='composetest',
            config_data=config_data,
        )
        project.up()

        containers = project.containers()
        assert len(containers) == 1
        container, = containers

        for net_name in ['foo', 'bar', 'baz']:
            full_net_name = 'composetest_{}'.format(net_name)
            network_data = self.client.inspect_network(full_net_name)
            assert network_data['Name'] == full_net_name

        aliases_key = 'NetworkSettings.Networks.{net}.Aliases'
        assert 'web' in container.get(aliases_key.format(net='composetest_foo'))
        assert 'web' in container.get(aliases_key.format(net='composetest_baz'))
        assert 'extra' in container.get(aliases_key.format(net='composetest_baz'))

        foo_data = self.client.inspect_network('composetest_foo')
        assert foo_data['Driver'] == 'bridge'

    @v2_only()
    def test_up_with_ipam_config(self):
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'networks': {'front': None},
            }],
            volumes={},
            networks={
                'front': {
                    'driver': 'bridge',
                    'driver_opts': {
                        "com.docker.network.bridge.enable_icc": "false",
                    },
                    'ipam': {
                        'driver': 'default',
                        'config': [{
                            "subnet": "172.28.0.0/16",
                            "ip_range": "172.28.5.0/24",
                            "gateway": "172.28.5.254",
                            "aux_addresses": {
                                "a": "172.28.1.5",
                                "b": "172.28.1.6",
                                "c": "172.28.1.7",
                            },
                        }],
                    },
                },
            },
        )

        project = Project.from_config(
            client=self.client,
            name='composetest',
            config_data=config_data,
        )
        project.up()

        network = self.client.networks(names=['composetest_front'])[0]

        assert network['Options'] == {
            "com.docker.network.bridge.enable_icc": "false"
        }

        assert network['IPAM'] == {
            'Driver': 'default',
            'Options': None,
            'Config': [{
                'Subnet': "172.28.0.0/16",
                'IPRange': "172.28.5.0/24",
                'Gateway': "172.28.5.254",
                'AuxiliaryAddresses': {
                    'a': '172.28.1.5',
                    'b': '172.28.1.6',
                    'c': '172.28.1.7',
                },
            }],
        }

    @v2_only()
    def test_up_with_network_static_addresses(self):
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top',
                'networks': {
                    'static_test': {
                        'ipv4_address': '172.16.100.100',
                        'ipv6_address': 'fe80::1001:102'
                    }
                },
            }],
            volumes={},
            networks={
                'static_test': {
                    'driver': 'bridge',
                    'driver_opts': {
                        "com.docker.network.enable_ipv6": "true",
                    },
                    'ipam': {
                        'driver': 'default',
                        'config': [
                            {"subnet": "172.16.100.0/24",
                             "gateway": "172.16.100.1"},
                            {"subnet": "fe80::/64",
                             "gateway": "fe80::1001:1"}
                        ]
                    }
                }
            }
        )
        project = Project.from_config(
            client=self.client,
            name='composetest',
            config_data=config_data,
        )
        project.up(detached=True)

        network = self.client.networks(names=['static_test'])[0]
        service_container = project.get_service('web').containers()[0]

        assert network['Options'] == {
            "com.docker.network.enable_ipv6": "true"
        }

        IPAMConfig = (service_container.inspect().get('NetworkSettings', {}).
                      get('Networks', {}).get('composetest_static_test', {}).
                      get('IPAMConfig', {}))
        assert IPAMConfig.get('IPv4Address') == '172.16.100.100'
        assert IPAMConfig.get('IPv6Address') == 'fe80::1001:102'

    @v2_only()
    def test_up_with_network_static_addresses_missing_subnet(self):
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'networks': {
                    'static_test': {
                        'ipv4_address': '172.16.100.100',
                        'ipv6_address': 'fe80::1001:101'
                    }
                },
            }],
            volumes={},
            networks={
                'static_test': {
                    'driver': 'bridge',
                    'driver_opts': {
                        "com.docker.network.enable_ipv6": "true",
                    },
                    'ipam': {
                        'driver': 'default',
                    },
                },
            },
        )

        project = Project.from_config(
            client=self.client,
            name='composetest',
            config_data=config_data,
        )

        assert len(project.up()) == 0

    @v2_only()
    def test_project_up_volumes(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={vol_name: {'driver': 'local'}},
            networks={},
        )

        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        project.up()
        self.assertEqual(len(project.containers()), 1)

        volume_data = self.client.inspect_volume(full_vol_name)
        self.assertEqual(volume_data['Name'], full_vol_name)
        self.assertEqual(volume_data['Driver'], 'local')

    @v2_only()
    def test_project_up_logging_with_multiple_files(self):
        base_file = config.ConfigFile(
            'base.yml',
            {
                'version': V2_0,
                'services': {
                    'simple': {'image': 'busybox:latest', 'command': 'top'},
                    'another': {
                        'image': 'busybox:latest',
                        'command': 'top',
                        'logging': {
                            'driver': "json-file",
                            'options': {
                                'max-size': "10m"
                            }
                        }
                    }
                }

            })
        override_file = config.ConfigFile(
            'override.yml',
            {
                'version': V2_0,
                'services': {
                    'another': {
                        'logging': {
                            'driver': "none"
                        }
                    }
                }

            })
        details = config.ConfigDetails('.', [base_file, override_file])

        tmpdir = py.test.ensuretemp('logging_test')
        self.addCleanup(tmpdir.remove)
        with tmpdir.as_cwd():
            config_data = config.load(details)
        project = Project.from_config(
            name='composetest', config_data=config_data, client=self.client
        )
        project.up()
        containers = project.containers()
        self.assertEqual(len(containers), 2)

        another = project.get_service('another').containers()[0]
        log_config = another.get('HostConfig.LogConfig')
        self.assertTrue(log_config)
        self.assertEqual(log_config.get('Type'), 'none')

    @v2_only()
    def test_initialize_volumes(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={vol_name: {}},
            networks={},
        )

        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        project.volumes.initialize()

        volume_data = self.client.inspect_volume(full_vol_name)
        self.assertEqual(volume_data['Name'], full_vol_name)
        self.assertEqual(volume_data['Driver'], 'local')

    @v2_only()
    def test_project_up_implicit_volume_driver(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={vol_name: {}},
            networks={},
        )

        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        project.up()

        volume_data = self.client.inspect_volume(full_vol_name)
        self.assertEqual(volume_data['Name'], full_vol_name)
        self.assertEqual(volume_data['Driver'], 'local')

    @v2_only()
    def test_initialize_volumes_invalid_volume_driver(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))

        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={vol_name: {'driver': 'foobar'}},
            networks={},
        )

        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        with self.assertRaises(config.ConfigurationError):
            project.volumes.initialize()

    @v2_only()
    def test_initialize_volumes_updated_driver(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)

        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={vol_name: {'driver': 'local'}},
            networks={},
        )
        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        project.volumes.initialize()

        volume_data = self.client.inspect_volume(full_vol_name)
        self.assertEqual(volume_data['Name'], full_vol_name)
        self.assertEqual(volume_data['Driver'], 'local')

        config_data = config_data._replace(
            volumes={vol_name: {'driver': 'smb'}}
        )
        project = Project.from_config(
            name='composetest',
            config_data=config_data,
            client=self.client
        )
        with self.assertRaises(config.ConfigurationError) as e:
            project.volumes.initialize()
        assert 'Configuration for volume {0} specifies driver smb'.format(
            vol_name
        ) in str(e.exception)

    @v2_only()
    def test_initialize_volumes_updated_blank_driver(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)

        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={vol_name: {'driver': 'local'}},
            networks={},
        )
        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        project.volumes.initialize()

        volume_data = self.client.inspect_volume(full_vol_name)
        self.assertEqual(volume_data['Name'], full_vol_name)
        self.assertEqual(volume_data['Driver'], 'local')

        config_data = config_data._replace(
            volumes={vol_name: {}}
        )
        project = Project.from_config(
            name='composetest',
            config_data=config_data,
            client=self.client
        )
        project.volumes.initialize()
        volume_data = self.client.inspect_volume(full_vol_name)
        self.assertEqual(volume_data['Name'], full_vol_name)
        self.assertEqual(volume_data['Driver'], 'local')

    @v2_only()
    def test_initialize_volumes_external_volumes(self):
        # Use composetest_ prefix so it gets garbage-collected in tearDown()
        vol_name = 'composetest_{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)
        self.client.create_volume(vol_name)
        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={
                vol_name: {'external': True, 'external_name': vol_name}
            },
            networks=None,
        )
        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        project.volumes.initialize()

        with self.assertRaises(NotFound):
            self.client.inspect_volume(full_vol_name)

    @v2_only()
    def test_initialize_volumes_inexistent_external_volume(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))

        config_data = config.Config(
            version=V2_0,
            services=[{
                'name': 'web',
                'image': 'busybox:latest',
                'command': 'top'
            }],
            volumes={
                vol_name: {'external': True, 'external_name': vol_name}
            },
            networks=None,
        )
        project = Project.from_config(
            name='composetest',
            config_data=config_data, client=self.client
        )
        with self.assertRaises(config.ConfigurationError) as e:
            project.volumes.initialize()
        assert 'Volume {0} declared as external'.format(
            vol_name
        ) in str(e.exception)

    @v2_only()
    def test_project_up_named_volumes_in_binds(self):
        vol_name = '{0:x}'.format(random.getrandbits(32))
        full_vol_name = 'composetest_{0}'.format(vol_name)

        base_file = config.ConfigFile(
            'base.yml',
            {
                'version': V2_0,
                'services': {
                    'simple': {
                        'image': 'busybox:latest',
                        'command': 'top',
                        'volumes': ['{0}:/data'.format(vol_name)]
                    },
                },
                'volumes': {
                    vol_name: {'driver': 'local'}
                }

            })
        config_details = config.ConfigDetails('.', [base_file])
        config_data = config.load(config_details)
        project = Project.from_config(
            name='composetest', config_data=config_data, client=self.client
        )
        service = project.services[0]
        self.assertEqual(service.name, 'simple')
        volumes = service.options.get('volumes')
        self.assertEqual(len(volumes), 1)
        self.assertEqual(volumes[0].external, full_vol_name)
        project.up()
        engine_volumes = self.client.volumes()['Volumes']
        container = service.get_container()
        assert [mount['Name'] for mount in container.get('Mounts')] == [full_vol_name]
        assert next((v for v in engine_volumes if v['Name'] == vol_name), None) is None

    def test_project_up_orphans(self):
        config_dict = {
            'service1': {
                'image': 'busybox:latest',
                'command': 'top',
            }
        }

        config_data = build_config(config_dict)
        project = Project.from_config(
            name='composetest', config_data=config_data, client=self.client
        )
        project.up()
        config_dict['service2'] = config_dict['service1']
        del config_dict['service1']

        config_data = build_config(config_dict)
        project = Project.from_config(
            name='composetest', config_data=config_data, client=self.client
        )
        with mock.patch('compose.project.log') as mock_log:
            project.up()

        mock_log.warning.assert_called_once_with(mock.ANY)

        assert len([
            ctnr for ctnr in project._labeled_containers()
            if ctnr.labels.get(LABEL_SERVICE) == 'service1'
        ]) == 1

        project.up(remove_orphans=True)

        assert len([
            ctnr for ctnr in project._labeled_containers()
            if ctnr.labels.get(LABEL_SERVICE) == 'service1'
        ]) == 0
