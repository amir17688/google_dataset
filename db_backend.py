from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from completion.backends.base import BaseBackend
from completion.models import AutocompleteObject
from completion.utils import clean_phrase, create_key, partial_complete


class DatabaseAutocomplete(BaseBackend):
    def flush(self):
        AutocompleteObject.objects.all().delete()
    
    def store_object(self, obj, data):
        """
        Given a title & some data that needs to be stored, make it available
        for autocomplete via the suggest() method
        """
        self.remove_object(obj, data)
        
        title = data['title']
        for partial_title in partial_complete(title):
            key = create_key(partial_title)
            autocomplete_obj = AutocompleteObject(
                title=key,
                object_id=obj.pk,
                content_type=ContentType.objects.get_for_model(obj),
                pub_date=data['pub_date'],
                data=data['data']
            )
            autocomplete_obj.save()
            autocomplete_obj.sites = data['sites']
    
    def remove_object(self, obj, data):
        AutocompleteObject.objects.for_object(obj).delete()
    
    def suggest(self, phrase, limit, models):
        phrase = create_key(phrase)
        if not phrase:
            return []
        
        query = dict(
            title__startswith=phrase,
            sites__pk__exact=settings.SITE_ID,
        )
        
        if models is not None:
            query.update(content_type__in=[
                ContentType.objects.get_for_model(model_class) \
                    for model_class in models
            ])
        
        qs = AutocompleteObject.objects.filter(
            **query
        ).values_list('data', flat=True).distinct()
        
        if limit is not None:
            qs = qs[:limit]
        
        return qs
