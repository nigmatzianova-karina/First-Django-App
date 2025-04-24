from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start Demo select fields")

        result = Product.objects.filter(
            name__contains = "phone",
        ).update(discount=10)

        print(result)

        # info = [
        #     ("phone 1", 19),
        #     ("phone 2", 29),
        #     ("phone 3", 39),
        # ]
        #
        # products = [
        #     Product(name=name, price=price)
        #     for name, price in info
        # ]
        #
        # result = Product.objects.bulk_create(products)
        #
        # for obj in result:
        #     print(obj)

        self.stdout.write(self.style.SUCCESS(f"DONE"))