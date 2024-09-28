from django.shortcuts import render, HttpResponse
from .dataset import dataset

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
    post = [post for post in dataset if post['slug'] == slug]

    if not post:
        return HttpResponse('404 - Пост не найден', status=404)
    
    context = post[0]
    context['menu'] = menu
    context['page_alias'] = 'blog'
    
    return render(request, 'main/post_detail.html', context=context)