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
DataObject module
"""
import uuid
import copy
import time
import json
import inspect
from random import randint
from ovs.dal.exceptions import (ObjectNotFoundException, ConcurrencyException, LinkedObjectException,
                                MissingMandatoryFieldsException, RaceConditionException, InvalidRelationException,
                                VolatileObjectException)
from ovs.dal.helpers import Descriptor, Toolbox, HybridRunner
from ovs.dal.relations import RelationMapper
from ovs.dal.datalist import DataList
from ovs.extensions.generic.volatilemutex import VolatileMutex
from ovs.extensions.storage.exceptions import KeyNotFoundException, AssertException
from ovs.extensions.storage.persistentfactory import PersistentFactory
from ovs.extensions.storage.volatilefactory import VolatileFactory
from ovs.log.logHandler import LogHandler

logger = LogHandler.get('dal', name='dataobject')


class MetaClass(type):
    """
    This metaclass provides dynamic __doc__ generation feeding doc generators
    """

    def __new__(mcs, name, bases, dct):
        """
        Overrides instance creation of all DataObject instances
        """
        if name != 'DataObject':
            for internal in ['_properties', '_relations', '_dynamics']:
                data = set()
                for base in bases:
                    if hasattr(base, internal):
                        data.update(getattr(base, internal))
                if '_{0}_{1}'.format(name, internal) in dct:
                    data.update(dct.pop('_{0}_{1}'.format(name, internal)))
                dct[internal] = list(data)

            for prop in dct['_properties']:
                docstring = prop.docstring
                if isinstance(prop.property_type, type):
                    itemtype = prop.property_type.__name__
                    extra_info = ''
                else:
                    itemtype = 'Enum({0})'.format(prop.property_type[0].__class__.__name__)
                    extra_info = '(enum values: {0})'.format(', '.join(prop.property_type))
                dct[prop.name] = property(
                    doc='[persistent] {0} {1}\n@type: {2}'.format(docstring, extra_info, itemtype)
                )
            for relation in dct['_relations']:
                itemtype = relation.foreign_type.__name__ if relation.foreign_type is not None else name
                dct[relation.name] = property(
                    doc='[relation] one-to-{0} relation with {1}.{2}\n@type: {3}'.format(
                        'one' if relation.onetoone else 'many',
                        itemtype,
                        relation.foreign_key,
                        itemtype
                    )
                )
            for dynamic in dct['_dynamics']:
                if bases[0].__name__ == 'DataObject':
                    if '_{0}'.format(dynamic.name) not in dct:
                        raise LookupError('Dynamic property {0} in {1} could not be resolved'.format(dynamic.name, name))
                    method = dct['_{0}'.format(dynamic.name)]
                else:
                    methods = [getattr(base, '_{0}'.format(dynamic.name)) for base in bases if hasattr(base, '_{0}'.format(dynamic.name))]
                    if len(methods) == 0:
                        raise LookupError('Dynamic property {0} in {1} could not be resolved'.format(dynamic.name, name))
                    method = [0]
                docstring = method.__doc__.strip()
                if isinstance(dynamic.return_type, type):
                    itemtype = dynamic.return_type.__name__
                    extra_info = ''
                else:
                    itemtype = 'Enum({0})'.format(dynamic.return_type[0].__class__.__name__)
                    extra_info = '(enum values: {0})'.format(', '.join(dynamic.return_type))
                dct[dynamic.name] = property(
                    fget=method,
                    doc='[dynamic] ({0}s) {1} {2}\n@rtype: {3}'.format(dynamic.timeout, docstring, extra_info, itemtype)
                )

        return super(MetaClass, mcs).__new__(mcs, name, bases, dct)


class DataObjectAttributeEncoder(json.JSONEncoder):
    """
    Custom JSONEncoder for attributes
    """
    def default(self, obj):
        """
        Default return value
        :param obj: Object to encode
        :return: String
        """
        return "{0}: {1}".format(type(obj), obj)


class DataObject(object):
    """
    This base class contains all logic to support our multiple backends and the caching
      - Storage backends:
        - Persistent backend for persistent storage (key-value store)
        - Volatile backend for volatile but fast storage (key-value store)
        - Storage backends are abstracted and injected into this class, making it possible to use
          fake backends
      - Features:
        - Hybrid property access:
          - Persistent backend
          - 3rd party component for "live" properties
        - Individual cache settings for "live" properties
        - 1-n relations with automatic property propagation
        - Recursive save
    """
    __metaclass__ = MetaClass

    ##############
    # Attributes #
    ##############

    # Properties that needs to be overwritten by implementation
    _properties = []  # Blueprint data of the object type
    _dynamics = []    # Timeout of readonly object properties cache
    _relations = []   # Blueprint for relations

    NAMESPACE = 'ovs_data'

    ###############
    # Constructor #
    ###############

    def __new__(cls, *args, **kwargs):
        """
        Initializes the class
        """
        hybrid_structure = HybridRunner.get_hybrids()
        identifier = Descriptor(cls).descriptor['identifier']
        if identifier in hybrid_structure and identifier != hybrid_structure[identifier]['identifier']:
            new_class = Descriptor().load(hybrid_structure[identifier]).get_object()
            return super(cls, new_class).__new__(new_class, *args)
        return super(DataObject, cls).__new__(cls)

    def __init__(self, guid=None, data=None, datastore_wins=False, volatile=False, _hook=None):
        """
        Loads an object with a given guid. If no guid is given, a new object
        is generated with a new guid.
        * guid: The guid indicating which object should be loaded
        * datastoreWins: Optional boolean indicating save conflict resolve management.
        ** True: when saving, external modified fields will not be saved
        ** False: when saving, all changed data will be saved, regardless of external updates
        ** None: in case changed field were also changed externally, an error will be raised
        """

        # Initialize super class
        super(DataObject, self).__init__()

        # Initialize internal fields
        self._frozen = False
        self._datastore_wins = datastore_wins
        self._guid = None    # Guid identifier of the object
        self._original = {}  # Original data copy
        self._metadata = {}  # Some metadata, mainly used for unit testing
        self._data = {}      # Internal data storage
        self._objects = {}   # Internal objects storage

        # Initialize public fields
        self.dirty = False
        self.volatile = volatile

        # Worker fields/objects
        self._classname = self.__class__.__name__.lower()

        # Rebuild _relation types
        hybrid_structure = HybridRunner.get_hybrids()
        for relation in self._relations:
            if relation.foreign_type is not None:
                identifier = Descriptor(relation.foreign_type).descriptor['identifier']
                if identifier in hybrid_structure and identifier != hybrid_structure[identifier]['identifier']:
                    relation.foreign_type = Descriptor().load(hybrid_structure[identifier]).get_object()

        # Init guid
        self._new = False
        if guid is None:
            self._guid = str(uuid.uuid4())
            self._new = True
        else:
            self._guid = str(guid)

        # Build base keys
        self._key = '{0}_{1}_{2}'.format(DataObject.NAMESPACE, self._classname, self._guid)

        # Worker mutexes
        self._mutex_version = VolatileMutex('ovs_dataversion_{0}_{1}'.format(self._classname, self._guid))

        # Load data from cache or persistent backend where appropriate
        self._volatile = VolatileFactory.get_client()
        self._persistent = PersistentFactory.get_client()
        self._metadata['cache'] = None
        if self._new:
            self._data = {}
        else:
            if data is not None:
                self._data = copy.deepcopy(data)
                self._metadata['cache'] = None
            else:
                self._data = self._volatile.get(self._key)
                if self._data is None:
                    self._metadata['cache'] = False
                    try:
                        self._data = self._persistent.get(self._key)
                    except KeyNotFoundException:
                        raise ObjectNotFoundException('{0} with guid \'{1}\' could not be found'.format(
                            self.__class__.__name__, self._guid
                        ))
                else:
                    self._metadata['cache'] = True

        # Set default values on new fields
        for prop in self._properties:
            if prop.name not in self._data:
                self._data[prop.name] = prop.default
            self._add_property(prop)

        # Load relations
        for relation in self._relations:
            if relation.name not in self._data:
                if relation.foreign_type is None:
                    cls = self.__class__
                else:
                    cls = relation.foreign_type
                self._data[relation.name] = Descriptor(cls).descriptor
            self._add_relation_property(relation)

        # Add wrapped properties
        for dynamic in self._dynamics:
            self._add_dynamic_property(dynamic)

        # Load foreign keys
        relations = RelationMapper.load_foreign_relations(self.__class__)
        if relations is not None:
            for key, info in relations.iteritems():
                self._objects[key] = {'info': info,
                                      'data': None}
                self._add_list_property(key, info['list'])

        if _hook is not None and hasattr(_hook, '__call__'):
            _hook()

        if not self._new:
            # Re-cache the object, if required
            if self._metadata['cache'] is False:
                # The data wasn't loaded from the cache, so caching is required now
                try:
                    self._mutex_version.acquire(30)
                    this_version = self._data['_version']
                    store_version = self._persistent.get(self._key)['_version']
                    if this_version == store_version:
                        self._volatile.set(self._key, self._data)
                except KeyNotFoundException:
                    raise ObjectNotFoundException('{0} with guid \'{1}\' could not be found'.format(
                        self.__class__.__name__, self._guid
                    ))
                finally:
                    self._mutex_version.release()

        # Freeze property creation
        self._frozen = True

        # Optionally, initialize some fields
        if data is not None:
            for prop in self._properties:
                if prop.name in data:
                    setattr(self, prop.name, data[prop.name])

        # Store original data
        self._original = copy.deepcopy(self._data)

    ##################################################
    # Helper methods for dynamic getting and setting #
    ##################################################

    def _add_property(self, prop):
        """
        Adds a simple property to the object
        """
        # pylint: disable=protected-access
        fget = lambda s: s._get_property(prop)
        fset = lambda s, v: s._set_property(prop, v)
        # pylint: enable=protected-access
        setattr(self.__class__, prop.name, property(fget, fset))

    def _add_relation_property(self, relation):
        """
        Adds a complex property to the object (hybrids)
        """
        # pylint: disable=protected-access
        fget = lambda s: s._get_relation_property(relation)
        fset = lambda s, v: s._set_relation_property(relation, v)
        gget = lambda s: s._get_guid_property(relation)
        # pylint: enable=protected-access
        setattr(self.__class__, relation.name, property(fget, fset))
        setattr(self.__class__, '{0}_guid'.format(relation.name), property(gget))

    def _add_list_property(self, attribute, list):
        """
        Adds a list (readonly) property to the object
        """
        # pylint: disable=protected-access
        fget = lambda s: s._get_list_property(attribute)
        gget = lambda s: s._get_list_guid_property(attribute)
        # pylint: enable=protected-access
        setattr(self.__class__, attribute, property(fget))
        setattr(self.__class__, ('{0}_guids' if list else '{0}_guid').format(attribute), property(gget))

    def _add_dynamic_property(self, dynamic):
        """
        Adds a dynamic property to the object
        """
        # pylint: disable=protected-access
        fget = lambda s: s._get_dynamic_property(dynamic)
        # pylint: enable=protected-access
        setattr(self.__class__, dynamic.name, property(fget))

    # Helper method supporting property fetching
    def _get_property(self, prop):
        """
        Getter for a simple property
        """
        return self._data[prop.name]

    def _get_relation_property(self, relation):
        """
        Getter for a complex property (hybrid)
        It will only load the object once and caches it for the lifetime of this object
        """
        attribute = relation.name
        if attribute not in self._objects:
            descriptor = Descriptor().load(self._data[attribute])
            self._objects[attribute] = descriptor.get_object(instantiate=True)
        return self._objects[attribute]

    def _get_guid_property(self, relation):
        """
        Getter for a foreign key property
        """
        attribute = relation.name
        return self._data[attribute]['guid']

    def _get_list_property(self, attribute):
        """
        Getter for the list property
        It will execute the related query every time to return a list of hybrid objects that
        refer to this object. The resulting data will be stored or merged into the cached list
        preserving as much already loaded objects as possible
        """
        info = self._objects[attribute]['info']
        remote_class = Descriptor().load(info['class']).get_object()
        remote_key = info['key']
        datalist = DataList.get_relation_set(remote_class, remote_key, self.__class__, attribute, self.guid)
        if self._objects[attribute]['data'] is None:
            self._objects[attribute]['data'] = datalist
        else:
            self._objects[attribute]['data'].update(datalist)
        if info['list'] is True:
            return self._objects[attribute]['data']
        else:
            data = self._objects[attribute]['data']
            if len(data) > 1:
                raise InvalidRelationException('More than one element found in {0}'.format(attribute))
            return data[0] if len(data) == 1 else None

    def _get_list_guid_property(self, attribute):
        """
        Getter for guid list property
        """
        list_or_item = getattr(self, attribute)
        if list_or_item is None:
            return None
        if hasattr(list_or_item, '_guids'):
            return list_or_item._guids
        return list_or_item.guid

    def _get_dynamic_property(self, dynamic):
        """
        Getter for dynamic property, wrapping the internal data loading property
        in a caching layer
        """
        data_loader = getattr(self, '_{0}'.format(dynamic.name))
        return self._backend_property(data_loader, dynamic)

    # Helper method supporting property setting
    def _set_property(self, prop, value):
        """
        Setter for a simple property that will validate the type
        """
        self.dirty = True
        if value is None:
            self._data[prop.name] = value
        else:
            correct, allowed_types, given_type = Toolbox.check_type(value, prop.property_type)
            if correct:
                self._data[prop.name] = value
            else:
                raise TypeError('Property {0} allows types {1}. {2} given'.format(
                    prop.name, str(allowed_types), given_type
                ))

    def _set_relation_property(self, relation, value):
        """
        Setter for a complex property (hybrid) that will validate the type
        """
        self.dirty = True
        attribute = relation.name
        if value is None:
            self._objects[attribute] = None
            self._data[attribute]['guid'] = None
        else:
            descriptor = Descriptor(value.__class__).descriptor
            if descriptor['identifier'] != self._data[attribute]['identifier']:
                if descriptor['type'] == self._data[attribute]['type']:
                    logger.error('Corrupt descriptors: {0} vs {1}'.format(descriptor, self._data[attribute]))
                raise TypeError('An invalid type was given: {0} instead of {1}'.format(
                    descriptor['type'], self._data[attribute]['type']
                ))
            self._objects[attribute] = value
            self._data[attribute]['guid'] = value.guid

    def __setattr__(self, key, value):
        """
        __setattr__ hook that will block creating on the fly new properties, except
        the predefined ones
        """
        if not hasattr(self, '_frozen') or not self._frozen:
            allowed = True
        else:
            # If our object structure is frozen (which is after __init__), we only allow known
            # property updates: items that are in __dict__ and our own blueprinting dicts
            allowed = key in self.__dict__ \
                or key in (prop.name for prop in self._properties) \
                or key in (relation.name for relation in self._relations) \
                or key in (dynamic.name for dynamic in self._dynamics)
        if allowed:
            super(DataObject, self).__setattr__(key, value)
        else:
            raise RuntimeError('Property {0} does not exist on this object.'.format(key))

    ###############
    # Saving data #
    ###############

    def save(self, recursive=False, skip=None, _hook=None):
        """
        Save the object to the persistent backend and clear cache, making use
        of the specified conflict resolve settings.
        It will also invalidate certain caches if required. For example lists pointing towards this
        object
        :param recursive: Save related sub-objects recursively
        :param skip: Skip certain relations
        :param _hook:
        """
        if self.volatile is True:
            raise VolatileObjectException()

        tries = 0
        successful = False
        optimistic = True
        last_assert = None
        while successful is False:
            tries += 1
            if tries > 5:
                logger.error('Raising RaceConditionException. Last AssertException: {0}'.format(last_assert))
                raise RaceConditionException()

            invalid_fields = []
            for prop in self._properties:
                if prop.mandatory is True and self._data[prop.name] is None:
                    invalid_fields.append(prop.name)
            for relation in self._relations:
                if relation.mandatory is True and self._data[relation.name]['guid'] is None:
                    invalid_fields.append(relation.name)
            if len(invalid_fields) > 0:
                raise MissingMandatoryFieldsException('Missing fields on {0}: {1}'.format(self._classname, ', '.join(invalid_fields)))

            if recursive:
                # Save objects that point to us (e.g. disk.vmachine - if this is disk)
                for relation in self._relations:
                    if relation.name != skip:  # disks will be skipped
                        item = getattr(self, relation.name)
                        if item is not None:
                            item.save(recursive=True, skip=relation.foreign_key)

                # Save object we point at (e.g. machine.vdisks - if this is machine)
                relations = RelationMapper.load_foreign_relations(self.__class__)
                if relations is not None:
                    for key, info in relations.iteritems():
                        if key != skip:  # machine will be skipped
                            if info['list'] is True:
                                for item in getattr(self, key).iterloaded():
                                    item.save(recursive=True, skip=info['key'])
                            else:
                                item = getattr(self, key)
                                if item is not None:
                                    item.save(recursive=True, skip=info['key'])

            validation_keys = []
            for relation in self._relations:
                if self._data[relation.name]['guid'] is not None:
                    if relation.foreign_type is None:
                        cls = self.__class__
                    else:
                        cls = relation.foreign_type
                    validation_keys.append('{0}_{1}_{2}'.format(DataObject.NAMESPACE, cls.__name__.lower(), self._data[relation.name]['guid']))
            try:
                [_ for _ in self._persistent.get_multi(validation_keys)]
            except KeyNotFoundException:
                raise ObjectNotFoundException('One of the relations specified in {0} with guid \'{1}\' was not found'.format(
                    self.__class__.__name__, self._guid
                ))

            transaction = self._persistent.begin_transaction()
            if self._new is True:
                data = {'_version': 0}
            elif optimistic is True:
                self._persistent.assert_value(self._key, self._original, transaction=transaction)
                data = copy.deepcopy(self._original)
            else:
                try:
                    current_data = self._persistent.get(self._key)
                except KeyNotFoundException:
                    raise ObjectNotFoundException('{0} with guid \'{1}\' was deleted'.format(
                        self.__class__.__name__, self._guid
                    ))
                self._persistent.assert_value(self._key, current_data, transaction=transaction)
                data = copy.deepcopy(current_data)

            changed_fields = []
            data_conflicts = []
            for attribute in self._data.keys():
                if attribute == '_version':
                    continue
                if self._data[attribute] != self._original[attribute]:
                    # We changed this value
                    changed_fields.append(attribute)
                    if attribute in data and self._original[attribute] != data[attribute]:
                        # Some other process also wrote to the database
                        if self._datastore_wins is None:
                            # In case we didn't set a policy, we raise the conflicts
                            data_conflicts.append(attribute)
                        elif self._datastore_wins is False:
                            # If the datastore should not win, we just overwrite the data
                            data[attribute] = self._data[attribute]
                        # If the datastore should win, we discard/ignore our change
                    else:
                        # Normal scenario, saving data
                        data[attribute] = self._data[attribute]
                elif attribute not in data:
                    data[attribute] = self._data[attribute]
            for attribute in data.keys():
                if attribute == '_version':
                    continue
                if attribute not in self._data:
                    del data[attribute]
            if data_conflicts:
                raise ConcurrencyException('Got field conflicts while saving {0}. Conflicts: {1}'.format(
                    self._classname, ', '.join(data_conflicts)
                ))

            # Refresh internal data structure
            self._data = copy.deepcopy(data)

            # First, update reverse index
            base_reverse_key = 'ovs_reverseindex_{0}_{1}|{2}|{3}'
            for relation in self._relations:
                key = relation.name
                original_guid = self._original[key]['guid']
                new_guid = self._data[key]['guid']
                if original_guid != new_guid:
                    if relation.foreign_type is None:
                        classname = self.__class__.__name__.lower()
                    else:
                        classname = relation.foreign_type.__name__.lower()
                    if original_guid is not None:
                        reverse_key = base_reverse_key.format(classname, original_guid, relation.foreign_key, self.guid)
                        self._persistent.delete(reverse_key, transaction=transaction)
                    if new_guid is not None:
                        reverse_key = base_reverse_key.format(classname, new_guid, relation.foreign_key, self.guid)
                        self._persistent.assert_exists('{0}_{1}_{2}'.format(DataObject.NAMESPACE, classname, new_guid))
                        self._persistent.set(reverse_key, 0, transaction=transaction)

            # Second, invalidate property lists
            cache_key = '{0}_{1}|'.format(DataList.CACHELINK, self._classname)
            list_keys = set()
            cache_keys = {}
            for key in list(self._persistent.prefix(cache_key)):
                list_key, field = key.replace(cache_key, '').split('|')
                if list_key not in cache_keys:
                    cache_keys[list_key] = [False, []]
                cache_keys[list_key][1].append(key)
                if field in changed_fields or self._new is True:
                    list_keys.add(list_key)
                    cache_keys[list_key][0] = True
            for list_key in list_keys:
                self._volatile.delete(list_key)
                if cache_keys[list_key][0] is True:
                    for key in cache_keys[list_key][1]:
                        self._persistent.delete(key, must_exist=False, transaction=transaction)

            if _hook is not None and hasattr(_hook, '__call__'):
                _hook()

            # Save the data
            self._data['_version'] += 1
            try:
                self._persistent.set(self._key, self._data, transaction=transaction)
                self._persistent.apply_transaction(transaction)
                self._volatile.delete(self._key)
                successful = True
            except KeyNotFoundException:
                raise ObjectNotFoundException('{0} with guid \'{1}\' was deleted'.format(
                    self.__class__.__name__, self._guid
                ))
            except AssertException as ex:
                last_assert = ex
                optimistic = False
                time.sleep(randint(0, 25) / 100.0)

        self.invalidate_dynamics()
        self._original = copy.deepcopy(self._data)

        self.dirty = False
        self._new = False

    ###############
    # Other CRUDs #
    ###############

    def delete(self, abandon=None, _hook=None):
        """
        Delete the given object. It also invalidates certain lists
        :param abandon: Indicates whether(which) linked objects can be unlinked. Use with caution
        """
        if self.volatile is True:
            raise VolatileObjectException()

        tries = 0
        successful = False
        last_assert = None
        while successful is False:
            tries += 1
            if tries > 5:
                logger.error('Raising RaceConditionException. Last AssertException: {0}'.format(last_assert))
                raise RaceConditionException()

            transaction = self._persistent.begin_transaction()

            # Check foreign relations
            relations = RelationMapper.load_foreign_relations(self.__class__)
            if relations is not None:
                for key, info in relations.iteritems():
                    items = getattr(self, key)
                    if info['list'] is True:
                        if len(items) > 0:
                            if abandon is not None and (key in abandon or '_all' in abandon):
                                for item in items.itersafe():
                                    setattr(item, info['key'], None)
                                    try:
                                        item.save()
                                    except ObjectNotFoundException:
                                        pass
                            else:
                                multi = 'are {0} items'.format(len(items)) if len(items) > 1 else 'is 1 item'
                                raise LinkedObjectException('There {0} left in self.{1}'.format(multi, key))
                    elif items is not None:
                        # No list (so a 1-to-1 relation), so there should be an object, or None
                        item = items  # More clear naming
                        if abandon is not None and (key in abandon or '_all' in abandon):
                            setattr(item, info['key'], None)
                            try:
                                item.save()
                            except ObjectNotFoundException:
                                pass
                        else:
                            raise LinkedObjectException('There is still an item linked in self.{0}'.format(key))

            # Delete the object out of the persistent store
            try:
                self._persistent.delete(self._key, transaction=transaction)
            except KeyNotFoundException:
                pass

            # First, update reverse index
            base_reverse_key = 'ovs_reverseindex_{0}_{1}|{2}|{3}'
            for relation in self._relations:
                key = relation.name
                original_guid = self._original[key]['guid']
                if original_guid is not None:
                    if relation.foreign_type is None:
                        classname = self.__class__.__name__.lower()
                    else:
                        classname = relation.foreign_type.__name__.lower()
                    reverse_key = base_reverse_key.format(classname, original_guid, relation.foreign_key, self.guid)
                    self._persistent.delete(reverse_key, transaction=transaction)

            # Second, invalidate property lists
            list_keys = []
            cache_key = '{0}_{1}|'.format(DataList.CACHELINK, self._classname)
            for key in list(self._persistent.prefix(cache_key)):
                list_key, _ = key.replace(cache_key, '').split('|')
                if list_key not in list_keys:
                    list_keys.append(list_key)
                    self._volatile.delete(list_key)
                self._persistent.delete(key, must_exist=False, transaction=transaction)

            if _hook is not None and hasattr(_hook, '__call__'):
                _hook()

            try:
                self._persistent.apply_transaction(transaction)
                successful = True
            except KeyNotFoundException as ex:
                if ex.message != self._key:
                    raise
                successful = True
            except AssertException as ex:
                last_assert = ex

        # Delete the object and its properties out of the volatile store
        self.invalidate_dynamics()
        self._volatile.delete(self._key)

    # Discard all pending changes
    def discard(self):
        """
        Discard all pending changes, reloading the data from the persistent backend
        """
        self.__init__(guid=self._guid,
                      datastore_wins=self._datastore_wins)

    def invalidate_dynamics(self, properties=None):
        """
        Invalidates all dynamic property caches. Use with caution, as this action can introduce
        a short performance hit.
        :param properties: Properties to invalidate
        """
        if properties is not None and not isinstance(properties, list):
            properties = [properties]
        for dynamic in self._dynamics:
            if properties is None or dynamic.name in properties:
                key = '{0}_{1}'.format(self._key, dynamic.name)
                mutex = VolatileMutex(key)
                try:
                    if dynamic.locked:
                        mutex.acquire()
                    self._volatile.delete(key)
                finally:
                    mutex.release()

    def invalidate_cached_objects(self):
        """
        Invalidates cached objects so they are reloaded when used.
        """
        for relation in self._relations:
            self._objects.pop(relation.name, None)

    def export(self):
        """
        Exports this object's data for import in another object
        """
        return dict((prop.name, self._data[prop.name]) for prop in self._properties)

    def serialize(self, depth=0):
        """
        Serializes the internal data, getting rid of certain metadata like descriptors
        :param depth: Depth of relations to serialize
        """
        data = {'guid': self.guid}
        for relation in self._relations:
            key = relation.name
            if depth == 0:
                data['{0}_guid'.format(key)] = self._data[key]['guid']
            else:
                instance = getattr(self, key)
                if instance is not None:
                    data[key] = getattr(self, key).serialize(depth=(depth - 1))
                else:
                    data[key] = None
        for prop in self._properties:
            data[prop.name] = self._data[prop.name]
        for dynamic in self._dynamics:
            data[dynamic.name] = getattr(self, dynamic.name)
        return data

    def copy(self, other_object, include=None, exclude=None, include_relations=False):
        """
        Copies all _properties (and optionally _relations) properties over from a given hybrid to
        self. One can pass in a list of properties that should be copied, or a list of properties
        that should not be copied. Exclude > Include
        :param other_object: Other object to copy properties from into current 1
        :param include: Properties to include
        :param exclude: Properties to exclude
        :param include_relations: Include all relations
        """
        if include is not None and not isinstance(include, list):
            raise TypeError('Argument include should be None or a list of strings')
        if exclude is not None and not isinstance(exclude, list):
            raise TypeError('Argument exclude should be None or a list of strings')
        if self.__class__.__name__ != other_object.__class__.__name__:
            raise TypeError('Properties can only be loaded from hybrids of the same type')

        all_properties = [prop.name for prop in self._properties]
        all_relations = [relation.name for relation in self._relations]
        properties_to_copy = all_properties if include is None else include
        if include_relations:
            properties_to_copy += all_relations

        if exclude:
            properties_to_copy = [p for p in properties_to_copy if p not in exclude]

        possible_options = all_properties + (all_relations if include_relations else [])
        properties_to_copy = [p for p in properties_to_copy if p in possible_options]

        for key in properties_to_copy:
            setattr(self, key, getattr(other_object, key))

    def updated_on_datastore(self):
        """
        Checks whether this object has been modified on the datastore
        """
        if self.volatile is True:
            return False

        this_version = self._data['_version']
        cached_object = self._volatile.get(self._key)
        if cached_object is None:
            try:
                backend_version = self._persistent.get(self._key)['_version']
            except KeyNotFoundException:
                backend_version = -1
        else:
            backend_version = cached_object['_version']
        return this_version != backend_version

    ##############
    # Properties #
    ##############

    @property
    def guid(self):
        """
        The primary key of the object
        """
        return self._guid

    ##################
    # Helper methods #
    ##################

    def _backend_property(self, function, dynamic):
        """
        Handles the internal caching of dynamic properties
        """
        caller_name = dynamic.name
        cache_key = '{0}_{1}'.format(self._key, caller_name)
        mutex = VolatileMutex(cache_key)
        try:
            cached_data = self._volatile.get(cache_key)
            if cached_data is None:
                if dynamic.locked:
                    mutex.acquire()
                    cached_data = self._volatile.get(cache_key)
                if cached_data is None:
                    function_info = inspect.getargspec(function)
                    if 'dynamic' in function_info.args:
                        cached_data = function(dynamic=dynamic)  # Load data from backend
                    else:
                        cached_data = function()
                    if cached_data is not None:
                        correct, allowed_types, given_type = Toolbox.check_type(cached_data, dynamic.return_type)
                        if not correct:
                            raise TypeError('Dynamic property {0} allows types {1}. {2} given'.format(
                                caller_name, str(allowed_types), given_type
                            ))
                    if dynamic.timeout > 0:
                        self._volatile.set(cache_key, cached_data, dynamic.timeout)
            return cached_data
        finally:
            mutex.release()

    def __str__(self):
        """
        The string representation of a DataObject is the serialized value
        """
        return json.dumps(self.serialize(), indent=4, cls=DataObjectAttributeEncoder)

    def __hash__(self):
        """
        Defines a hashing equivalent for a given object. The key (object type and guid) is considered to be identifying
        """
        return hash(self._key)

    def __eq__(self, other):
        """
        Checks whether two objects are the same.
        """
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        """
        Checks whether two objects are not the same.
        """
        return not self.__eq__(other)

    def _benchmark(self, iterations=100):
        import time
        begin = time.time()
        stats = {}
        totals = []
        for _ in range(iterations):
            istart = time.time()
            for dynamic in self._dynamics:
                start = time.time()
                function = getattr(self, '_{0}'.format(dynamic.name))
                function_info = inspect.getargspec(function)
                if 'dynamic' in function_info.args:
                    function(dynamic=dynamic)
                else:
                    function()
                duration = time.time() - start
                if dynamic.name not in stats:
                    stats[dynamic.name] = []
                stats[dynamic.name].append(duration)
            totals.append(time.time() - istart)
        print "Object: {0}('{1}')".format(self.__class__.__name__, self._guid)
        for dyn in stats:
            print '- {0}: avg {1:.3f}s (min: {2:.3f}s, max: {3:.3f}s)'.format(dyn, sum(stats[dyn]) / float(len(stats[dyn])), min(stats[dyn]), max(stats[dyn]))
        print 'Took {0:.3f}s for {1} iterations'.format(time.time() - begin, iterations)
        print 'Avg: {0:.3f}s, min: {1:.3f}s, max: {2:.3f}s'.format(sum(totals) / float(len(totals)), min(totals), max(totals))

    @staticmethod
    def enumerator(name, items):
        """
        Generates an enumerator
        :param name: Name of enumerator
        :param items: Enumerator items
        """
        class Enumerator(dict):
            """
            Enumerator class
            """
            def __init__(self, *args, **kwargs):
                super(Enumerator, self).__init__(*args, **kwargs)

        if isinstance(items, list):
            enumerator = Enumerator(zip(items, items))
        elif isinstance(items, dict):
            enumerator = Enumerator(**items)
        else:
            raise ValueError("Argument 'items' should be a list or a dict. A '{0}' was given".format(type(items)))
        enumerator.__name__ = name
        for item in enumerator:
            setattr(enumerator, item, enumerator[item])
        return enumerator
