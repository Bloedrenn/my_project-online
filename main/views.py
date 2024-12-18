from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, Tag

from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import View, TemplateView, CreateView, UpdateView, ListView, DetailView
from django.views.generic.edit import FormMixin

from django.urls import reverse, reverse_lazy
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

# Оказалось не нужным:
# from django.utils.decorators import method_decorator
# @method_decorator(login_required)

menu = [
    {"name": "Главная", "alias": "main"},
    {"name": "Блог", "alias": "blog"},
    {"name": "Добавить пост", "alias": "add_post"},
    {"name": "О проекте", "alias": "about"}
]


class BlogView(ListView):
    model = Post
    template_name = 'main/blog.html'
    context_object_name = 'posts'
    paginate_by = 4
    extra_context = {
        'menu': menu,
        'page_alias': 'blog',
        'breadcrumbs': [
            {'name': 'Главная', 'url': reverse_lazy('main')},
            {'name': 'Блог'},
        ]
    }

    def get_queryset(self):
        # Базовый QuerySet с предзагрузкой связанных данных
        queryset = Post.objects.prefetch_related('tags', 'comments').select_related('author', 'category').filter(status="published")
        
        # Получаем параметры поиска из GET-запроса
        search_query = self.request.GET.get("search", "")
        search_category = self.request.GET.get("search_category")
        search_tag = self.request.GET.get("search_tag")
        search_comments = self.request.GET.get("search_comments")

        if search_query:
            query = Q(title__icontains=search_query) | Q(text__icontains=search_query)
            
            if search_category:
                query |= Q(category__name__icontains=search_query)
            
            if search_tag:
                query |= Q(tags__name__icontains=search_query)
            
            if search_comments:
                query |= Q(comments__text__icontains=search_query)
            
            queryset = queryset.filter(query)

        return queryset.distinct().order_by("-created_at")


class IndexView(TemplateView):
    # Указываем имя шаблона для отображения страницы
    template_name = "main/index.html"

    # Дополняем встроенный контекст
    extra_context = {
        'menu': menu,          # Глобальное меню сайта
        'page_alias': 'main',  # Идентификатор текущей страницы
    }

    # Можно передать контекст по-другому:
    # def get_context_data(self, **kwargs):
    #     # Получаем базовый контекст от родительского класса
    #     context = super().get_context_data(**kwargs)
    #     # Добавляем в контекст глобальное меню сайта
    #     context["menu"] = menu
    #     # Устанавливаем идентификатор текущей страницы
    #     context["page_alias"] = "main"
    #     return context


class AboutView(View):
    """
    Класс-представление для отображения страницы "О проекте".
    
    Методы:
        get(request) - обрабатывает GET-запросы к странице
        
    Атрибуты:
        breadcrumbs - список навигационных ссылок (хлебные крошки)
        menu - глобальное меню сайта
        page_alias - идентификатор текущей страницы
        
    Шаблон: about.html
    
    Контекст шаблона:
        - breadcrumbs: список словарей с навигационными ссылками
        - menu: список пунктов главного меню
        - page_alias: строка-идентификатор страницы
    """
    def get(self, request):
        breadcrumbs = [
            {'name': 'Главная', 'url': reverse('main')},
            {'name': 'О проекте'},
        ]

        return render(request, 'main/about.html', {
            'breadcrumbs': breadcrumbs,
            'menu': menu,
            'page_alias': 'about'
        })


class PostDetailView(FormMixin, DetailView):
    model = Post
    template_name = 'main/post_detail.html'
    # context_object_name = 'post' Не нужно
    form_class = CommentForm

    def get_success_url(self):
        return reverse('post_by_slug', kwargs={'slug': self.object.slug})

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        # Проверяем, есть ли ключ 'post_{post.id}_viewed' в словаре session в текущей сессии, если нет то добавляем
        # И увеличиваем views на 1
        if f'post_{post.id}_viewed' not in self.request.session:
            Post.objects.filter(id=post.id).update(views=F('views') + 1)
            self.request.session[f'post_{post.id}_viewed'] = True

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = self.object.comments.filter(status='accepted').order_by('created_at')
        paginator = Paginator(comments, 20)
        page_number = self.request.GET.get('page')

        try:
            paginated_comments = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_comments = paginator.page(1)
        except EmptyPage:
            paginated_comments = paginator.page(paginator.num_pages)

        context['paginated_comments'] = paginated_comments
        context['menu'] = menu
        context['page_alias'] = 'blog'
        context['breadcrumbs'] = [
            {'name': 'Главная', 'url': reverse('main')},
            {'name': 'Блог', 'url': reverse('blog')},
            {'name': self.object.title}
        ]
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, 'Ваш комментарий находится на модерации.')
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


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

    context = {
        "form": form,
        'menu': menu,
        'page_alias': 'add_post',
        "operation_name": "Добавить пост",
        "submit_button_text": "Добавить",
    }

    return render(request, 'main/post_form.html', context)


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

    context = {
        "form": form,
        'menu': menu,
        "operation_name": "Обновить пост",
        "submit_button_text": "Обновить",
    }

    return render(request, 'main/post_form.html', context)


class PostsByCategoryListView(ListView):
    model = Post
    template_name = 'main/blog.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        return Post.objects.select_related('author', 'category')\
                        .prefetch_related('tags', 'comments')\
                        .filter(category__slug=category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['menu'] = menu
        context['page_alias'] = 'blog'
        context['breadcrumbs'] = [
            {'name': 'Главная', 'url': reverse('main')},
            {'name': 'Блог', 'url': reverse('blog')},
            {'name': Category.objects.get(slug=self.kwargs['category_slug']).name}
        ]

        return context


