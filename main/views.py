from django.shortcuts import render, HttpResponse
from .dataset import dataset

# Create your views here.

def index(request):
    context = {'dataset': dataset}

    return render(request, template_name='main/index.html', context=context)


def post_by_slug(request, slug):
    post = [post for post in dataset if post['slug'] == slug]

    if not post:
        return HttpResponse('404 - Пост не найден', status=404)
    
    return render(request, 'main/post_detail.html', context=post[0])