from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from catalog.models import ContactInfo, Product

from .forms import ProductForm


class ProductListView(ListView):
    """Отображает главную страницу каталога с товарами"""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6
    ordering = ["-created_at"]


class ContactView(TemplateView):
    """Страница контактов с формой обратной связи"""

    template_name = "catalog/contact.html"

    def post(self, request: HttpRequest, *args, **kwargs):
        """Обрабатывает POST-запрос формы контактов"""
        name: Optional[str] = request.POST.get("name")
        phone: Optional[str] = request.POST.get("phone")
        message: Optional[str] = request.POST.get("message")

        if name and message:
            ContactInfo.objects.create(
                name=f"Заявка: {name}",
                email="feedback@store.ru",
                phone=phone or "",
                address=message[:255],
            )
            contact_phone = phone or "email"
            messages.success(request, f"Спасибо {name}! Свяжемся по {contact_phone}")
            return redirect("catalog:contact")
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавляет контактные данные в контекст"""
        context = super().get_context_data(**kwargs)
        context["store_contacts"] = {
            "name": "Online Store",
            "email": "feedback@store.ru",
            "phone": "8-098-765-43-21",
            "address": "Московская область, Мытищи, улица Самая Хорошая",
        }
        return context


class ProductDetailView(DetailView):
    """Отображает страницу с подробной информацией о товаре"""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset: QuerySet = None) -> Product:
        """Получает объект товара по ID"""
        return super().get_object(queryset)


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание нового продукта"""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self) -> str:
        """Возвращает URL для перенаправления после успешного создания"""
        return reverse_lazy("catalog:product_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """Обрабатывает валидную форму"""
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование продукта"""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:home")


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление продукта"""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")
