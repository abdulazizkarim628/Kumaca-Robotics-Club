from django.db import models
from django.db.models.fields import TextField
from uuid import uuid4
from .utils import get_read_time, count_words
from taggit.managers import TaggableManager
from accounts.models import Author
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(blank=True, null=True)
    image = models.ImageField(default='category-default.jpg',
                              upload_to='category_images')
    approved = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.slug = f'{slugify(self.name, allow_unicode=True)}'
        super(Category, self).save(*args, **kwargs)


class Post(models.Model):
    DRAFTED = "DRAFTED"
    PUBLISHED = "PUBLISHED"

    # CHOICES
    STATUS_CHOICES = (
        (DRAFTED, 'Draft'),
        (PUBLISHED, 'Publish'),
    )

    title = models.CharField(max_length=255, default='', unique=False)
    overview = models.TextField(help_text="Briefly describe the post", max_length=200, blank=True, null=True)
    tags = TaggableManager(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='DRAFT')
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name='posts')
    # related name for author is needed to use author.posts in template for posts posted by author
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    content = RichTextUploadingField()
    image = models.ImageField(upload_to='post_images', blank=False)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    count_words = models.PositiveBigIntegerField(default=0)
    read_time = models.PositiveBigIntegerField(default=0)
    slug = models.SlugField(blank=True, null=True)
    views = models.ManyToManyField(
        User, related_name='views', blank=True)
    deleted = models.BooleanField(default=False)
    date_published = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = f'{slugify(self.title, allow_unicode=True)}-{str(uuid4())[:3]}'
        self.title = str(self.title).title()
        self.read_time = get_read_time(self.content)
        self.count_words = count_words(self.content)

        super(Post, self).save(*args, **kwargs)

    def total_views(self):
        return self.views.count()

    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        c = Comment.objects.filter(post=self, author=self.author)
        t = 0
        for i in c:
            t += i.replies.count()
        return t + c.count()
            
    class Meta:
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.title


class Comment(models.Model):

    author = models.ForeignKey(Author, default='', on_delete=models.CASCADE)
    date_commented = models.DateTimeField(auto_now=True)
    content = models.TextField()
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self):
        return self.author.user.username + f'\'s comment on {self.post.title}'


class Reply(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(Author, null=True, on_delete=models.CASCADE)
    content = TextField()
    replied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'reply'
        verbose_name_plural = 'replies'

    def __str__(self):
        return f"{self.comment} | { self.author } |{ self.replied_at }"


class Subscribers(models.Model):

    email = models.EmailField('Email', max_length=254)
    date_subscribed = models.DateTimeField("Date subscribed", auto_now=True)

    class Meta:
        verbose_name = "subscriber"
        verbose_name_plural = "subscribers"

    def __str__(self):
        return self.email


class Video(models.Model):
    video_url = models.URLField(help_text='Video\'s url')
    description = models.TextField(max_length=100)

    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'

    def __str__(self):
        return self.video_url
