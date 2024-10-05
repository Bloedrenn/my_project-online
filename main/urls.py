from django.urls import path

from .views import blog, add_post, about, main, post_by_slug, posts_by_tag

urlpatterns = [
    path('blog/post/<slug:slug>/view/', post_by_slug, name='post_by_slug'),
    path('blog/tag/<slug:tag>/posts/', posts_by_tag, name="posts_by_tag"),
    path('blog/post/add/', add_post, name='add_post'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('', main, name='main'),
]