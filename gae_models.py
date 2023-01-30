# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Models relating to the per-exploration file system."""

from core.platform import models
import feconf
import utils

from google.appengine.ext import ndb

(base_models,) = models.Registry.import_models([models.NAMES.base_model])


class FileMetadataSnapshotMetadataModel(base_models.BaseSnapshotMetadataModel):
    """Class for storing the file metadata snapshot commit history."""
    pass


class FileMetadataSnapshotContentModel(base_models.BaseSnapshotContentModel):
    """Class for storing the content of the file metadata snapshots."""
    pass


class FileMetadataModel(base_models.VersionedModel):
    """File metadata model, keyed by exploration id and absolute file name."""
    SNAPSHOT_METADATA_CLASS = FileMetadataSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = FileMetadataSnapshotContentModel

    # The size of the file.
    size = ndb.IntegerProperty(indexed=False)

    @classmethod
    def get_new_id(cls, entity_name):
        raise NotImplementedError

    @classmethod
    def get_undeleted(cls):
        return cls.get_all().filter(cls.deleted == False).fetch(  # pylint: disable=singleton-comparison
            feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def _construct_id(cls, exploration_id, filepath):
        return utils.vfs_construct_path('/', exploration_id, filepath)

    @classmethod
    def create(cls, exploration_id, filepath):
        model_id = cls._construct_id(exploration_id, filepath)
        return cls(id=model_id, deleted=False)

    @classmethod
    def get_model(cls, exploration_id, filepath, strict=False):
        model_id = cls._construct_id(exploration_id, filepath)
        return super(FileMetadataModel, cls).get(model_id, strict=strict)

    @classmethod
    def get_version(cls, exploration_id, filepath, version_number):
        model_id = cls._construct_id(exploration_id, filepath)
        return super(FileMetadataModel, cls).get_version(
            model_id, version_number)

    def commit(self, committer_id, commit_cmds):
        return super(FileMetadataModel, self).commit(
            committer_id, '', commit_cmds)


class FileSnapshotMetadataModel(base_models.BaseSnapshotMetadataModel):
    """Class for storing the file snapshot commit history."""
    pass


class FileSnapshotContentModel(base_models.BaseSnapshotContentModel):
    """Class for storing the content of the file snapshots."""

    # Overwrite the superclass member to use a BlobProperty for raw strings.
    content = ndb.BlobProperty(indexed=False)


class FileModel(base_models.VersionedModel):
    """File data model, keyed by exploration id and absolute file name."""
    SNAPSHOT_METADATA_CLASS = FileSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = FileSnapshotContentModel

    # The contents of the file.
    content = ndb.BlobProperty(indexed=False)

    def _reconstitute(self, snapshot_blob):
        """Manually overwrite the superclass method."""
        self.content = snapshot_blob
        return self

    def _compute_snapshot(self):
        """Manually overwrite the superclass method."""
        return self.content

    @classmethod
    def get_new_id(cls, entity_name):
        raise NotImplementedError

    @classmethod
    def _construct_id(cls, exploration_id, filepath):
        return utils.vfs_construct_path('/', exploration_id, filepath)

    @classmethod
    def create(cls, exploration_id, filepath):
        model_id = cls._construct_id(exploration_id, filepath)
        return cls(id=model_id, deleted=False)

    @classmethod
    def get_model(cls, exploration_id, filepath, strict=False):
        model_id = cls._construct_id(exploration_id, filepath)
        return super(FileModel, cls).get(model_id, strict=strict)

    def commit(self, committer_id, commit_cmds):
        return super(FileModel, self).commit(committer_id, '', commit_cmds)

    @classmethod
    def get_version(cls, exploration_id, filepath, version_number):
        model_id = cls._construct_id(exploration_id, filepath)
        return super(FileModel, cls).get_version(model_id, version_number)
del in the form of
    #   [EXPLORATION_ID].[THREAD_ID]
    thread_id = ndb.StringProperty(required=True, indexed=True)
    # 0-based sequential numerical ID. Sorting by this field will create the
    # thread in chronological order.
    message_id = ndb.IntegerProperty(required=True, indexed=True)
    # ID of the user who posted this message. This may be None if the feedback
    # was given anonymously by a learner.
    author_id = ndb.StringProperty(indexed=True)
    # New thread status. Must exist in the first message of a thread. For the
    # rest of the thread, should exist only when the status changes.
    updated_status = ndb.StringProperty(choices=STATUS_CHOICES, indexed=True)
    # New thread subject. Must exist in the first message of a thread. For the
    # rest of the thread, should exist only when the subject changes.
    updated_subject = ndb.StringProperty(indexed=False)
    # Message text. Allowed not to exist (e.g. post only to update the status).
    text = ndb.StringProperty(indexed=False)

    @classmethod
    def _generate_id(cls, exploration_id, thread_id, message_id):
        return '.'.join([exploration_id, thread_id, str(message_id)])

    @property
    def exploration_id(self):
        return self.id.split('.')[0]

    def get_thread_subject(self):
        return FeedbackThreadModel.get_by_id(self.thread_id).subject

    @classmethod
    def create(cls, exploration_id, thread_id, message_id):
        """Creates a new FeedbackMessageModel entry.

        Throws an exception if a message with the given thread ID and message
        ID combination exists already.
        """
        instance_id = cls._generate_id(
            exploration_id, thread_id, message_id)
        if cls.get_by_id(instance_id):
            raise Exception('Feedback message ID conflict on create.')
        return cls(id=instance_id)

    @classmethod
    def get(cls, exploration_id, thread_id, message_id, strict=True):
        """Gets the FeedbackMessageModel entry for the given ID.

        If the message id is valid and it is not marked as deleted, returns the
        message instance. Otherwise:
        - if strict is True, raises EntityNotFoundError
        - if strict is False, returns None.
        """
        instance_id = cls._generate_id(exploration_id, thread_id, message_id)
        return super(FeedbackMessageModel, cls).get(instance_id, strict=strict)

    @classmethod
    def get_messages(cls, exploration_id, thread_id):
        """Returns an array of messages in the thread.

        Does not include the deleted entries.
        """
        full_thread_id = FeedbackThreadModel.generate_full_thread_id(
            exploration_id, thread_id)
        return cls.get_all().filter(
            cls.thread_id == full_thread_id).fetch(feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_most_recent_message(cls, exploration_id, thread_id):
        full_thread_id = FeedbackThreadModel.generate_full_thread_id(
            exploration_id, thread_id)
        return cls.get_all().filter(
            cls.thread_id == full_thread_id).order(-cls.last_updated).get()

    @classmethod
    def get_message_count(cls, exploration_id, thread_id):
        """Returns the number of messages in the thread.

        Includes the deleted entries.
        """
        full_thread_id = FeedbackThreadModel.generate_full_thread_id(
            exploration_id, thread_id)
        return cls.get_all(include_deleted_entities=True).filter(
            cls.thread_id == full_thread_id).count()

    @classmethod
    def get_all_messages(cls, page_size, urlsafe_start_cursor):
        return cls._fetch_page_sorted_by_last_updated(
            cls.query(), page_size, urlsafe_start_cursor)


class FeedbackAnalyticsModel(base_models.BaseMapReduceBatchResultsModel):
    """Model for storing feedback thread analytics for an exploration.

    The key of each instance is the exploration id.
    """
    # The number of open feedback threads filed against this exploration.
    num_open_threads = ndb.IntegerProperty(default=None, indexed=True)
    # Total number of feedback threads filed against this exploration.
    num_total_threads = ndb.IntegerProperty(default=None, indexed=True)

    @classmethod
    def create(cls, model_id, num_open_threads, num_total_threads):
        """Creates a new FeedbackAnalyticsModel entry."""
        cls(
            id=model_id,
            num_open_threads=num_open_threads,
            num_total_threads=num_total_threads
        ).put()


class SuggestionModel(base_models.BaseModel):
    """Suggestions made by learners.

    The id of each instance is the id of the corresponding thread.
    """

    # ID of the user who submitted the suggestion.
    author_id = ndb.StringProperty(required=True, indexed=True)
    # ID of the corresponding exploration.
    exploration_id = ndb.StringProperty(required=True, indexed=True)
    # The exploration version for which the suggestion was made.
    exploration_version = ndb.IntegerProperty(required=True, indexed=True)
    # Name of the corresponding state.
    state_name = ndb.StringProperty(required=True, indexed=True)
    # Learner-provided description of suggestion changes.
    description = ndb.TextProperty(required=True, indexed=False)
    # The state's content after the suggested edits.
    # Contains keys 'type' (always 'text') and 'value' (the actual content).
    state_content = ndb.JsonProperty(required=True, indexed=False)

    @classmethod
    def create(cls, exploration_id, thread_id, author_id, exploration_version,
               state_name, description, state_content):
        """Creates a new SuggestionModel entry.

        Throws an exception if a suggestion with the given thread id already
        exists.
        """
        instance_id = cls._get_instance_id(exploration_id, thread_id)
        if cls.get_by_id(instance_id):
            raise Exception('There is already a feedback thread with the given '
                            'thread id: %s' % instance_id)
        cls(id=instance_id, author_id=author_id,
            exploration_id=exploration_id,
            exploration_version=exploration_version,
            state_name=state_name,
            description=description,
            state_content=state_content).put()

    @classmethod
    def _get_instance_id(cls, exploration_id, thread_id):
        return '.'.join([exploration_id, thread_id])

    @classmethod
    def get_by_exploration_and_thread_id(cls, exploration_id, thread_id):
        """Gets a suggestion by the corresponding exploration and thread id's.

        Returns None if it doesn't match anything."""

        return cls.get_by_id(cls._get_instance_id(exploration_id, thread_id))
