from django import forms
from django.core.exceptions import ValidationError
from django.forms import BooleanField

from .models import Category, Product

FORBIDDEN_WORDS = ["казино", "криптовалюта", "крипта", "биржа", "дешево", "бесплатно", "обман", "полиция", "радар"]


def validate_forbidden_words(value):
    if value:
        found_words = []
        value_lower = value.lower()
        for word in FORBIDDEN_WORDS:
            if word in value_lower:
                found_words.append(word)

        if found_words:
            raise ValidationError(f"Обнаружены запрещённые слова {', '.join(found_words)}")

    return value


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования товаров"""

    class Meta:
        model = Product
        fields = ["name", "description", "image", "category", "price"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Выберите категорию"

        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if name:
            validate_forbidden_words(name)

        return name

    def clean_description(self):
        description = self.cleaned_data.get("description")

        if description:
            validate_forbidden_words(description)

        return description

    def clean_price(self):
        price = self.cleaned_data.get("price")

        if price is None:
            raise ValidationError("Укажите цену товара")

        if price < 0:
            raise ValidationError("Цена должна быть положительным числом")

        return price

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if image and hasattr(image, "content_type"):
            content_type = image.content_type
            if content_type not in ("image/png", "image/jpeg"):
                raise ValidationError("Поддерживаются форматы только JPEG и PNG")

            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Файл слишком большой")

        return image
