from django.core import paginator
from django.http import request
from django.shortcuts import redirect, resolve_url, get_list_or_404, render, get_object_or_404, HttpResponseRedirect
from django.views import View
from django.views.generic import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count 
from .models import Post, Category, Reply, Comment, Subscribers, Video 
from django.db.models import Q
from functools import reduce
import operator
from django.contrib import messages
from accounts.models import Action

# Create your views here.
class IndexView(View):
    def get(self, request,*args,**kwargs):
        popular_posts = Post.objects.filter(deleted=False, status=Post.PUBLISHED).order_by('-views')[:4]
        context = {'posts': popular_posts}
        return render(request, 'blog/index.html', context)

def page_not_found(request, Exception):
    pv_link = request.META.get('http_referer')
    return render(request, '404.html', context={'pv_link': pv_link})


class CategoryView(View):
    def get(self,request,slug,*args,**kwargs):
        category_obj = get_object_or_404(Category, slug=slug)
        #post = category_obj.blog_set.all().order_by('-id')
        posts = Post.objects.filter(category= category_obj, deleted=False, status=Post.PUBLISHED)\
            .order_by('-date_created')
        popular = Post.objects.filter(category = category_obj, deleted=False, status=Post.PUBLISHED)\
            .annotate(post_count=Count('views'))\
            .order_by('-views')
        # as Per templates views
        featured_post = popular.first()
        popular_post = popular[1:6]
        # Pagination 
        paginator = Paginator(posts, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context ={
            'category':category_obj,
            'posts':page_obj,
            'popular_posts':popular_post,
            'f_post':featured_post,
        }
        return render(request,'blog/category.html', context )


class CommentView(LoginRequiredMixin, View):
    def post(self,request,post_slug, *args,**kwargs):
        post = get_object_or_404(Post,slug=post_slug)
        comment = Comment()
        comment.author = request.user.author
        comment.content = request.POST.get('content')
        comment.post = post
        comment.save()
        activity = Action(author=self.request.user, activity=f'You commented on %s "{post.title}" post'%('your' if post.author == request.user.author else f'{post.author}\'s'), level='info')
        activity.save()
        return HttpResponseRedirect(f"{request.META.get('HTTP_REFERER')}#comment{comment.id}")

class ReplyCommentView(LoginRequiredMixin, View):
    def post(self,request, comment_id, *args,**kwargs):
        reply_obj = Reply()
        reply_obj.comment = get_object_or_404(Comment, id=comment_id)
        reply_obj.author = request.user.author
        reply_obj.content = request.POST.get('content')
        reply_obj.save()

        activity = Action(author=self.request.user, activity=f'You replied%s on the topic: "{reply_obj.comment.post}"'%('' if reply_obj.comment.author == request.user.author else f' {reply_obj.comment.author}'), level='info')
        activity.save()
        return HttpResponseRedirect(f"{request.META.get('HTTP_REFERER')}#comment{comment_id}")
         

class SubscribeView(View):
    def post(self, request,*args,**kwargs):
        sub_obj = request.POST.get('email')
        email = Subscribers.objects.filter(email=sub_obj)
        if email :
            messages.success(request,message='You have already Subscribed , Thanks!', extra_tags='info')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            subscriber = Subscribers()
            subscriber.email = sub_obj
            subscriber.save()
            messages.success(request, message='Thanks for Subscribing!', extra_tags='success')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class SinglePostView(View):
    def get(self,request,post_slug,*args,**kwargs):
        post_obj = get_object_or_404(Post, slug=post_slug)

        if request.user.is_authenticated:
            post_obj.views.add(request.user)
            post_obj.save()
            
        latest_posts = Post.objects.filter(deleted=False, status=Post.PUBLISHED).exclude(slug=post_slug).order_by('-date_published')[:3]
        
        related_post = Post.objects.filter(deleted=False, status=Post.PUBLISHED, author=post_obj.author).exclude(slug=post_slug).order_by('-id')[:4]
        # As per templates views 
        first_post = related_post.first()
        last_post  = related_post[1:]
        
        context ={
            'categories': Category.objects.all(),
            'r_post': related_post,
            'first': first_post,
            'last': last_post,
            'post':post_obj,
            'latest_posts': latest_posts,
        }
        return render(request,'blog/post_detail.html', context)

class ContactUsView(View):
    def get(self, request):
        context = {}
        if request.user.is_authenticated:
            name = request.user.get_full_name()
            email = request.user.email
            context['name'] = name
            context['email'] = email

        return render(request, "blog/contact-us.html", context)

class PostListView(ListView):
    
    model = Post
    template_name = "blog/post_list.html"
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(deleted=False, status=Post.PUBLISHED)
        context["latest_posts"] = Post.objects.filter(status=Post.PUBLISHED, deleted=False).order_by("-date_published")[0:3]
        context["categories"] = Category.objects.filter(approved=True)
        return context
    

class SearchView(View):

    def get(self, request):

        query = self.request.GET.get('q')
        search_results = Post.objects.filter(deleted=False, status=Post.PUBLISHED)

        if query:
            query_list = query.split()
            search_results = search_results.filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(author__user__username__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(content__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(overview__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(category__name__icontains=q) for q in query_list))
            )
        paginator = Paginator(search_results, 6)
        page = request.GET.get('page')

        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)


        context = {'search_results': search_results, 'search': query}
        return render(request, 'blog/search.html', context)



class LikeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        
        post = get_object_or_404(Post, slug=self.kwargs.get("post_slug"))

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return HttpResponseRedirect(f"{request.META.get('HTTP_REFERER')}#likes")


class SavePostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        
        post = get_object_or_404(Post, slug=self.kwargs.get("post_slug"))

  
        if request.user.author.saved_posts.filter(id=post.id).exists():
            request.user.author.saved_posts.remove(post)
        else:
            request.user.author.saved_posts.add(post)
        return HttpResponseRedirect(f"{request.META.get('HTTP_REFERER')}")



class TagListView(ListView):
    """
        List articles related to a tag.
    """
    model = Post
    paginate_by = 12
    context_object_name = 'tag_articles_list'
    template_name = 'blog/tag_list.html'

    def get_queryset(self):
        """
            Filter Articles by tag_name
        """

        tag_name = self.kwargs.get('tag_name', '')
        tag_name_edit = tag_name.replace('#', '').capitalize()
        if tag_name:
            tag_articles_list = Post.objects.filter(tags__name__in=[tag_name],
                                                       status=Post.PUBLISHED,
                                                       deleted=False
                                                       )

            if not tag_articles_list:
                messages.info(self.request, f"No Results for '{tag_name_edit}' tag")
                return tag_articles_list
            else:
                messages.success(self.request, f"Results for '{tag_name_edit}' tag")
                return tag_articles_list
        else:
            messages.error(self.request, "Invalid tag")
            return []
            
            return tag_articles_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(approved=True)
        context['tag_name'] = self.kwargs.get('tag_name', '')
        return context
