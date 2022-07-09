# Third-party library imports
from django import template

register = template.Library()


@register.filter
def justnow(post):
    if post.date_published:
        return post.date_published
        