from shopapp.models import Product

from django.core.management import BaseCommand

class Command(BaseCommand):
    """
    Creates products
    """
    def handle(self, *args, **options):
        self.stdout.write("Creates products")

        products_name = [
            "Laptop",
            "Desktop",
            "Phone",
        ]
        for name in products_name:
            product, created = Product.objects.get_or_create(name=name)
            self.stdout.write(f"Created product {product.name}")

        self.stdout.write(self.style.SUCCESS("Products created!"))