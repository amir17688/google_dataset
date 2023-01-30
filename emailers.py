from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from offers.tasks import (
    send_comment_mail,
    send_new_comment_followers_mail,
    send_comment_like,
    send_comment_unlike,
)


def send_simple_mail(subject, message_template, message_plain_template, context, to):

    if settings.SITE_URL.endswith('/'):
        site_url = 'http://' + settings.SITE_URL[:-1]
    else:
        site_url = 'http://' + settings.SITE_URL

    context.update({"site_url": site_url})

    message = render_to_string(message_template, context)
    message_plain = render_to_string(message_plain_template, context)

    msg = EmailMultiAlternatives(
        subject,
        message_plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to]
    )
    msg.attach_alternative(
        message,
        "text/html"
    )
    msg.send()


def send_comment_reply(comment):
    if not comment.is_reply():
        return

    send_comment_mail.delay(comment.pk)


def send_comment_new(comment, user):
    user_pk = None
    if user.is_authenticated():
        user_pk = user.pk
    send_new_comment_followers_mail.delay(comment.pk, user_pk)


def send_comment_liked(like):
    if like.pk is None:
        return

    send_comment_like.delay(like.pk)


def send_comment_unliked(comment, liker_name):
    send_comment_unlike.delay(comment.pk, liker_name)
