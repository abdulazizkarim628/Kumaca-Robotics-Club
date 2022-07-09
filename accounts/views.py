from datetime import time
from functools import reduce
from django.http import request
from django.shortcuts import get_object_or_404, render, redirect, HttpResponseRedirect, reverse
from django.contrib.auth.models import User
from pkg_resources import require
from django.contrib.auth.forms import PasswordChangeForm
from . models import Author, Action
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .forms import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import operator
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    UpdateView,

    )
from blog.models import Post
import random


class ClearView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        obj = kwargs.get('obj')
        if obj == 'deleted_posts':

            deleted_posts = Post.objects.filter(author=request.user.author,
                                               deleted=True)
            deleted_posts.delete()
            messages.warning(request, message='Deleted posts have been cleared permanently')

            activity = Action(author=request.user, activity='Deleted posts were permanently cleared', level='danger')
            activity.save()
            return redirect('accounts:deleted_posts')
        elif obj == 'activitylog':

            Action.objects.filter(author=request.user).delete()
            messages.warning(request, message='Activity Log has been cleared successfully')
            return redirect('accounts:activitylog')

def ChangePasswordView(request):
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJLKMNOPQRSTUVWXYZ'

    numbers = '0123456789'
    symbols = '(){}/;[]. '

    all = lower + upper + numbers + symbols

    length = 16

    suggestion = ''.join(random.sample(all, length))
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            activity = Action(author=request.user, activity='Password successfully was changed', level='success')
            activity.save()

            return redirect(to='accounts:profile', author = request.user)
        else:
            messages.error(request, 'Please correct the error below.')
    else:

        form = PasswordChangeForm(request.user)

    return render(request, 'registration/changepassword.html', {
        'form': form,
        'suggestion': suggestion
    })
    


@csrf_exempt
def SignupForm(request):
    if request.user.is_authenticated:
        messages.info(request, f'Dear {request.user} you have already logged in with an account')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            author = Author(user=user)
            author.save() 
            messages.success(request, 'Your account has been created successfully')
            activity = Action(author=user, activity='Joined Kumaca Robotics Club', level='success')
            activity.save()    
            return redirect('accounts:dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def AuthorProfileUpdateView(request):
    u_form = UserUpdateForm(data=request.POST, instance=request.user)
    a_form = AuthorUpdateForm(data=request.POST, files=request.FILES, instance=request.user.author)
    
    if request.method == 'POST':
        if a_form.is_valid() and u_form.is_valid():
            a_form.save()
            u_form.save()
            messages.success(request, 'Your account has been updated successfully')

            activity = Action(
                author=request.user, activity='Your profile was updated', level='success')
            activity.save()
            return redirect('accounts:profile', author=request.user.author)
    else:
        a_form = AuthorUpdateForm(instance=request.user.author)
        u_form = UserUpdateForm(instance=request.user)
    return render(request, 'dashboard/author_profile_update.html', {'u_form': u_form, 'a_form': a_form})



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "dashboard/post_create.html"
    form_class = PostForm
    SAVE_AS_DRAFT = "SAVE_AS_DRAFT"
    PUBLISH = "PUBLISH"

    def form_valid(self, form):

        form.instance.author = Author.objects.filter(
            user=self.request.user).first()
        
        action = self.request.POST.get("action")

        if action == self.SAVE_AS_DRAFT:
            form.instance.status = Post.DRAFTED
            form.instance.date_published = None    
            form.save()
            messages.success(self.request, f"Post drafted successfully.")
            activity = Action(author=self.request.user, activity='The post "%s" was  created and drafted' % (
                form.cleaned_data.get('title')), level='warning')
            activity.save()
            return redirect(to='accounts:drafted_posts')
        
        if action == self.PUBLISH:
            form.instance.status = Post.PUBLISHED
            form.instance.date_published = timezone.now()
            form.save()
            activity = Action(author=self.request.user, activity='The post "%s" was  created and published'%(form.cleaned_data.get('title')), level='success')
            activity.save()
            messages.success(self.request, f"Post published successfully.")
            return redirect(reverse("accounts:dashboard_post_detail", kwargs={"slug": form.instance.slug}))


class PostDeleteView(LoginRequiredMixin, View):
    """
      Deletes posts
    """

    def get(self, *args, **kwargs):
    
        post = get_object_or_404(Post, slug=self.kwargs.get("slug"), author=self.request.user.author)

        if not self.request.user.username == post.author.user.username:

            messages.error(request=self.request, message="You do not have permission to delete this post")
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))

        post.deleted = True
        post.save()

        activity = Action(author=self.request.user, activity='"%s" was deleted'%(post.title), level='warning')
        activity.save()
        
        messages.success(request=self.request, message=f'"{post.title}" was deleted successfully')

        return redirect(to='accounts:deleted_posts')


