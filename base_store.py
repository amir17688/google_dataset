#!/usr/bin/env python

"""Standalone use utility methods for CouchDB"""

__author__ = 'Thomas R. Lennan, Michael Meisinger'


from uuid import uuid4
import couchdb
from couchdb.http import PreconditionFailed, ResourceConflict, ResourceNotFound, ServerError
import gevent

from pyon.datastore.couchdb.couch_common import AbstractCouchDataStore
from pyon.datastore.couchdb.views import get_couchdb_view_designs
from pyon.core.exception import BadRequest, Conflict, NotFound
from pyon.util.containers import get_safe, DictDiffer

from ooi.logging import log


class CouchDataStore(AbstractCouchDataStore):
    """
    Datastore implementation utilizing CouchDB to persist documents.
    For API info, see: http://packages.python.org/CouchDB/client.html.
    A base datastore knows how to manage datastores, CRUD documents (dict) and access generic indexes.
    """
    def __init__(self, datastore_name=None, config=None, scope=None, profile=None, **kwargs):
        super(CouchDataStore, self).__init__(datastore_name=datastore_name, config=config, scope=scope, profile=profile)

        if self.config.get("type", None) and self.config['type'] != "couchdb":
            raise BadRequest("Datastore server config is not couchdb: %s" % self.config)
        if self.datastore_name and self.datastore_name != self.datastore_name.lower():
            raise BadRequest("Invalid CouchDB datastore name: '%s'" % self.datastore_name)
        if self.scope and self.scope != self.scope.lower():
            raise BadRequest("Invalid CouchDB scope name: '%s'" % self.scope)

        # Connection
        if self.username and self.password:
            connection_str = "http://%s:%s@%s:%s" % (self.username, self.password, self.host, self.port)
            log_connection_str = "http://%s:%s@%s:%s" % ("username", "password", self.host, self.port)
            log.debug("Using username:password authentication to connect to datastore")
        else:
            connection_str = "http://%s:%s" % (self.host, self.port)
            log_connection_str = connection_str

        log.info("Connecting to CouchDB server: %s", log_connection_str)
        self.server = couchdb.Server(connection_str)

        self._id_factory = None   # TODO

        # Just to test existence of the datastore
        if self.datastore_name:
            try:
                ds, _ = self._get_datastore()
            except NotFound:
                self.create_datastore()
                ds, _ = self._get_datastore()

    def close(self):
        """
        Close any connections required for this datastore.
        """
        log.trace("Closing connection to %s", self.datastore_name)
        # Compatiblity between couchdb client 0.8 and 0.9
        if hasattr(self.server.resource.session, 'conns'):
            conns = self.server.resource.session.conns
            self.server.resource.session.conns = {}     # just in case we try to reuse this, for some reason
        else:
            conns = self.server.resource.session.connection_pool.conns
            self.server.resource.session.connection_pool.conns = {}     # just in case we try to reuse this, for some reason
        map(lambda x: map(lambda y: y.close(), x), conns.values())


    # -------------------------------------------------------------------------
    # Couch database operations

    def _get_datastore(self, datastore_name=None):
        """
        Returns the couch datastore instance and datastore name.
        This caches the datastore instance to avoid an explicit lookup to save on http request.
        The consequence is that if another process deletes the datastore in the meantime, we will fail later.
        """
        datastore_name = self._get_datastore_name(datastore_name)

        if datastore_name in self._datastore_cache:
            return self._datastore_cache[datastore_name], datastore_name

        try:
            ds = self.server[datastore_name]   # Note: causes http lookup
            self._datastore_cache[datastore_name] = ds
            return ds, datastore_name
        except ResourceNotFound:
            raise NotFound("Datastore '%s' does not exist" % datastore_name)
        except ValueError:
            raise BadRequest("Datastore name '%s' invalid" % datastore_name)
        except ServerError as se:
            raise BadRequest("Data store name %s invalid" % datastore_name)

    def _create_datastore(self, datastore_name):
        try:
            self.server.create(datastore_name)
        except PreconditionFailed:
            raise BadRequest("Datastore with name %s already exists" % datastore_name)
        except ValueError:
            raise BadRequest("Datastore name %s invalid" % datastore_name)
        except ServerError as se:
            if se.message[1][0] == 'illegal_database_name':
                raise BadRequest("Data store name %s invalid" % datastore_name)
            else:
                raise

    def delete_datastore(self, datastore_name=None):
        try:
            super(CouchDataStore, self).delete_datastore(datastore_name)
        except ResourceNotFound:
            raise NotFound('Datastore %s does not exist' % datastore_name)
        except ValueError:
            raise BadRequest("Datastore name %s invalid" % datastore_name)
        except ServerError as se:
            if se.message[1][0] == 'illegal_database_name':
                raise BadRequest("Data store name %s invalid" % datastore_name)
            else:
                raise

    def list_datastores(self):
        """
        List all datastores within this datastore server. This is
        equivalent to listing all databases hosted on a database server.
        Returns scoped names.
        """
        return list(self.server)

    def info_datastore(self, datastore_name=None):
        """
        List information about a datastore.  Content may vary based
        on datastore type.
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        info = ds.info()
        return info

    def compact_datastore(self, datastore_name=None):
        ds, datastore_name = self._get_datastore(datastore_name)
        return ds.compact()

    def datastore_exists(self, datastore_name=None):
        """
        Indicates whether named datastore currently exists.
        """
        datastore_name = self._get_datastore_name(datastore_name)
        try:
            self.server[datastore_name]
            return True
        except ResourceNotFound:
            return False


    # -------------------------------------------------------------------------
    # Couch document operations

    def list_objects(self, datastore_name=None):
        """
        List all object types existing in the datastore instance.
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        return list(ds)

    def list_object_revisions(self, object_id, datastore_name=None):
        """
        Method for itemizing all the versions of a particular object
        known to the datastore.
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        gen = ds.revisions(object_id)
        res = [ent["_rev"] for ent in gen]
        return res


    def _save_doc(self, ds, doc):
        try:
            obj_id, version = ds.save(doc)
        except ResourceConflict:
            if "_rev" in doc:
                raise Conflict("Object with id %s revision conflict" % doc["_id"])
            else:
                raise BadRequest("Object with id %s already exists" % doc["_id"])

        return obj_id, version

    def _save_doc_mult(self, ds, docs):
        res = ds.update(docs)
        return res

    def create_doc(self, doc, object_id=None, attachments=None, datastore_name=None):
        if '_rev' in doc:
            raise BadRequest("Doc must not have '_rev'")
        return super(CouchDataStore, self).create_doc(doc, object_id=object_id, attachments=attachments, datastore_name=datastore_name)

    def create_attachment(self, doc, attachment_name, data, content_type=None, datastore_name=""):
        """
        Assumes that the document already exists and creates attachment to it.
        @param doc can be either id or a document
        """
        if not isinstance(attachment_name, str):
            raise BadRequest("attachment name is not string")
        if not isinstance(data, str) and not isinstance(data, file):
            raise BadRequest("data to create attachment is not a str or file")
        if isinstance(doc, str):
            doc = self.read_doc(doc_id=doc)
        ds, _ = self._get_datastore(datastore_name)
        ds.put_attachment(doc=doc, content=data, filename=attachment_name, content_type=content_type)
        self._count(create_attachment=1)

    def update_doc(self, doc, datastore_name=None):
        if '_rev' not in doc:
            raise BadRequest("Doc must have '_rev'")
        return super(CouchDataStore, self).update_doc(doc, datastore_name=datastore_name)

    def update_doc_mult(self, docs, datastore_name=None):
        if not all(["_rev" in doc for doc in docs]):
            raise BadRequest("Docs must have '_rev'")

        return super(CouchDataStore, self).update_doc_mult(docs, datastore_name=datastore_name)

    def update_attachment(self, doc, attachment_name, data, content_type=None, datastore_name=""):
        self.create_attachment(doc=doc, attachment_name=attachment_name, data=data,
                               content_type=content_type,
                               datastore_name=datastore_name)
        self._count(update_attachment=1)

    def read_doc(self, doc_id, rev_id=None, datastore_name=None, object_type=None):
        """"
        Fetch a raw doc instance.  If rev_id is specified, an attempt
        will be made to return that specific doc version.  Otherwise,
        the HEAD version is returned.
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        if not rev_id:
            doc = ds.get(doc_id)
            if doc is None:
                raise NotFound('Object with id %s does not exist.' % doc_id)
        else:
            # There was an issue with couchdb_python 0.8 and concurrent use of this library
            # See https://code.google.com/p/couchdb-python/issues/detail?id=204
            # Fixed in client 0.9
            doc = ds.get(doc_id, rev=rev_id)
            if doc is None:
                raise NotFound('Object with id %s does not exist.' % doc_id)
        self._count(read=1)

        return doc

    def read_doc_mult(self, object_ids, datastore_name=None, strict=True):
        """"
        Fetch a number of raw doc instances, HEAD rev.
        """
        if not object_ids:
            return []
        ds, datastore_name = self._get_datastore(datastore_name)
        rows = ds.view("_all_docs", keys=object_ids, include_docs=True)

        if strict:
            # Check for docs not found
            notfound_list = ['Object with id %s does not exist.' % str(row.key)
                             for row in rows if row.doc is None]
            if notfound_list:
                raise NotFound("\n".join(notfound_list))

        doc_list = [row.doc.copy() if row.doc is not None else None for row in rows]   # TODO: Is copy() necessary?
        self._count(read_mult_call=1, read_mult_obj=len(doc_list))

        return doc_list

    def read_attachment(self, doc, attachment_name, datastore_name=""):
        if not isinstance(attachment_name, str):
            raise BadRequest("Attachment_name param is not str")

        ds, datastore_name = self._get_datastore(datastore_name)

        attachment = ds.get_attachment(doc, attachment_name)

        if attachment is None:
            raise NotFound('Attachment %s does not exist in document %s.%s.',
                           attachment_name, datastore_name, doc)

        attachment_content = attachment.read()
        if not isinstance(attachment_content, str):
            raise NotFound('Attachment read is not a string')

        self._count(read_attachment=1)

        return attachment_content

    def list_attachments(self, doc):
        """
        Returns the a list of attachments for the document, as a dict of dicts, key'ed by name with
        nested keys 'data' for the content and 'content-type'.
        @param doc  accepts either str (meaning an id) or dict (a full document).
        """
        if isinstance(doc, dict) and '_attachments' not in doc:
            # Need to reread again, because it did not contain the _attachments
            doc = self.read_doc(doc_id=doc["_id"])
        elif isinstance(doc, str):
            doc = self.read_doc(doc_id=doc)

        attachment_list = doc.get("_attachments", None)
        return attachment_list

    def delete_doc(self, doc, datastore_name=None, object_type=None, **kwargs):
        """
        Remove all versions of specified raw doc from the datastore.
        This method will check the '_rev' value to ensure that the doc
        provided is the most recent known doc version.  If not, a
        Conflict exception is thrown.
        If object id (str) is given instead of an object, deletes the
        object with the given id.
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        doc_id = doc if type(doc) is str else doc["_id"]
        log.debug('Deleting object %s/%s', datastore_name, doc_id)
        try:
            if type(doc) is str:
                del ds[doc_id]
            else:
                ds.delete(doc)
        except ResourceNotFound:
            raise NotFound('Object with id %s does not exist.' % doc_id)
        except ResourceConflict:
            raise Conflict("Object with id %s revision conflict" % doc["_id"])

    def delete_doc_mult(self, object_ids, datastore_name=None, object_type=None):
        obj_list = self.read_doc_mult(object_ids, datastore_name=datastore_name)
        for obj in obj_list:
            obj['_deleted'] = True
        self.update_doc_mult(obj_list, datastore_name=datastore_name)
        self._count(delete_mult_call=1, delete_mult_obj=len(obj_list))

    def delete_attachment(self, doc, attachment_name, datastore_name=""):
        """
        Deletes an attachment from a document.
        """
        if not isinstance(attachment_name, str):
            raise BadRequest("attachment_name is not a string")

        if isinstance(doc, str):
            doc = self.read_doc(doc_id=doc, datastore_name=datastore_name)

        ds, datastore_name = self._get_datastore(datastore_name)

        log.debug('Delete attachment %s of document %s', attachment_name, doc["_id"])
        ds.delete_attachment(doc, attachment_name)
        self._count(delete_attachment=1)


    # -------------------------------------------------------------------------
    # View operations

    def compact_views(self, design, datastore_name=None):
        ds, datastore_name = self._get_datastore(datastore_name)
        return ds.compact(design)

    def define_profile_views(self, profile=None, datastore_name=None, keepviews=False):
        profile = profile or self.profile
        ds_views = get_couchdb_view_designs(profile)
        self._define_profile_views(ds_views, datastore_name=datastore_name, keepviews=keepviews)

    def define_viewset(self, design_name, design_doc, datastore_name=None, keepviews=False):
        """
        Create or update a design document (i.e. a set of views).
        If design exists, only updates if view definitions are different to prevent rebuild of indexes.
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        doc_name = self._get_design_name(design_name)
        try:
            ds[doc_name] = dict(views=design_doc)
        #except ResourceConflict:
        except Exception:
            # View exists
            old_design = ds[doc_name]
            if not keepviews:
                try:
                    try:
                        del ds[doc_name]
                    except ResourceNotFound:
                        pass
                    ds[doc_name] = dict(views=design_doc)
                except Exception as ex:
                    # In case this gets executed concurrently and 2 processes perform the same creates
                    log.warn("Error defining datastore %s view %s (concurrent create?): %s", datastore_name, doc_name, str(ex))
            else:
                ddiff = DictDiffer(old_design.get("views", {}), design_doc)
                if ddiff.changed():
                    old_design["views"] = design_doc
                    ds.save(old_design)

    def refresh_views(self, datastore_name="", profile=None):
        """
        Triggers a refresh of all views (all designs) for this datastore's profile
        """
        profile = profile or self.profile
        ds_views = get_couchdb_view_designs(profile)
        for design_name, design_doc in ds_views.iteritems():
            self.refresh_viewset(design_name, datastore_name=datastore_name)

    def refresh_viewset(self, design, datastore_name=None):
        """
        Triggers the rebuild of a design document (set of views).
        """
        ds, datastore_name = self._get_datastore(datastore_name)
        doc_id = self._get_design_name(design)
        try:
            design_doc = ds[doc_id]
            view_name = design_doc["views"].keys()[0]
            ds.view(self._get_view_name(design, view_name))
        except Exception:
            log.exception("Problem with design %s/%s", datastore_name, doc_id)

    def delete_views(self, design, datastore_name=None):
        ds, datastore_name = self._get_datastore(datastore_name)
        try:
            del ds[self._get_design_name(design)]
        except ResourceNotFound:
            pass

