from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from catalog.models import Category, ContactInfo, Product

from .forms import ProductForm
from .services import get_products_by_category


class ProductListView(ListView):
    """Отображает главную страницу каталога с товарами"""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6
    ordering = ["-created_at"]

    def get_queryset(self):
        """Получаем номер текущей страницы"""
        page = self.request.GET.get("page", 1)
        cache_key = f"product_list_page_{page}"
        products = cache.get(cache_key)

        if products is None:
            products = super().get_queryset()
            cache.set(cache_key, products, 60 * 15)

        return products


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
        """Получает товара из кэша"""
        product_id = self.kwargs.get("pk")
        cache_key = f"product_detail_{product_id}"
        product = cache.get(cache_key)

        if not product:
            product = super().get_object(queryset)
            cache.set(cache_key, product, 60 * 15)

        return product


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
        product = form.save(commit=False)
        user = self.request.user
        product.owner = user
        product.save()

        for page in range(1, 101):
            cache.delete(f"product_list_page_{page}")

        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование продукта"""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:home")
    permission_required = "catalog.can_unpublish_product"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if not obj.owner == self.request.user:
            raise PermissionDenied

        return obj

    def form_valid(self, form):
        """Обрабатывает валидную форму"""
        response = super().form_valid(form)
        cache_key = f"product_detail_{self.object.pk}"
        cache.delete(cache_key)

        for page in range(1, 101):
            cache.delete(f"product_list_page_{page}")

        return response


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление продукта"""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if not (obj.owner == self.request.user or self.request.user.has_perm("catalog.can_unpublish_product")):
            raise PermissionDenied

        return obj

    def delete(self, request, *args, **kwargs):
        """Удаляем из кэша"""
        product_id = self.kwargs.get("pk")
        cache_key = f"product_detail_{product_id}"
        cache.delete(cache_key)

        response = super().delete(request, *args, **kwargs)

        for page in range(1, 101):
            cache.delete(f"product_list_page_{page}")

        return response


class CategoryProductListView(ListView):
    """Список товаров определенной категории"""

    model = Product
    template_name = "catalog/category_product_list.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        """Получает товары для текущей категории"""
        category_id = self.kwargs.get("pk")
        get_object_or_404(Category, pk=category_id)

        return get_products_by_category(category_id)

    def get_context_data(self, **kwargs):
        """Добавляем в шаблон название категории"""
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get("pk")
        category = get_object_or_404(Category, pk=category_id)

        context["category"] = category

        return context