class ActivityLogView(LoginRequiredMixin, View):
    def get(self, request):
        template_name = 'dashboard/activitylog.html'
        context_object = {}

        actions = Action.objects.filter(author=request.user).order_by('-id')
        context_object['actions'] = actions

        return render(request, template_name, context_object)


class AuthorDeletedPostsView(LoginRequiredMixin, View):
    """
       Displays deleted articles by an author.
    """

    def get(self, request):
        """
           Returns deleted articles by an author.
        """
        template_name = 'dashboard/author_deleted_posts_list.html'
        context_object = {}

        deleted_articles = Post.objects.filter(author=request.user.author,
                                                  deleted=True).order_by('-date_published')
        total_articles_deleted = len(deleted_articles)

        page = request.GET.get('page', 1)

        paginator = Paginator(deleted_articles, 5)
        try:
            deleted_articles_list = paginator.page(page)
        except PageNotAnInteger:
            deleted_articles_list = paginator.page(1)
        except EmptyPage:
            deleted_articles_list = paginator.page(paginator.num_pages)

        context_object['deleted_articles_list'] = deleted_articles_list
        context_object['total_articles_deleted'] = total_articles_deleted
        
        return render(request, template_name, context_object)





class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "dashboard/post_update.html"
    form_class = PostForm

    SAVE_AS_DRAFT = "SAVE_AS_DRAFT"
    PUBLISH = "PUBLISH"

    def form_valid(self, form):
        

        if form.instance.author == self.request.user.author:
            action = self.request.POST.get("action")
            form.instance.date_updated = timezone.now

            if action == self.SAVE_AS_DRAFT:
                form.instance.status = Post.DRAFTED
                form.save()

                activity = Action(author=self.request.user, activity='The post "%s" was updated and drafted' % (
                    form.cleaned_data.get('title')), level='warning')
                activity.save()

                messages.success(self.request, 'Post drafted successfully')
                return redirect(to='accounts:drafted_posts')

            if action == self.PUBLISH:
                form.instance.status = Post.PUBLISHED
                if form.instance.date_published is None:
                    form.instance.date_published = timezone.now()
                form.save()
                

                activity = Action(author=self.request.user, activity='The post "%s" was updated and published' % (
                    form.cleaned_data.get('title')), level='success')
                activity.save()
                messages.success(self.request, f"'{form.instance.title}' is successfully updated.")
                return redirect(reverse("accounts:dashboard_post_detail", kwargs={"slug": form.instance.slug}))
            
        else:
            messages.warning(self.request, message='You do not have permission to edit the post')
            return redirect('accounts:saved_posts')

class AuthorPublishedPostsView(LoginRequiredMixin, View):
    """
       Displays published articles by an author.
    """

    def get(self, request):
        """
           Returns published articles by an author.
        """
        template_name = 'dashboard/author_published_posts_list.html'
        context_object = {}

        published_articles = Post.objects.filter(author=request.user.author,
                                                    status=Post.PUBLISHED, deleted=False).order_by('-date_published')
        total_articles_published = len(published_articles)

        page = request.GET.get('page', 1)

        paginator = Paginator(published_articles, 5)
        try:
            published_articles_list = paginator.page(page)
        except PageNotAnInteger:
            published_articles_list = paginator.page(1)
        except EmptyPage:
            published_articles_list = paginator.page(paginator.num_pages)

        context_object['published_articles_list'] = published_articles_list
        context_object['total_articles_published'] = total_articles_published

        return render(request, template_name, context_object)

