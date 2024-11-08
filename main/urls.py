from django.urls import path

from .views import BlogView, add_post, update_post, AddCategoryView, AddTagView, UpdateCategoryView, PreviewPostView, AboutView, PostDetailView, posts_by_category, PostsByTagListView

urlpatterns = [
    path('', BlogView.as_view(), name='blog'),
    path('about/', AboutView.as_view(), name='about'), # as_view() - это метод класса-представления, который возвращает экземпляр класса-представления, готовый к обработке запроса.

    path('post/<slug:slug>/view/', PostDetailView.as_view(), name='post_by_slug'),
    path('category/<slug:category_slug>/posts/', posts_by_category, name="posts_by_category"),
    path('tag/<slug:tag_slug>/posts/', PostsByTagListView.as_view(), name="posts_by_tag"),

    path('post/add/', add_post, name='add_post'),
    path("post/<slug:post_slug>/update/", update_post, name="update_post"),
    path('preview/', PreviewPostView.as_view(), name='preview_post'),

    path("category/add/", AddCategoryView.as_view(), name="add_category"),
    path("category/<slug:category_slug>/update/", UpdateCategoryView.as_view(), name="update_category"),

    path("tag/add/", AddTagView.as_view(), name="add_tag"),
]