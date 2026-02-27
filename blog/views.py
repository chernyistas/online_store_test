from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from blog.forms import BlogPostForm
from blog.models import BlogPost


class BlogPostListView(ListView):
    """Список опубликованных статей блога"""

    model = BlogPost
    context_object_name = "blogs"
    paginate_by = 6

    def get_queryset(self) -> QuerySet[BlogPost]:
        """Возвращает QuerySet только опубликованных статей"""
        return super().get_queryset().filter(is_published=True).order_by("-created_at")


class BlogPostDetailView(DetailView):
    """Детально одна статья блога"""

    model = BlogPost
    context_object_name = "blog"

    def get_object(self, queryset=None) -> BlogPost:
        """Обновление количества просмотров"""
        obj = super().get_object(queryset)
        obj.views_count += 1

        if obj.views_count == 100:
            send_mail(
                subject=f'Статья "{obj.title}" достигла 100 просмотров!',
                message=f'Поздравляем! Статья "{obj.title}" достигла 100 просмотров.',
                from_email="noreplay@onlinestore.com",
                recipient_list=["admin@onlinestore.com"],
                fail_silently=True,
            )
        obj.save(update_fields=["views_count"])
        return obj


class BlogPostCreateView(PermissionRequiredMixin, CreateView):
    """Создание статьи для блога"""

    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy("blog:blogpost_list")
    permission_required = "blog.add_blogpost"


class BlogPostUpdateView(PermissionRequiredMixin, UpdateView):
    """Редактирование статьи для блога"""

    model = BlogPost
    form_class = BlogPostForm
    permission_required = "blog.change_blogpost"

    def get_success_url(self):
        """Перенаправление на страницу статьи после редактирования"""
        return reverse_lazy("blog:blogpost_detail", kwargs={"pk": self.object.pk})


class BlogPostDeleteView(PermissionRequiredMixin, DeleteView):
    """Удаление статьи для блога"""

    model = BlogPost
    success_url = reverse_lazy("blog:blogpost_list")
    permission_required = "blog.delete_blogpost"
