from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Отображает главную страницу каталога."""
    return render(request, "home.html")


def contact(request: HttpRequest) -> HttpResponse:
    """Страница контактов с формой обратной связи."""
    if request.method == "POST":
        name: Optional[str] = request.POST.get("name")
        phone: Optional[str] = request.POST.get("phone")
        message: Optional[str] = request.POST.get("message")
        return HttpResponse(f"Спасибо {name}, ваше сообщение {message} отправлено! с вами свяжутся  по {phone}")
    return render(request, "contact.html")
