from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.enums import Choices
from django_countries.fields import CountryField
from django.core.cache import cache


# Create your models here.

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures', default='profile_pictures/profile_rr3sky.png')
    bio = models.TextField(max_length="101", blank=True, null=True)
    facebook_page = models.URLField(default=f'http://www.facebook.com/', blank=True, null=True)
    instagram_page = models.URLField(default='http://www.instagram.com/', blank=True, null=True)
    twitter_page = models.URLField(default='http://www.twitter.com/',blank=True, null=True)
    personal_website = models.URLField(default='  ',blank=True, null=True)
    whatsapp_link = models.URLField(default='http://www.wa.me/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True, max_length=255)
    gender = models.CharField(max_length=255, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    country = CountryField(blank_label='(select country)')
    workplace= models.CharField(max_length=200, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    saved_posts = models.ManyToManyField(to="blog.Post", related_name='saved_posts', blank=True)
    
    def save(self, *args, **kwargs):
        if not self.profile_picture:
            self.profile_picture = models.ImageField(upload_to='profile_pictures', default='profile_pictures/profile_rr3sky.png')
        
        super(Author, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'author'
        verbose_name_plural = 'authors'
    
    def __str__(self):
        return self.user.get_username()

class Action(models.Model):
    action_levels = [('danger', 'danger'), ('success', 'success'),('info', 'info'), ('warning', 'warning')]

    author = models.ForeignKey(
        User, default='', on_delete=models.CASCADE, related_name='actions')
    activity = models.CharField(max_length=255)
    activity_date = models.DateTimeField(auto_now_add=True)
    level = models.CharField(default='info', blank=True, max_length=255, choices=action_levels)

    class Meta:
        verbose_name = 'action'
        verbose_name_plural = 'actions'
    
    def __str__(self):
        return f'{self.author}: {self.activity}'