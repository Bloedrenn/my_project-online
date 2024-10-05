from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode

# Create your models here.

class Post(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=300, unique=True)
    text = models.TextField()
    slug = models.SlugField(unique=True)
    tags = models.ManyToManyField('Tag', related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))

        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('post_by_slug', kwargs={'slug': self.slug})
        # return f'/blog/post/{self.slug}/view/'


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.name = self.name.lower().replace(' ', '_')
        self.slug = slugify(unidecode(self.name))

        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.name}'
