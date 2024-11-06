from django.urls import path

from .views import blog, add_post, update_post, AddCategoryView, AddTagView, update_category, preview_post, AboutView, post_by_slug, posts_by_category, posts_by_tag

urlpatterns = [
    path('', blog, name='blog'),
    path('about/', AboutView.as_view(), name='about'), # as_view() - это метод класса-представления, который возвращает экземпляр класса-представления, готовый к обработке запроса.

    path('post/<slug:post_slug>/view/', post_by_slug, name='post_by_slug'),
    path('category/<slug:category_slug>/posts/', posts_by_category, name="posts_by_category"),
    path('tag/<slug:tag_slug>/posts/', posts_by_tag, name="posts_by_tag"),

    path('post/add/', add_post, name='add_post'),
    path("post/<slug:post_slug>/update/", update_post, name="update_post"),
    path('preview/', preview_post, name='preview_post'),

    path("category/add/", AddCategoryView.as_view(), name="add_category"),
    path("category/<slug:category_slug>/update/", update_category, name="update_category"),

    path("tag/add/", AddTagView.as_view(), name="add_tag"),
]