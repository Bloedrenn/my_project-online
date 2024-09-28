from django.urls import path

from .views import blog, about, main, post_by_slug

urlpatterns = [
    path('blog/post/<slug:slug>/view/', post_by_slug, name='post_by_slug'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('', main, name='main'),
]