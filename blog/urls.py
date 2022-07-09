from django.urls import path, include
from . import views

# make sure you arrange the links very well they are arranged according to priority
app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('like/', views.LikeView.as_view(), name='like_post'),
    path('<slug:post_slug>/save/', views.SavePostView.as_view(), name='save_post'),
    path('topic/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('<slug:post_slug>/comment/',views.CommentView.as_view(), name='comment'),
    path('tags/<str:tag_name>/', views.TagListView.as_view(), name='tag_list'),
    path('<int:comment_id>/reply_comment/', views.ReplyCommentView.as_view(), name='reply_comment'),
    
    path('blog/', include([
        path('search/', views.SearchView.as_view(), name='search'),
        path('', views.PostListView.as_view(), name='posts'),
        path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
        path('<slug:post_slug>/', include([
            path('', views.SinglePostView.as_view(), name='post_detail'),
            path('like/', views.LikeView.as_view(), name='like_post'),
     ])),
    ]))
]

