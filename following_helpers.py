from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def following(request, offer):
    if not request.user.is_authenticated():
        return ""

    total_followers = offer.followers.count()

    badge = ""
    if total_followers:
        badge = ' <span class="badge">{0}</span>'.format(total_followers)

    if not offer.followers.filter(pk=request.user.pk).exists():
        return '<a class="btn btn-success" href="%s">Follow%s</a>' % (offer.get_absolute_url() + '?do=follow', badge)

    return '<a class="btn btn-warning" href="%s">Unfollow%s</a>' % (offer.get_absolute_url() + '?do=unfollow', badge)
