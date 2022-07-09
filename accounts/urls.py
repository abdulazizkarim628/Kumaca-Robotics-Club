from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
app_name = 'accounts'
urlpatterns = [
    #Authentication and authorization
    path('signup/', views.SignupForm, name='signup'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('changepassword/', views.ChangePasswordView, name='changepassword'),
    

    path('dashboard/', include([
        path('', views.DashboardHomeView.as_view(), name='dashboard'),
        
        path('search/', views.SearchView.as_view(), name='dashboard_search'),
        path('clearall/<str:obj>/', views.ClearView.as_view(), name='clear'),
        path('update_profile/',views.AuthorProfileUpdateView,name='profile_update'),
        

        path('activitylog/', include([
            path('', views.ActivityLogView.as_view(), name='activitylog'),
            
        ])),
        
        #for posts
        path('<slug:slug>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
        path('posts/', include([
            path('', views.AuthorPostsView.as_view(), name='author_posts'),
            path('deleted/', views.AuthorDeletedPostsView.as_view(), name='deleted_posts'),
            path('drafted/', views.AuthorDraftedPostsView.as_view(), name='drafted_posts'),
            path('create/', views.PostCreateView.as_view(), name='create_post'),
            path('published/', views.AuthorPublishedPostsView.as_view(), name='published_posts'),
            path('saved/', views.SavedPostsView.as_view(), name='saved_posts'),
            
            
            path('<slug:slug>/', include([
                path('', views.DashboardPostDetailView.as_view(), name='dashboard_post_detail'),
                path('publish/', views.PostPublishView.as_view(), name='publish_post'),
                path('draft/', views.PostDraftView.as_view(), name='draft_post'),
                path('update/', views.PostUpdateView.as_view(), name='update_post'),
                
                
            ])),
            
        ])),
        #path('update/', views.AuthorProfileUpdateView.as_view(), name='update_profile'),
        # author profile actions
        path('<str:author>/', views.AuthorProfileView.as_view(), name='profile')
    ]))
]