class AuthorPostsView(LoginRequiredMixin, View):
    """
       Displays all articles written by an author.
    """

    def get(self, request):
        """
           Returns all articles written by an author.
        """
        template_name = 'dashboard/author_posts_list.html'
        context_object = {}

        written_articles = Post.objects.filter(
            author=request.user.author, deleted=False).order_by('-date_created')
        total_articles_written = len(written_articles)

        page = request.GET.get('page', 1)

        paginator = Paginator(written_articles, 5)
        try:
            written_articles_list = paginator.page(page)
        except PageNotAnInteger:
            written_articles_list = paginator.page(1)
        except EmptyPage:
            written_articles_list = paginator.page(paginator.num_pages)

        context_object['written_articles_list'] = written_articles_list
        context_object['total_articles_written'] = total_articles_written

        return render(request, template_name, context_object)


class DashboardPostDetailView(LoginRequiredMixin, View):
    """
       Displays article details.
    """

    def get(self, request, *args, **kwargs):
        """
           Returns article details.
        """
        template_name = 'dashboard/dashboard_post_detail.html'
        context_object = {}

        post = get_object_or_404(Post, slug=self.kwargs.get("slug"))
        if not post.views.filter(id=request.user.id).exists():
            post.views.add(request.user)

        context_object['article_title'] = post.title
        context_object['article'] = post

        return render(request, template_name, context_object)


