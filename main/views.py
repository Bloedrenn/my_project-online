from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .dataset import dataset
from .models import Post, Category, Tag

from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import json
from .templatetags.md_to_html import markdown_to_html

from django.db.models import F, Q

from .forms import CommentForm
from django.contrib import messages

# from django.core.cache import cache
# from django.core.cache.utils import make_template_fragment_key

menu = [
    {"name": "Главная", "alias": "main"},
    {"name": "Блог", "alias": "blog"},
    {"name": "Добавить пост", "alias": "add_post"},
    {"name": "О проекте", "alias": "about"}
]


def blog(request):
    search_query = request.GET.get('search', '')
    search_category = request.GET.get("search_category")
    search_tag = request.GET.get("search_tag")
    # search_comments = request.GET.get("search_comments")

    posts = Post.objects.prefetch_related('tags').select_related('author').select_related('category').filter(status="published")

    if search_query:
        query = Q(title__icontains=search_query) | Q(text__icontains=search_query) 
        
        if search_category:
            query |= Q(category__name__icontains=search_query)
        
        if search_tag:
            query |= Q(tags__name__icontains=search_query)
        
        # if search_comments:
        #     query |= Q(comment__text__icontains=search_query)
        
        posts = posts.filter(query)

    posts = posts.distinct().order_by("-created_at")

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

    Post.objects.filter(slug=slug).update(views=F('views') + 1)
    # Как обновить кеш только там где нужно?
    # key = make_template_fragment_key("post_preview", [post.id])
    # cache.delete(key)
    # key = make_template_fragment_key("post_detail", [post.id])
    # cache.delete(key)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                # Создаем комментарий, но пока не сохраняем в базу
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Ваш комментарий находится на модерации.')
                return redirect('post_by_slug', slug=slug)
        else:
            messages.error(request, 'Для добавления комментария необходимо войти в систему.')
            return redirect('login')
    else:
        form = CommentForm()

    # Выбираем только одобренные комментарии
    comments = post.comments.filter(status='accepted')

    context = {
        'post': post,
        'menu': menu,
        'page_alias': 'blog',
        'form': form,
        'comments': comments,
    }
    
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
