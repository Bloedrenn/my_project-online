from django.shortcuts import render, HttpResponse, get_object_or_404
from .dataset import dataset
from .models import Post

menu = [
    {"name": "Главная", "alias": "main"},
    {"name": "Блог", "alias": "blog"},
    {"name": "О проекте", "alias": "about"},
]


def blog(request):
    context = {
        'dataset': dataset,
        'menu': menu,
        'page_alias': 'blog'   
    }

    return render(request, template_name='main/blog.html', context=context)

def main(request):
    context = {
        'menu': menu,
        'page_alias': 'main'   
    }

    return render(request, template_name='main/index.html', context=context)

def about(request):
    context = {
        'menu': menu,
        'page_alias': 'about'   
    }

    return render(request, template_name='main/about.html', context=context)


def post_by_slug(request, slug):
    # posts = Post.objects.all()
    # post = [post for post in posts if post.slug == slug][0]

    # if not post:
    #     return HttpResponse('404 - Пост не найден', status=404)

    post = get_object_or_404(Post, slug=slug)

    context = {
        'title': post.title,
        'text': post.text,
        'hashtags': post.tags,
        'created_at': post.created_at,
        'updated_at': post.updated_at
    }

    context['menu'] = menu
    context['page_alias'] = 'blog'
    
    return render(request, 'main/post_detail.html', context=context)