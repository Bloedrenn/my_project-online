from django import forms
from .models import Comment, Category, Tag

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

    # def save(self, commit=True):
    #     """
    #     Тут можно переопределить логику сохранения. 
    #     Как правило это добавление связанных данных или т.п.
    #     """
    #     return tag
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if Tag.objects.filter(name=name).exists():
            raise forms.ValidationError("Тег с таким названием уже существует.")
        return name
