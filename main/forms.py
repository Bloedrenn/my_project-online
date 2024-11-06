from django import forms
from .models import Comment, Category, Tag, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Если это существующий пост, заполняем поле тегов
            self.initial['tags'] = ', '.join([tag.name for tag in self.instance.tags.all()])

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Выберите категорию",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Категория'
    )

    tags = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите теги через запятую'}),
        label='Теги',
        required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'cover_image', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст поста',
            'cover_image': 'Обложка',
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags:
            return [tag.strip().lower().replace(' ', '_') for tag in tags.split(',') if tag.strip()]
        return []
    
    def save(self, commit=True, author=None):
        instance = super().save(commit=False)
        if author:
            instance.author = author
        if commit:
            instance.save()
            self.save_tags(instance)
        return instance
    
    def save_tags(self, instance):
        instance.tags.clear()

        tag_names = self.cleaned_data.get('tags')

        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Введите ваш комментарий...'}),
        }
        labels = {
            'text': '',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category

        fields = ['name']

        labels = {
            'name': 'Название категории'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название категории'})
        }
        help_texts = {
            'name': 'Введите название категории (от 2 до 200 символов)'
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("Категория с таким названием уже существует.")
        return name
    

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название тега'}),
        }
        labels = {
            'name': 'Название тега',
        }
    
    def clean_name(self):
        name = self.cleaned_data['name'].lower().strip().replace(' ', '_')
        if Tag.objects.filter(name=name).exists():
            raise forms.ValidationError("Тег с таким названием уже существует.")
        return name
