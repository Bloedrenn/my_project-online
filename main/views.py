from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .dataset import dataset
from .models import Post, Category, Tag

from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import json
from .templatetags.md_to_html import markdown_to_html

from django.db.models import F, Q

from .forms import CommentForm, CategoryForm, TagForm
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

    page_number = request.GET.get('page', 1)  # Получаем номер страницы из URL-параметра 'page' /blog/?page=2

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

    paginator = Paginator(posts, 2) # первый аргумент - кверисет, второй - сколько объектов на странице
    try:
        paginated_posts = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_posts = paginator.page(1)  # Если параметр page не число, показываем первую страницу
    except EmptyPage:
        paginated_posts = paginator.page(paginator.num_pages)  # Если страница вне диапазона, показываем последнюю

    context = {
        'paginated_posts': paginated_posts,
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

    # Простой вариант увеличения просмотров (1)
    # post.views = F('views') + 1
    # post.save(update_fields=['views'])
    
    # Проверяем, был ли уже просмотр поста в текущей сессии (2)
    # if f'post_{post.id}_viewed' not in request.session:
    #     post.views = F('views') + 1
    #     post.save(update_fields=['views'])
    #     request.session[f'post_{post.id}_viewed'] = True

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

    # Пагинация комментариев
    comments = post.comments.filter(status='accepted').order_by('-created_at')
    paginator = Paginator(comments, 2)  # 2 комментариев на страницу
    page_number = request.GET.get('page', 1)
    try:
        paginated_comments = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_comments = paginator.page(1)
    except EmptyPage:
        paginated_comments = paginator.page(paginator.num_pages)

    context = {
        'post': post,
        'menu': menu,
        'page_alias': 'blog',
        'form': form,
        'paginated_comments': paginated_comments
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


def add_category(request):
    context = {"menu": menu}
    if request.method == "GET":
        form = CategoryForm()
        context["form"] = form
        return render(request, "main/add_category.html", context)
    
    elif request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            # # Добавим проверку, существует ли категория с таким именем (если такой нет в методе clean в forms.py)
            # if Category.objects.filter(name=form.cleaned_data['name']).exists():
            #     # Помещаем ошибку в поле name формы
            #     form.add_error('name', 'Категория с таким названием уже существует')
            #     context['form'] = form
            #     return render(request, "main/add_category.html", context)

            name = form.cleaned_data['name']
            Category.objects.create(name=name)

            # Добавляем ключ message о том что категория добавлена
            context["message"] = f"Категория {name} успешно добавлена!"
            context["form"] = form
            
            return render(request, "main/add_category.html", context)
        
        context["form"] = form
        return render(request, "main/add_category.html", context)
    

def add_tag(request):
    """
    Будет использовать форму связанную с моделью Tag - TagForm
    Шаблон - add_tag.html
    """
    context = {"menu": menu}
    if request.method == "GET":
        form = TagForm()
        context["form"] = form
        return render(request, "main/add_tag.html", context)
    
    elif request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            # Так как форма связана с моделью мы можем использовать метод save() к форме
            form.save()
            # Добавляем ключ message о том что тег добавлен
            name = form.cleaned_data['name']

            context["message"] = f"Тег {name} успешно добавлен!"
            context["form"] = form

            return render(request, "main/add_tag.html", context)
        
        context["form"] = form
        return render(request, "main/add_tag.html", context)
