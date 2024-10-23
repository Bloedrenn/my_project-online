from django.urls import path

from .views import blog, add_post, update_post, add_category, add_tag, update_category, preview_post, about, post_by_slug, posts_by_category, posts_by_tag

urlpatterns = [
    path('', blog, name='blog'),
    path('about/', about, name='about'),

    path('post/<slug:post_slug>/view/', post_by_slug, name='post_by_slug'),
    path('category/<slug:category_slug>/posts/', posts_by_category, name="posts_by_category"),
    path('tag/<slug:tag_slug>/posts/', posts_by_tag, name="posts_by_tag"),

    path('post/add/', add_post, name='add_post'),
    path("post/<slug:post_slug>/update/", update_post, name="update_post"),
    path('preview/', preview_post, name='preview_post'),

    path("category/add/", add_category, name="add_category"),
    path("category/<slug:category_slug>/update/", update_category, name="update_category"),

    path("tag/add/", add_tag, name="add_tag"),
]