class AuthorDraftedPostsView(LoginRequiredMixin, View):
    """
       Displays drafted Posts by an author.
    """

    def get(self, request):
        """
           Returns drafted Posts by an author.
        """
        template_name = 'dashboard/author_drafted_posts_list.html'
        context_object = {}

        drafted_articles = Post.objects.filter(author=request.user.author,
                                                  status=Post.DRAFTED, deleted=False).order_by('-date_created')
        total_articles_drafted = len(drafted_articles)

        page = request.GET.get('page', 1)

        paginator = Paginator(drafted_articles, 5)
        try:
            drafted_articles_list = paginator.page(page)
        except PageNotAnInteger:
            drafted_articles_list = paginator.page(1)
        except EmptyPage:
            drafted_articles_list = paginator.page(paginator.num_pages)

        context_object['drafted_articles_list'] = drafted_articles_list
        context_object['total_articles_drafted'] = total_articles_drafted

        return render(request, template_name, context_object)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Dear {name} you have already logged in'.format(name=self.request.user))
            return redirect('accounts:dashboard')
        return render(request, 'registration/login.html')

    def post(self, request,*args,**kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(request, f'Welcome back {str(request.user).title()}')
            messages.success(request, f'Explore our beautiful admin dashboard')

            activity = Action(author=self.request.user, activity='You logged in', level='info')
            activity.save()
            return redirect(self.request.GET.get('next') if self.request.GET.get('next') else 'accounts:dashboard')

        else:
            messages.warning(request, 'Username or password didn\'t match')
            return redirect('accounts:login')

# Logout View
class LogoutView(LoginRequiredMixin, View):
    def get(self,request,*args,**kwargs):
        activity = Action(author=self.request.user, activity='You logged out', level='info')
        activity.save()
        logout(request)

        messages.success(request, 'You have logged out of your account')
        return redirect('blog:home')



class DashboardHomeView(LoginRequiredMixin, View):
    """
    Display homepage of the dashboard.
    """
    context = {}
    template_name = 'dashboard/index.html'

    def get(self, request, *args, **kwargs):
        posts_list = Post.objects.filter(author__user=request.user, deleted=False, status=Post.PUBLISHED).order_by('-date_published')
        popular_authors = Author.objects.all()
        
        actions = Action.objects.filter(author=request.user).order_by('-id')
        if actions.count() > 20:
            a = actions[:20]
            for i in a:
                i.delete()
        total_posts_comments = sum(article.total_comments() for article in posts_list)
        total_posts_published = len(posts_list)
        total_posts_views = sum(article.total_views() for article in posts_list)
        total_posts_likes = sum(article.total_likes() for article in posts_list)
        # total_posts_comments = sum(post.comments.count() for post in posts_list)

        recent_published_posts_list = posts_list.order_by("-date_created")[:6]
        authors_arround = Author.objects.all().filter(country=request.user.author.country).exclude(user__author=request.user.author)
        self.context['popular_authors'] = popular_authors[:5]
        self.context['total_posts_comments'] = total_posts_comments
        self.context['total_posts_published'] = total_posts_published
        self.context['total_posts_views'] = total_posts_views
        self.context['total_posts_likes'] = total_posts_likes
        self.context['recent_activities'] = Action.objects.filter(author=request.user).order_by('-id')[:5]
        self.context['all_activities'] = Action.objects.all().filter(author=request.user)
        self.context['authors_arround'] = authors_arround.order_by('-id')[:11]
        # self.context['total_posts_comments'] = total_posts_comment
        self.context['recent_published_posts_list'] = recent_published_posts_list

        return render(request, self.template_name, self.context)


class SavedPostsView(LoginRequiredMixin, View):
    """Displays saved posts"""
    context = {}
    def get(self, request):
        saved_posts = request.user.author.saved_posts.all()
        page = request.GET.get('page', 1)

        paginator = Paginator(saved_posts, 5)
        try:
            saved_posts = paginator.page(page)
        except PageNotAnInteger:
            saved_posts = paginator.page(1)
        except EmptyPage:
            saved_posts = paginator.page(paginator.num_pages)
        self.context['saved_posts'] = saved_posts

        return render(request, "dashboard/author_saved_posts.html", self.context)

class SearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search = request.GET['q']
        authors = Author.objects.filter(
            reduce(operator.and_,(Q(user__username__icontains=q) for q in search.split())) |
            reduce(operator.and_,(Q(user__author__bio__icontains=q) for q in search.split()))
        ).exclude(user__username=request.user)
        return render(request, 'dashboard/search.html', context={'authors':authors, 'q':search})


class PostDraftView(LoginRequiredMixin, View):
    """
       View to draft a published post
    """

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'), author=self.request.user.author)
        post.status = Post.DRAFTED

        if not post.author == self.request.user.author:
            messages.danger(self.request, 'You do not have permission to delete the post')
        else:    
            if not post.date_published:
                post.date_updated = timezone.now()
            post.save()
            activity = Action(author=self.request.user,
                          activity=f'The post "{post.title}" was saved as draft', level='warning')
            activity.save()
            messages.success(request, f"Post is saved as draft successfully.")
        
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


class PostPublishView(LoginRequiredMixin, View):
    """
       View to publish a drafted post
    """

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'), author=self.request.user.author)
        post.status = Post.PUBLISHED

        if not post.date_published:
            post.date_published = timezone.now()
        post.save()
        activity = Action(author=self.request.user, activity=f'The post "{post.title}" was published', level='success')
        activity.save()
        messages.success(request, f"Post Published successfully.")
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))



class AuthorProfileView(LoginRequiredMixin, View):
    """
    Displays author profile details
    """
    template_name = "dashboard/profile.html"
    context_object = {}

    def get(self, request, author):
        user = get_object_or_404(User, username=author)

        self.context_object['user'] = user
        self.context_object['trending_posts'] = Post.objects.filter(author=user.author).order_by('-views')[:12]
        return render(request, self.template_name, self.context_object)

# to add context to a redirected page,
# request.session['item_name'] = value
# in template
# {{request.session.item_name}}

