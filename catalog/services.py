from catalog.models import Product


def get_products_by_category(category_id):
    """
    Возвращает все опубликованные товары указанной категории
    """
    products = Product.objects.filter(category_id=category_id, is_published=True).select_related("category", "owner")

    return products
