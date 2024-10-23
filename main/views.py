from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from .dataset import dataset
from .models import Post, Category, Tag

from django.urls import reverse
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import json
from .templatetags.md_to_html import markdown_to_html

from django.db.models import F, Q

from .forms import CommentForm, CategoryForm, TagForm, PostForm
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.decorators import login_required, permission_required

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

    posts = Post.objects.prefetch_related('tags', 'comments').select_related('author', 'category').filter(status="published")

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

    breadcrumbs = [
        {'name': 'Главная', 'url': reverse('main')},
        {'name': 'Блог'},
    ]
    
    return render(request, 'main/blog.html', {
        'breadcrumbs': breadcrumbs,
        'paginated_posts': paginated_posts,
        'menu': menu,
        'page_alias': 'blog'
    })


def main(request):
    context = {
        'menu': menu,
        'page_alias': 'main'   
    }

    return render(request, template_name='main/index.html', context=context)


def about(request):
    breadcrumbs = [
        {'name': 'Главная', 'url': reverse('main')},
        {'name': 'О проекте'},
    ]
    return render(request, 'main/about.html', {
        'breadcrumbs': breadcrumbs,
        'menu': menu,
        'page_alias': 'about'
    })


def post_by_slug(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)

    breadcrumbs = [
        {'name': 'Главная', 'url': reverse('main')},
        {'name': 'Блог', 'url': reverse('blog')},
        {'name': post.title}
    ]
    
    # Проверяем, есть ли ключ 'post_{post.id}_viewed' в словаре session в текущей сессии, если нет то добавляем
    # И увеличиваем views на 1
    if f'post_{post.id}_viewed' not in request.session:
        Post.objects.filter(id=post.id).update(views=F('views') + 1)
        request.session[f'post_{post.id}_viewed'] = True

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
                return redirect('post_by_slug', post_slug=post_slug)
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
        'breadcrumbs': breadcrumbs,
        'post': post,
        'menu': menu,
        'page_alias': 'blog',
        'form': form,
        'paginated_comments': paginated_comments
    }
    
    return render(request, 'main/post_detail.html', context=context)


@login_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(author=request.user)
            messages.success(request, 'Пост успешно создан и отправлен на модерацию.')
            return redirect('add_post')
    else:
        form = PostForm()

    return render(request, 'main/add_post.html', {'form': form, 'menu': menu, 'page_alias': 'add_post'})


@login_required
def update_post(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пост успешно обновлен и отправлен на модерацию.')
            return redirect('update_post', post_slug=post_slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'main/add_post.html', {'form': form, 'menu': menu})


def posts_by_category(request, category_slug):
    context = {
        'menu': menu,
        'page_alias': 'blog', 
        'paginated_posts': Category.objects.get(slug=category_slug).posts.all() # Сделать пагинацию
    }

    return render(request, 'main/blog.html', context=context)


def posts_by_tag(request, tag_slug):
    context = {
        'menu': menu,
        'page_alias': 'blog', 
        'posts': Post.objects.filter(tags__slug=tag_slug)
    }

    return render(request, 'main/blog.html', context=context)

# @csrf_exempt # Отключает проверку CSRF токена при пост запросах для этой вью
def preview_post(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', '')
        html = markdown_to_html(text)
        return JsonResponse({'html': html})


@login_required
def add_category(request):
    context = {"menu": menu}
    
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Категория '{form.cleaned_data['name']}' успешно добавлена!")
            return redirect('add_category')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
    else:
        form = CategoryForm()
    
    context.update({
        "form": form,
        "operation_title": "Добавить категорию",
        "operation_header": "Добавить новую категорию",
        "submit_button_text": "Создать",
    })
    return render(request, "main/category_form.html", context)
    

@login_required
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


@login_required
def update_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    context = {"menu": menu}

    if request.method == "POST":
        category_name = category.name
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Категория '{category_name}' успешно обновлена.")
            return redirect('posts_by_category', category=category.slug)
            # return redirect('update_category', category_slug=category.slug)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
    else:
        form = CategoryForm(instance=category)
    
    context.update({
        "form": form,
        "operation_title": "Обновить категорию",
        "operation_header": "Обновить категорию",
        "submit_button_text": "Сохранить",
    })
    return render(request, "main/category_form.html", context)
