from django import template

register = template.Library()


@register.filter
def remove_hashtag(tag_name):
    tag_name = str(tag_name).replace('#', '')
    return tag_name.capitalize()
