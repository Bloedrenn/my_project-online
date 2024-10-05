from django.shortcuts import render, HttpResponse, get_object_or_404
from .dataset import dataset
from .models import Post

menu = [
    {"name": "Главная", "alias": "main"},
    {"name": "Блог", "alias": "blog"},
    {"name": "Добавить пост", "alias": "add_post"},
    {"name": "О проекте", "alias": "about"}
]


def blog(request):
    context = {
        'posts': Post.objects.all(),
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

        if title and text:
            if not Post.objects.filter(title=title).exists():
                Post.objects.create(author=author, title=title, text=text)

                context['message'] = 'Пост успешно добавлен'

                return render(request, 'main/add_post.html', context=context)
            else:
                context['message'] = 'Такой пост уже существует'

                return render(request, 'main/add_post.html', context=context)
        else:
            context.update({'message': 'Заполните все поля'})

            return render(request, 'main/add_post.html', context=context)
        
def posts_by_tag(request, tag):
    context = {
        'menu': menu,
        'page_alias': 'blog', 
        'posts': Post.objects.filter(tags__slug=tag)
    }

    return render(request, 'main/blog.html', context=context)
