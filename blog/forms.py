from django import forms

from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    """Форма для создания и редактирования блога"""

    class Meta:
        model = BlogPost
        fields = ("title", "content", "preview", "is_published")
