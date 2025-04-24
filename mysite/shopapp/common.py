from csv import DictReader
from io import TextIOWrapper

from django.contrib.auth.models import User

from shopapp.models import Product, Order



def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    orders = []
    for row in reader:
        user_id = row.get("user")
        user = User.objects.get(pk=user_id)
        order = Order(
            delivery_address=row.get('delivery_address'),
            promocode=row.get('promocode'),
            user=user,
        )
        orders.append(order)

    Order.objects.bulk_create(orders)

    for order in orders:
        product_id = row.get('products').split(',')
        products = Product.objects.filter(id__in=product_id)
        order.products.set(products)

    return orders
