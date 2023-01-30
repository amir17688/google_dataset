from django import template
from django.contrib.sites.models import Site

register = template.Library()


@register.simple_tag
def make_absolute_url(url):
    current_site = Site.objects.get_current()

    return "http://%s%s" % (current_site.domain, url)
