from django.urls import path

from .views import blog, add_post, update_post, add_category, add_tag, update_category, preview_post, about, main, post_by_slug, posts_by_category, posts_by_tag

urlpatterns = [
    path('blog/post/<slug:slug>/view/', post_by_slug, name='post_by_slug'),
    path('blog/category/<slug:category>/posts/', posts_by_category, name="posts_by_category"),
    path('blog/tag/<slug:tag>/posts/', posts_by_tag, name="posts_by_tag"),
    path('blog/post/add/', add_post, name='add_post'),
    path("blog/post/<slug:post_slug>/update/", update_post, name="update_post"),
    path("blog/category/add/", add_category, name="add_category"),
    path("blog/category/<slug:category_slug>/update/", update_category, name="update_category"),
    path("blog/tag/add/", add_tag, name="add_tag"),
    path('preview/', preview_post, name='preview_post'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('', main, name='main'),
]