from typing import Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from catalog.models import ContactInfo, Product


def home(request: HttpRequest) -> HttpResponse:
    """Отображает главную страницу каталога."""
    latest_products = Product.objects.order_by("-created_at")[:5]
    print("Последние 5 продуктов")
    for p in latest_products:
        print(f"- {p.name} ({p.price} руб.) | {p.category.name}")
    return render(request, "home.html", {"latest_products": latest_products})


def contact(request: HttpRequest) -> HttpResponse:
    """Страница контактов с формой обратной связи."""
    if request.method == "POST":
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

    context = {
        "store_contacts": {
            "name": "Online Store",
            "email": "feedback@store.ru",
            "phone": "8-098-765-43-21",
            "address": "Московская область, Мытищи, улица Самая Хорошая",
        },
    }
    return render(request, "contact.html", context)
