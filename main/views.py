from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .dataset import dataset
from .models import Post, Category, Tag

from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import json
from .templatetags.md_to_html import markdown_to_html

menu = [
    {"name": "Главная", "alias": "main"},
    {"name": "Блог", "alias": "blog"},
    {"name": "Добавить пост", "alias": "add_post"},
    {"name": "О проекте", "alias": "about"}
]


def blog(request):
    search_query = request.GET.get('search', '')

    if search_query:
        posts = Post.objects.filter(text__icontains=search_query)
    else:
        posts = Post.objects.filter(status="published").order_by('-created_at')

    context = {
        'posts': posts,
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
        'hashtags': post.tags.all(),
        'created_at': post.created_at,
        'updated_at': post.updated_at
    }

    context['menu'] = menu
    context['page_alias'] = 'blog'
    
    return render(request, 'main/post_detail.html', context=context)

def add_post(request):
    context = {
        'menu': menu,
        'page_alias': 'add_post'
    }

    if request.method == 'GET':
        return render(request, 'main/add_post.html', context=context)
    
    elif request.method == 'POST':
        author = request.user
        title = request.POST['title']
        text = request.POST['text']
        tags = request.POST['tags']

        if title and text:
            if not Post.objects.filter(title=title).exists():
                post = Post.objects.create(author=author, title=title, text=text)

                tag_list = [tag.strip().lower().replace(' ', '_') for tag in tags.split(',') if tag.strip()]
                for tag in tag_list:
                    tag, created = Tag.objects.get_or_create(name=tag)
                    post.tags.add(tag)

                context['message'] = 'Пост успешно добавлен'

                return redirect('post_by_slug', slug=post.slug)
            else:
                context['message'] = 'Такой пост уже существует'

                return render(request, 'main/add_post.html', context=context)
        else:
            context.update({'message': 'Заполните все поля'})

            return render(request, 'main/add_post.html', context=context)
        

def posts_by_category(request, category):
    context = {
        'menu': menu,
        'page_alias': 'blog', 
        'posts': Category.objects.get(slug=category).posts.all()
    }

    return render(request, 'main/blog.html', context=context)


def posts_by_tag(request, tag):
    context = {
        'menu': menu,
        'page_alias': 'blog', 
        'posts': Post.objects.filter(tags__slug=tag)
    }

    return render(request, 'main/blog.html', context=context)

# @csrf_exempt # Отключает проверку CSRF токена при пост запросах для этой вью
def preview_post(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', '')
        html = markdown_to_html(text)
        return JsonResponse({'html': html})