class PostsByTagListView(ListView):
    """
    Класс-представление для отображения списка постов по тегу.
    """
    model = Post
    template_name = 'main/blog.html'
    context_object_name = 'posts'
    paginate_by = 2
    extra_context = {
        'menu': menu,
        "page_alias": "blog"
    }

    def get_queryset(self):
        posts = Post.objects.filter(tags__slug=self.kwargs['tag_slug'])
        return posts


class PreviewPostView(View):
    """
    Класс-представление для предпросмотра постов через AJAX
    """
    http_method_names = ['post']  # Явно указываем разрешенный метод
    
    def post(self, request):
        # Получаем данные из тела AJAX-запроса в формате JSON
        data = json.loads(request.body)
        # Извлекаем текст поста из данных с пустой строкой как значение по умолчанию
        text = data.get("text", "")
        # Преобразуем markdown-разметку в HTML для предпросмотра
        html = markdown_to_html(text)
        # Отправляем готовый HTML в формате JSON обратно клиенту
        return JsonResponse({"html": html})


class AddCategoryView(LoginRequiredMixin, View):
    """
    Класс-представление для добавления новой категории.
    
    Методы:
        get(request) - обрабатывает GET-запросы, отображает форму для создания категории
        post(request) - обрабатывает POST-запросы, сохраняет новую категорию
        
    Атрибуты контекста:
        menu - глобальное меню сайта
        form - форма для создания категории (CategoryForm)
        operation_title - заголовок операции
        operation_header - заголовок формы
        submit_button_text - текст кнопки отправки формы
        
    Шаблон: category_form.html
    
    Сообщения:
        - Успех: "Категория '{name}' успешно добавлена!"
        - Ошибка: "Пожалуйста, исправьте ошибки ниже."
        
    Редиректы:
        - После успешного создания: add_category
        - При ошибке валидации: add_category
    """
    def get(self, request):
        # Формируем контекст для отображения формы добавления категории
        context = {
            "menu": menu,
            "form": CategoryForm(),
            "operation_title": "Добавить категорию",
            "operation_header": "Добавить новую категорию",
            "submit_button_text": "Создать",
        }
        # Отображаем шаблон с формой для создания категории
        return render(request, "main/category_form.html", context)
    
    def post(self, request):
        # Создаем форму на основе полученных POST данных
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Сохраняем новую категорию в базу данных
            form.save()
            # Добавляем сообщение об успешном создании категории
            messages.success(request, f"Категория '{form.cleaned_data['name']}' успешно добавлена!")
            return redirect('add_category')
        else:
            # В случае ошибки валидации формы, добавляем сообщение об ошибке
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
            return redirect('add_category')
    

class AddTagView(LoginRequiredMixin, CreateView):
    """
    Класс-представление для добавления тега.
    Наследуется от CreateView для создания объектов и LoginRequiredMixin для ограничения доступа
    только авторизованным пользователям
    """

    # Указываем модель, с которой будет работать представление
    model = Tag

    # Указываем форму, которую мы описали в forms.py
    form_class = TagForm

    # Указываем путь к шаблону, который будет использоваться для отображения формы
    template_name = "main/add_tag.html"

    success_url = reverse_lazy("add_tag")

    extra_context = {
        'menu': menu,          # Глобальное меню сайта
    }

    def form_valid(self, form):
            """Метод вызывается при успешной валидации формы"""
            # Сохраняем форму
            response = super().form_valid(form)
            # Добавляем сообщение об успехе
            messages.success(self.request, f"Тег {form.instance.name} успешно добавлен!")
            return response
    
    def form_invalid(self, form):
        """Метод вызывается при неуспешной валидации формы"""
        # Добавляем сообщение об ошибке
        messages.error(self.request, "Ошибка при добавлении тега. Проверьте введенные данные.")
        return super().form_invalid(form)


class UpdateCategoryView(LoginRequiredMixin, UpdateView):
    """
    Класс-представление для обновления категории.
    Наследуется от UpdateView для редактирования объектов и LoginRequiredMixin для ограничения доступа
    только авторизованным пользователям
    """
    model = Category
    form_class = CategoryForm
    template_name = "main/category_form.html"
    extra_context = {
        'menu': menu,
        "operation_title": "Обновить категорию",
        "operation_header": "Обновить категорию",
        "submit_button_text": "Сохранить",
    }
        
    def get_object(self):
        """Метод для получения объекта категории по slug из URL"""
        return get_object_or_404(Category, slug=self.kwargs['category_slug'])
    
    def get_success_url(self):
        """Метод определяет URL для перенаправления после успешного обновления категории"""
        # category/<slug:category_slug>/posts/
        return reverse_lazy('posts_by_category', kwargs={'category_slug': self.object.slug})
    
    def form_valid(self, form):
        """Метод вызывается при успешной валидации формы"""
        response = super().form_valid(form)
        messages.success(self.request, f"Категория успешно обновлена.")
        return response
    
    def form_invalid(self, form):
        """Метод вызывается при неуспешной валидации формы"""
        messages.error(self.request, "Пожалуйста, исправьте ошибки ниже.")
        return super().form_invalid(form)
    

class LikePostView(View):
    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        user = request.user

        if post.liked_users.filter(id=user.id).exists():
            # Пользователь уже лайкнул пост, удаляем лайк
            post.liked_users.remove(user)
            liked = False
        else:
            # Пользователь еще не лайкнул пост, добавляем лайк
            post.liked_users.add(user)
            liked = True
            
        # Возвращаем обновленные данные о лайках
        return JsonResponse({'liked': liked, 'likes_count': post.liked_users.count()})
