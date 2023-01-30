from django.contrib.auth.models import User

from completion.backends.redis_backend import RedisAutocomplete
from completion.completion_tests.base import AutocompleteTestCase, AutocompleteBackendTestCase
from completion.completion_tests.models import Blog, Note1, Note2, Note3, BlogProvider, NoteProvider
from completion.sites import AutocompleteSite


test_site = AutocompleteSite(RedisAutocomplete(prefix='test:ac:'))
test_site.register(Blog, BlogProvider)
test_site.register(Note1, NoteProvider)
test_site.register(Note2, NoteProvider)
test_site.register(Note3, NoteProvider)


class RedisBackendTestCase(AutocompleteTestCase, AutocompleteBackendTestCase):
    def setUp(self):
        self.test_site = test_site
        AutocompleteTestCase.setUp(self)
        test_site.flush()
    
    def test_removing_objects_in_depth(self):
        # want to ensure that redis is cleaned up and does not become polluted
        # with spurious keys when objects are removed
        backend = test_site.backend
        redis_client = backend.client
        prefix = backend.prefix
        
        # store the blog "testing python"
        test_site.store_object(self.blog_tp)
        
        # see how many keys we have in the db - check again in a bit
        key_len = len(redis_client.keys())
        
        # make sure that the final item in our sorted set indicates such
        values = redis_client.zrange('%stestingpython' % prefix, 0, -1)
        self.assertEqual(values, [backend.terminator])

        test_site.store_object(self.blog_tpc)
        key_len2 = len(redis_client.keys())
        
        self.assertTrue(key_len != key_len2)
        
        # check to see that the final item in the sorted set from earlier now
        # includes a reference to 'c'
        values = redis_client.zrange('%stestingpython' % prefix, 0, -1)
        self.assertEqual(values, [backend.terminator, 'c'])
        
        test_site.remove_object(self.blog_tpc)
        
        # see that the reference to 'c' is removed so that we aren't following
        # a path that no longer exists
        values = redis_client.zrange('%stestingpython' % prefix, 0, -1)
        self.assertEqual(values, [backend.terminator])
        
        # back to the original amount of keys
        self.assertEqual(len(redis_client.keys()), key_len)
