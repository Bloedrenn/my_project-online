from django.urls import path

from .views import blog, add_post, preview_post, about, main, post_by_slug, posts_by_category, posts_by_tag

urlpatterns = [
    path('blog/post/<slug:slug>/view/', post_by_slug, name='post_by_slug'),
    path('blog/category/<slug:category>/posts/', posts_by_category, name="posts_by_category"),
    path('blog/tag/<slug:tag>/posts/', posts_by_tag, name="posts_by_tag"),
    path('blog/post/add/', add_post, name='add_post'),
    path('preview/', preview_post, name='preview_post'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('', main, name='main'),
]