from django.db import models
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode

# Create your models here.

class Post(models.Model):
    STATUS_CHOICES = (
        ('published','Опубликован'),
        ('draft','Черновик')
    )

    author = models.ForeignKey(get_user_model(), related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=300, unique=True)
    text = models.TextField()
    cover_image = models.ImageField(blank=True, null=True, upload_to='images/')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey('Category', related_name='posts', blank=True, null=True, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))

        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('post_by_slug', kwargs={'slug': self.slug})
        # return f'/blog/post/{self.slug}/view/'


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.name))

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.name = self.name.lower().replace(' ', '_')
        self.slug = slugify(unidecode(self.name))

        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.name}'

    def get_absolute_url(self):
        url = reverse_lazy('posts_by_tag', args=[self.slug])
        return url


class Comment(models.Model):
    STATUS_CHOICES = (
        ('unchecked','Не проверен'),
        ('accepted','Проверен'),
        ('rejected','Отклонён')
    )

    text = models.TextField(max_length=2000)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='unchecked')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