ion model dependent. Could extract somewhere
        res = None
        try:
            if col == "geom":  # Resource center point (POINT type)
                if "geospatial_point_center" in doc:
                    lat, lon = doc["geospatial_point_center"].get("lat", 0), doc["geospatial_point_center"].get("lon", 0)
                    if lat != lon != 0:
                        res = "POINT(%s %s)" % (lon, lat)   # x,y

            elif col == "geom_loc":  # Resource bounding box (POLYGON shape, 2D)
                geoc = None
                if "geospatial_bounds" in doc:
                    geoc = doc["geospatial_bounds"]
                elif "constraint_list" in doc:
                    # Find the first one - alternatively could expand a bbox
                    for cons in doc["constraint_list"]:
                        if isinstance(cons, dict) and cons.get("type_", None) == "GeospatialBounds":
                            geoc = cons
                            break
                if geoc:
                    try:
                        geovals = dict(x1=float(geoc["geospatial_longitude_limit_west"]),
                                       y1=float(geoc["geospatial_latitude_limit_south"]),
                                       x2=float(geoc["geospatial_longitude_limit_east"]),
                                       y2=float(geoc["geospatial_latitude_limit_north"]))
                        if any((geovals["x1"], geovals["x2"], geovals["y1"], geovals["y2"])):
                            res = ("POLYGON((%(x1)s %(y1)s, %(x2)s %(y1)s, %(x2)s %(y2)s, %(x1)s %(y2)s, %(x1)s %(y1)s))") % geovals
                    except ValueError as ve:
                        log.warn("GeospatialBounds location values not parseable %s: %s", geoc, ve)

            if res:
                log.debug("Geospatial column %s value: %s", col, res)
        except Exception as ex:
            log.warn("Could not compute value for geospatial column %s: %s", col, ex)
        return res

    def _get_range_value(self, col, doc):
        """For a given range column name, return the appropriate representation given a document"""
        # TODO: This is information model dependent. Could extract somewhere
        res = None
        try:
            if col == "vertical_range":  # Resource vertical intent (NUMRANGE)
                geoc = None
                if "geospatial_bounds" in doc:
                    geoc = doc["geospatial_bounds"]
                elif "constraint_list" in doc:
                    # Find the first one - alternatively could expand a bbox
                    for cons in doc["constraint_list"]:
                        if isinstance(cons, dict) and cons.get("type_", None) == "GeospatialBounds":
                            geoc = cons
                            break
                if geoc:
                    try:
                        geovals = dict(z1=float(geoc["geospatial_vertical_min"]),
                                       z2=float(geoc["geospatial_vertical_max"]))
                        if any((geovals["z1"], geovals["z2"])):
                            res = "[%s, %s]" % (geovals["z1"], geovals["z2"])
                    except ValueError as ve:
                        log.warn("GeospatialBounds vertical values not parseable %s: %s", geoc, ve)

            elif col == "temporal_range":  # Resource temporal intent (NUMRANGE)
                tempc = None
                if "nominal_datetime" in doc:
                    # Case for DataProduct resources
                    tempc = doc["nominal_datetime"]
                elif "constraint_list" in doc:
                    # Case for Deployment resources
                    # Find the first one - alternatively could expand a bbox
                    for cons in doc["constraint_list"]:
                        if isinstance(cons, dict) and cons.get("type_", None) == "TemporalBounds":
                            tempc = cons
                            break
                #elif "ts_created" in doc and "ts_updated" in doc:
                #    # All other resources.
                #    # Values are in seconds float since epoch
                #    tempc = dict(start_datetime=parse_ion_ts(doc["ts_created"]),
                #                 end_datetime=parse_ion_ts(doc["ts_updated"]))

                if tempc and tempc["start_datetime"] and tempc["end_datetime"]:
                    try:
                        geovals = dict(t1=float(tempc["start_datetime"]),
                                       t2=float(tempc["end_datetime"]))
                        if any((geovals["t1"], geovals["t2"])):
                            res = "[%s, %s]" % (geovals["t1"], geovals["t2"])
                    except ValueError as ve:
                        log.warn("TemporalBounds values not parseable %s: %s", tempc, ve)
            if res:
                log.debug("Numrange column %s value: %s", col, res)
        except Exception as ex:
            log.warn("Could not compute value for numrange column %s: %s", col, ex)
        return res

    def _create_value_expression(self, col, doc, valuename, value_dict, allow_null_values=False, assign=False):
        """Returns part of an SQL statement to insert or update a value for a column.
        Places the value into a dict for the DB client to convert properly"""
        if col in GEOSPATIAL_COLS:
            value = self._get_geom_value(col, doc)
        elif col in NUMRANGE_COLS:
            value = self._get_range_value(col, doc)
        else:
            value = doc.get(col, None)

        if allow_null_values or value or type(value) is bool:
            insert_expr = ", "
            if assign:
                insert_expr += col + "="
            if col in GEOSPATIAL_COLS:
                insert_expr += "ST_GeomFromText(%(" + valuename + ")s,4326)"
            elif col in NUMRANGE_COLS:
                insert_expr += "%(" + valuename + ")s::numrange"
            else:
                insert_expr += "%(" + valuename + ")s"
            value_dict[valuename] = value
        else:
            insert_expr = None

        return insert_expr

    def create_doc(self, doc, object_id=None, attachments=None, datastore_name=None):
        qual_ds_name = self._get_datastore_name(datastore_name)
        if object_id and '_id' in doc:
            raise BadRequest("Doc must not have '_id'")
        if '_rev' in doc:
            raise BadRequest("Doc must not have '_rev'")
        #log.debug('create_doc(): Create document id=%s', "id")

        with self.pool.cursor(**self.cursor_args) as cur:
            try:
                # Assign an id to doc
                if "_id" not in doc:
                    object_id = object_id or self.get_unique_id()
                    doc["_id"] = object_id

                doc["_rev"] = "1"
                doc_json = json.dumps(doc)

                extra_cols, table = self._get_extra_cols(doc, qual_ds_name, self.profile)

                statement_args = dict(id=doc["_id"], doc=doc_json)
                xcol, xval = "", ""
                if extra_cols:
                    for col in extra_cols:
                        insert_expr = self._create_value_expression(col, doc, col, statement_args)
                        if insert_expr:
                            xcol += ", %s" % col
                            xval += insert_expr

                statement = "INSERT INTO " + table + " (id, rev, doc" + xcol + ") VALUES (%(id)s, 1, %(doc)s" + xval + ")"
                cur.execute(statement, statement_args)
                oid, version = doc["_id"], "1"
            except IntegrityError:
                raise BadRequest("Object with id %s already exists" % object_id)

        if attachments is not None:
            for att_name, att_value in attachments.iteritems():
                self.create_attachment(object_id, att_name, att_value['data'],
                                       content_type=att_value.get('content_type', ''), datastore_name=datastore_name)

        return oid, version

    def create_doc_mult(self, docs, object_ids=None, datastore_name=None):
        """Creates a list of objects and returns 3-tuples of (Success, id, rev)."""
        if type(docs) is not list:
            raise BadRequest("Invalid type for docs:%s" % type(docs))
        if object_ids and len(object_ids) != len(docs):
            raise BadRequest("Invalid object_ids")
        if not docs:
            return []
        log.debug('create_doc_mult(): create %s documents', len(docs))

        qual_ds_name = self._get_datastore_name(datastore_name)

        doc_obj_type = [self._get_obj_type(doc, self.profile) for doc in docs]
        all_obj_types = set(doc_obj_type)

        with self.pool.cursor(**self.cursor_args) as cur:
            # Need to make sure to first insert resources then associations for referential integrity
            for obj_type in sorted(all_obj_types, key=lambda x: OBJ_TYPE_PRECED.get(x, 10)):
                sb = StatementBuilder()
                docs_ot = [doc for (doc, doc_ot) in zip(docs, doc_obj_type) if doc_ot == obj_type]

                # Take the first document to determine the type of objects (resource, association, dir entry)
                extra_cols, table = self._get_extra_cols(docs_ot[0], qual_ds_name, self.profile)
                xcol = ""
                for col in extra_cols:
                    xcol += ", %s" % col
                sb.append("INSERT INTO "+table+" (id, rev, doc" + xcol + ") VALUES ")

                # Build a large statement
                for i, doc in enumerate(docs_ot):
                    object_id = object_ids[i] if object_ids else None
                    if "_id" not in doc:
                        object_id = object_id or self.get_unique_id()
                        doc["_id"] = object_id

                    doc["_rev"] = "1"
                    doc_json = json.dumps(doc)

                    if i>0:
                        sb.append(",")

                    sb.statement_args["id"+str(i)] = doc["_id"]
                    sb.statement_args["doc"+str(i)] = doc_json
                    xval = ""
                    for col in extra_cols:
                        valuename = col + str(i)
                        insert_expr = self._create_value_expression(col, doc, valuename, sb.statement_args, allow_null_values=True)
                        xval += insert_expr

                    sb.append("(%(id", str(i), ")s, 1, %(doc", str(i), ")s", xval, ")")

                try:
                    cur.execute(*sb.build())
                    if cur.rowcount != len(docs_ot):
                        log.warn("Number of objects created (%s) != objects given (%s) in %s", cur.rowcount, len(docs_ot), table)
                except IntegrityError as ie:
                    raise BadRequest("Some object already exists: %s" % ie)

        result_list = [(True, doc["_id"], doc["_rev"]) for doc in docs]

        return result_list

    def create_attachment(self, doc, attachment_name, data, content_type=None, datastore_name=""):
        if not isinstance(attachment_name, str):
            raise BadRequest("attachment name is not string")
        if not isinstance(data, str) and not isinstance(data, file):
            raise BadRequest("data to create attachment is not a str or file")

        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name + "_att"

        if isinstance(doc, str):
            doc_id = doc
        else:
            doc_id = doc['_id']
            self._assert_doc_rev(doc)

        statement_args = dict(docid=doc_id, rev=1, doc=buffer(data), name=attachment_name, content_type=content_type)
        with self.pool.cursor(**self.cursor_args) as cur:
            statement = "INSERT INTO " + table + " (docid, rev, doc, name, content_type) "+\
                        "VALUES (%(docid)s, 1, %(doc)s, %(name)s, %(content_type)s)"
            try:
                cur.execute(statement, statement_args)
            except IntegrityError:
                raise NotFound('Object with id %s does not exist.' % doc_id)

    def update_doc(self, doc, datastore_name=None):
        if '_id' not in doc:
            raise BadRequest("Doc must have '_id'")
        if '_rev' not in doc:
            raise BadRequest("Doc must have '_rev'")
        qual_ds_name = self._get_datastore_name(datastore_name)
        #log.debug('update_doc(): Update document id=%s', doc['_id'])

        with self.pool.cursor(**self.cursor_args) as cur:
            if "_deleted" in doc:
                self._delete_doc(cur, qual_ds_name, doc["_id"])
                oid, version = doc["_id"], doc["_rev"]
            else:
                oid, version = self._update_doc(cur, qual_ds_name, doc)

        return oid, version

    def update_doc_mult(self, docs, datastore_name=None):
        if type(docs) is not list:
            raise BadRequest("Invalid type for docs:%s" % type(docs))
        if not all(["_id" in doc for doc in docs]):
            raise BadRequest("Docs must have '_id'")
        if not all(["_rev" in doc for doc in docs]):
            raise BadRequest("Docs must have '_rev'")
        if not docs:
            return []
        log.debug('update_doc_mult(): update %s documents', len(docs))

        qual_ds_name = self._get_datastore_name(datastore_name)
        # Could use cur.executemany() here but does not allow for case-by-case reaction to failure
        with self.pool.cursor(**self.cursor_args) as cur:
            result_list = []
            for doc in docs:
                if "_deleted" in doc:
                    self._delete_doc(cur, qual_ds_name, doc["_id"])
                    oid, version = doc["_id"], doc["_rev"]
                else:
                    oid, version = self._update_doc(cur, qual_ds_name, doc)
                result_list.append((True, oid, version))

        return result_list

    def _update_doc(self, cur, table, doc):
        old_rev = int(doc["_rev"])
        doc["_rev"] = str(old_rev+1)
        doc_json = json.dumps(doc)

        extra_cols, table = self._get_extra_cols(doc, table, self.profile)

        statement_args = dict(doc=doc_json, id=doc["_id"], rev=old_rev, revn=old_rev+1)
        xval = ""
        if extra_cols:
            for col in extra_cols:
                insert_expr = self._create_value_expression(col, doc, col, statement_args, assign=True)
                if insert_expr:
                    xval += insert_expr

        cur.execute("UPDATE "+table+" SET doc=%(doc)s, rev=%(revn)s" + xval + " WHERE id=%(id)s AND rev=%(rev)s",
                    statement_args)
        if not cur.rowcount:
            # Distinguish rev conflict from documents does not exist.
            #try:
            #    self.read_doc(doc["_id"])
            #    raise Conflict("Object with id %s revision conflict" % doc["_id"])
            #except NotFound:
            #    raise
            raise Conflict("Object with id %s revision conflict" % doc["_id"])
        return doc["_id"], doc["_rev"]

    def _get_extra_cols(self, doc, table, profile):
        obj_type = self._get_obj_type(doc, profile)
        table_ext, extra_cols = OBJ_SPECIAL.get(obj_type, ("", tuple()))
        table += table_ext
        return extra_cols, table

    def _get_obj_type(self, doc, profile):
        """Returns the type of the given object based on datastore profile and inferrence from object"""
        obj_type = "O"
        if profile == DataStore.DS_PROFILE.RESOURCES:
            if doc.get("type_", None) == "Association":
                obj_type = "A"
            elif doc.get("type_", None) == "DirEntry":
                obj_type = "D"
            elif doc.get("type_", None):
                obj_type = "R"
        elif profile == DataStore.DS_PROFILE.DIRECTORY:
            if doc.get("type_", None) == "DirEntry":
                obj_type = "D"
        elif profile == DataStore.DS_PROFILE.EVENTS:
            if doc.get("origin", None):
                obj_type = "E"
        return obj_type

    def update_attachment(self, doc, attachment_name, data, content_type=None, datastore_name=""):
        if not isinstance(attachment_name, str):
            raise BadRequest("attachment name is not string")
        if not isinstance(data, str) and not isinstance(data, file):
            raise BadRequest("data to create attachment is not a str or file")

        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name + "_att"

        if isinstance(doc, str):
            doc_id = doc
        else:
            doc_id = doc['_id']
            self._assert_doc_rev(doc)

        statement_args = dict(docid=doc_id, rev=1, doc=buffer(data), name=attachment_name, content_type=content_type)
        with self.pool.cursor(**self.cursor_args) as cur:
            statement = "UPDATE " + table + " SET "+\
                        "rev=rev+1, doc=%(doc)s,  content_type=%(content_type)s "+ \
                        "WHERE docid=%(docid)s AND name=%(name)s"
            cur.execute(statement, statement_args)
            if not cur.rowcount:
                raise NotFound('Attachment %s for object with id %s does not exist.' % (attachment_name, doc_id))

    def read_doc(self, doc_id, rev_id=None, datastore_name=None, object_type=None):
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name

        if object_type == "Association":
            table = qual_ds_name + "_assoc"
        elif object_type == "DirEntry":
            table = qual_ds_name + "_dir"

        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute("SELECT doc FROM "+table+" WHERE id=%s", (doc_id,))
            doc_list = cur.fetchall()
            if not doc_list:
                raise NotFound('Object with id %s does not exist.' % doc_id)
            if len(doc_list) > 1:
                raise Inconsistent('Object with id %s has %s values.' % (doc_id, len(doc_list)))

            doc_json = doc_list[0][0]
            doc = doc_json

        return doc

    def _read_doc_rev(self, doc_id, datastore_name=None):
        qual_ds_name = self._get_datastore_name(datastore_name)

        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute("SELECT rev FROM "+qual_ds_name+" WHERE id=%s", (doc_id,))
            doc_list = cur.fetchall()
            if not doc_list:
                raise NotFound('Object with id %s does not exist.' % doc_id)

            rev = doc_list[0][0]

        return str(rev)

    def _assert_doc_rev(self, doc, datastore_name=None):
        rev = self._read_doc_rev(doc["_id"], datastore_name=datastore_name)
        if rev != doc["_rev"]:
            raise Conflict("Object with id %s revision conflict is=%s, need=%s" % (doc["_id"], rev, doc["_rev"]))

    def read_doc_mult(self, object_ids, datastore_name=None, object_type=None, strict=True):
        """"
        Fetch a number of raw doc instances, HEAD rev.
        """
        if not object_ids:
            return []
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name

        if object_type == "Association":
            table = qual_ds_name + "_assoc"
        elif object_type == "DirEntry":
            table = qual_ds_name + "_dir"

        query = "SELECT id, doc FROM "+table+" WHERE id IN ("
        query_args = dict()
        for i, oid in enumerate(object_ids):
            arg_name = "id" + str(i)
            if i>0:
                query += ","
            query += "%(" + arg_name + ")s"
            query_args[arg_name] = oid
        query += ")"

        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute(query, query_args)
            rows = cur.fetchall()

        doc_by_id = {row[0]: row[1] for row in rows}
        doc_list = [doc_by_id.get(oid, None) for oid in object_ids]
        if strict:
            notfound_list = ['Object with id %s does not exist.' % object_ids[i]
                             for i, doc in enumerate(doc_list) if doc is None]
            if notfound_list:
                raise NotFound("\n".join(notfound_list))
        return doc_list

    def read_attachment(self, doc, attachment_name, datastore_name=""):
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name + "_att"

        doc_id = doc if isinstance(doc, str) else doc['_id']
        statement_args = dict(docid=doc_id, name=attachment_name)

        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute("SELECT doc FROM "+table+" WHERE docid=%(docid)s AND name=%(name)s", statement_args)
            row = cur.fetchone()

        if not row:
            raise NotFound('Attachment %s does not exist in document %s.%s.',
                           attachment_name, datastore_name or qual_ds_name, doc_id)

        return str(row[0])

    def list_attachments(self, doc, datastore_name=""):
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name + "_att"

        doc_id = doc if isinstance(doc, str) else doc['_id']
        statement_args = dict(docid=doc_id)
        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute("SELECT name, content_type FROM "+table+" WHERE docid=%(docid)s", statement_args)
            rows = cur.fetchall()

        return [dict(name=row[0], content_type=row[1]) for row in rows]

    def delete_doc(self, doc, datastore_name=None, object_type=None, **kwargs):
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name
        doc_id = doc if isinstance(doc, str) else doc["_id"]
        log.debug('delete_doc(): Delete document id=%s object_type=%s', doc_id, object_type)
        if self.profile == DataStore.DS_PROFILE.DIRECTORY:
            table = qual_ds_name + "_dir"
        if object_type == "Association":
            table = qual_ds_name + "_assoc"
        elif object_type == "DirEntry":
            table = qual_ds_name + "_dir"

        with self.pool.cursor(**self.cursor_args) as cur:
            self._delete_doc(cur, table, doc_id)

    def delete_doc_mult(self, object_ids, datastore_name=None, object_type=None):
        if not object_ids:
            return []
        #log.debug('delete_doc_mult(): Delete %s documents', len(object_ids))
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name
        if self.profile == DataStore.DS_PROFILE.DIRECTORY:
            table = qual_ds_name + "_dir"
        if object_type == "Association":
            table = qual_ds_name + "_assoc"
        elif object_type == "DirEntry":
            table = qual_ds_name + "_dir"

        with self.pool.cursor(**self.cursor_args) as cur:
            for doc_id in object_ids:
                self._delete_doc(cur, table, doc_id)

    def _delete_doc(self, cur, table, doc_id):
        sql = "DELETE FROM "+table+" WHERE id=%s"
        cur.execute(sql, (doc_id, ))
        if not cur.rowcount:
            raise NotFound('Object with id %s does not exist.' % doc_id)

    def delete_attachment(self, doc, attachment_name, datastore_name=""):
        qual_ds_name = self._get_datastore_name(datastore_name)
        table = qual_ds_name + "_att"

        if isinstance(doc, str):
            doc_id = doc
        else:
            doc_id = doc['_id']
            self._assert_doc_rev(doc)

        statement_args = dict(docid=doc_id, name=attachment_name)
        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute("DELETE FROM "+table+" WHERE docid=%(docid)s AND name=%(name)s", statement_args)
            if not cur.rowcount:
                raise NotFound('Attachment %s does not exist in document %s.%s.',
                               attachment_name, datastore_name or qual_ds_name, doc_id)

    # -------------------------------------------------------------------------
    # View operations

    def define_profile_views(self, profile=None, datastore_name=None, keepviews=False):
        pass

    def refresh_views(self, datastore_name="", profile=None):
        pass

    def _get_view_args(self, all_args, access_args=None):
        view_args = {}
        if all_args:
            view_args.update(all_args)
        extra_clause = ""
        if "limit" in all_args and all_args['limit'] > 0:
            extra_clause += " LIMIT %s" % all_args['limit']
        if "skip" in all_args and all_args['skip'] > 0:
            extra_clause += " OFFSET %s " % all_args['skip']

        view_args['extra_clause'] = extra_clause
        if access_args:
            view_args.update(access_args)
        return view_args

    def find_docs_by_view(self, design_name, view_name, key=None, keys=None, start_key=None, end_key=None,
                          id_only=True, **kwargs):
        log.debug("find_docs_by_view() %s/%s, %s, %s, %s, %s, %s, %s", design_name, view_name, key, keys, start_key, end_key, id_only, kwargs)

        funcname = "_find_%s" % (design_name) if view_name else "_find_all_docs"
        if not hasattr(self, funcname):
            raise NotImplementedError()

        filter = self._get_view_args(kwargs)

        res_list = getattr(self, funcname)(key=key, view_name=view_name, keys=keys, start_key=start_key, end_key=end_key, id_only=id_only, filter=filter)
        log.debug("find_docs_by_view() found %s results", len(res_list))
        return res_list

    def _find_all_docs(self, view_name, key=None, keys=None, start_key=None, end_key=None,
                       id_only=True, filter=None):
        if view_name and view_name != "_all_docs":
            log.warn("Using _all_docs view instead of requested %s", view_name)

        qual_ds_name = self._get_datastore_name()
        dsn_res = qual_ds_name
        dsn_assoc = qual_ds_name + "_assoc"
        dsn_dir = qual_ds_name + "_dir"

        if id_only:
            query = "SELECT * FROM (SELECT id FROM "+dsn_res
            if self.profile == DataStore.DS_PROFILE.RESOURCES:
                query += " UNION ALL SELECT id FROM "+dsn_assoc
                query += " UNION ALL SELECT id FROM "+dsn_dir
            query += ") AS res"
        else:
            query = "SELECT * FROM (SELECT id, doc FROM "+dsn_res
            if self.profile == DataStore.DS_PROFILE.RESOURCES:
                query += " UNION ALL SELECT id, doc FROM "+dsn_assoc
                query += " UNION ALL SELECT id, doc FROM "+dsn_dir
            query += ") AS res"

        query_clause = ""
        query_args = dict(key=key, start=start_key, end=end_key)

        if key:
            query_clause += " WHERE id=%(key)s"
        elif keys:
            query_clause += " WHERE id IN ("
            for i, key in enumerate(keys):
                if i>0:
                    query_clause += ","
                keyname = "key"+str(i)
                query_clause += "%("+keyname+")s"
                query_args[keyname] = key
            query_clause += ")"
        elif start_key or end_key:
            raise NotImplementedError()

        extra_clause = filter.get("extra_clause", "")
        with self.pool.cursor(**self.cursor_args) as cur:
            #print query + query_clause + extra_clause, query_args
            cur.execute(query + query_clause + extra_clause, query_args)
            rows = cur.fetchall()

        if id_only:
            res_rows = [(self._prep_id(row[0]), [], None) for row in rows]
        else:
            res_rows = [(self._prep_id(row[0]), [], self._prep_doc(row[-1])) for row in rows]

        return res_rows

    def _find_directory(self, view_name, key=None, keys=None, start_key=None, end_key=None,
                        id_only=True, filter=None):
        qual_ds_name = self._get_datastore_name()
        table = qual_ds_name + "_dir"
        query = "SELECT id, org, parent, key, doc FROM " + table
        query_clause = " WHERE "
        query_args = dict(key=key, start=start_key, end=end_key)

        if view_name == "by_key" and key:
            org = key[0]
            entry = key[1]
            parent = key[2]
            query_args.update(dict(org=org, parent=parent, key=entry))
            query_clause += "org=%(org)s AND parent=%(parent)s AND key=%(key)s"
        elif view_name == "by_key" and start_key:
            org = start_key[0]
            entry = start_key[1]
            parent = start_key[2]
            query_args.update(dict(org=org, parent="%s%%" % parent, key=entry))
            query_clause += "org=%(org)s AND parent LIKE %(parent)s AND key=%(key)s"
        elif view_name == "by_attribute":
            org = start_key[0]
            attr_name = start_key[1]
            attr_value = start_key[2]
            parent = start_key[3]
            query_args.update(dict(org=org, parent="%s%%" % parent, att="attributes.%s" % attr_name, val=attr_value))
            query_clause += "org=%(org)s AND parent LIKE %(parent)s AND json_string(doc,%(att)s)=%(val)s"
        elif view_name == "by_parent":
            org = start_key[0]
            parent = start_key[1]
            entry = start_key[2]
            query_args.update(dict(org=org, parent=parent, key=entry))
            query_clause += "org=%(org)s AND parent=%(parent)s"
        elif view_name == "by_path":
            org = start_key[0]
            parent = "/" + "/".join(start_key[1])
            query_args.update(dict(org=org, parent="%s%%" % parent))
            query_clause += "org=%(org)s AND parent LIKE %(parent)s"
        else:
        # by parent, path, attribute, key
            raise NotImplementedError()

        extra_clause = filter.get("extra_clause", "")
        with self.pool.cursor(**self.cursor_args) as cur:
            #print query + query_clause + extra_clause, query_args
            cur.execute(query + query_clause + extra_clause, query_args)
            rows = cur.fetchall()

        #if view_name == "by_attribute":
        #    rows = [row for row in rows if row[2].startswith(start_key[3])]

        if id_only:
            res_rows = [(self._prep_id(row[0]), [], self._prep_doc(row[-1])) for row in rows]
        else:
            res_rows = [(self._prep_id(row[0]), [], self._prep_doc(row[-1])) for row in rows]

        return res_rows


    def _find_resource(self, view_name, key=None, keys=None, start_key=None, end_key=None,
                       id_only=True, filter=None):
        qual_ds_name = self._get_datastore_name()
        if id_only:
            query = "SELECT id, name, type_, lcstate FROM " + qual_ds_name
        else:
            query = "SELECT id, name, type_, lcstate, doc FROM " + qual_ds_name
        query_clause = " WHERE lcstate<>'DELETED' AND "
        query_args = dict(key=key, start=start_key, end=end_key)

        if view_name == "by_type":
            query_args['type_'] = start_key[0]
            query_clause += "type_=%(type_)s"
        else:
            raise NotImplementedError()

        extra_clause = filter.get("extra_clause", "")
        with self.pool.cursor(**self.cursor_args) as cur:
            cur.execute(query + query_clause + extra_clause, query_args)
            rows = cur.fetchall()

        if id_only:
            res_rows = [(self._prep_id(row[0]), [], None) for row in rows]
        else:
            res_rows = [(self._prep_id(row[0]), [], self._prep_doc(row[-1])) for row in rows]

        return res_rows

    def _find_attachment(self, view_name, key=None, keys=None, start_key=None, end_key=None,
                       id_only=True, filter=None):
        qual_ds_name = self._get_datastore_name()
        if id_only:
            query = "SELECT R.id, R.name, R.type_, R.lcstate, json_keywords(R.doc) FROM " + qual_ds_name + " AS R," + qual_ds_name + "_assoc AS A"
        else:
            query = "SELECT R.id, R.name, R.type_, R.lcstate, json_keywords(R.doc), R.doc FROM " + qual_ds_name + " AS R," + qual_ds_name + "_assoc AS A"
        query_clause = " WHERE R.id=A.o and A.p='hasAttachment' AND R.lcstate<>'DELETED' AND A.retired<>true "
        query_args = dict(key=key, start=start_key, end=end_key)
        order_clause = " ORDER BY R.ts_created"

        if view_name == "by_resource":
            res_id = start_key[0]
            if len(start_key) > 1:
                raise NotImplementedError()
            query_args['resid'] = res_id
            query_clause += "AND A.s=%(resid)s"
        else:
            raise NotImplementedError()

        if filter.get('descending', False):
            order_clause += " DESC"

        extra_clause = filter.get("extra_clause", "")
        with self.pool.cursor(**self.cursor_args) as cur:
            # print query + query_clause + order_clause + extra_clause, query_args
            cur.execute(query + query_clause + order_clause + extra_clause, query_args)
            rows = cur.fetchall()

        if id_only:
            res_rows = [(self._prep_id(row[0]), [None, None, row[4]], None) for row in rows]
        else:
            res_rows = [(self._prep_id(row[0]), [None, None, row[4]], self._prep_doc(row[-1])) for row in rows]

        return res_rows

    def _find_event(self, view_name, key=None, keys=None, start_key=None, end_key=None,
                    id_only=True, filter=None):
        qual_ds_name = self._get_datastore_name()
        if id_only:
            query = "SELECT id, ts_created FROM " + qual_ds_name
        else:
            query = "SELECT id, ts_created, doc FROM " + qual_ds_name
        query_clause = " WHERE "
        query_args = dict(key=key, start=start_key, end=end_key)
        order_clause = " ORDER BY ts_created"

        if view_name == "by_origintype":
            query_args['origin'] = start_key[0]
            query_args['type_'] = start_key[1]
            query_clause += "origin=%(origin)s AND type_=%(type_)s"
            if len(start_key) == 3:
                query_args['startts'] = start_key[2]
                query_clause += " AND ts_created>=%(startts)s"
            if len(end_key) == 3:
                query_args['endts'] = end_key[2]
                query_clause += " AND ts_created<=%(endts)s"
            order_clause = " ORDER BY origin, type_, ts_created"
        elif view_name == "by_origin":
            query_args['origin'] = start_key[0]
            query_clause += "origin=%(origin)s"
            if len(start_key) == 2:
                query_args['startts'] = start_key[1]
                query_clause += " AND ts_created>=%(startts)s"
            if len(end_key) == 2:
                query_args['endts'] = end_key[1]
                query_clause += " AND ts_created<=%(endts)s"
            order_clause = " ORDER BY origin, ts_created"
        elif view_name == "by_type":
            query_args['type_'] = start_key[0]
            query_clause += "type_=%(type_)s"
            if len(start_key) == 2:
                query_args['startts'] = start_key[1]
                query_clause += " AND ts_created>=%(startts)s"
            if len(end_key) == 2:
                query_args['endts'] = end_key[1]
                query_clause += " AND ts_created<=%(endts)s"
            order_clause = " ORDER BY type_, ts_created"
        elif view_name == "by_time":
            if start_key and end_key:
                query_args['startts'] = start_key[0]
                query_args['endts'] = end_key[0]
                query_clause += "ts_created BETWEEN %(startts)s AND %(endts)s"
            elif start_key:
                query_args['startts'] = start_key[0]
                query_clause += "ts_created>=%(startts)s"
            elif end_key:
                query_args['endts'] = end_key[0]
                query_clause += "ts_created<=%(endts)s"
            else:
                # Make sure the result set is not too long
                if filter.get("limit", 0) < 0:
                    filter["limit"] = 100
                    filter = self._get_view_args(filter)
        else:
            raise NotImplementedError()

        if filter.get('descending', False):
            order_clause += " DESC"

        if query_clause == " WHERE ":
            query_clause = " "
        extra_clause = filter.get("extra_clause", "")
        with self.pool.cursor(**self.cursor_args) as cur:
            sql = query + query_clause + order_clause + extra_clause
            #print "QUERY:", sql, query_args
            #print "filter:", filter
            cur.execute(sql, query_args)
            rows = cur.fetchall()

        if id_only:
            res_rows = [(self._prep_id(row[0]), [], row[1]) for row in rows]
        else:
            res_rows = [(self._prep_id(row[0]), [], self._prep_doc(row[-1])) for row in rows]

        return res_rows

    def get_unique_id(self):
        return uuid4().hex

    def _prep_id(self, internal_id):
        return internal_id.replace("-", "")

    def _prep_doc(self, internal_doc):
        # With latest psycopg2, this is not necessary anymore and can be removed
        if internal_doc is None:
            return None
        doc = internal_doc
        return doc
