from django.db.models import Avg, Sum, Max, Min, Count
from django.core.management import BaseCommand
from shopapp.models import Product, Order


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Start Demo select fields")

        # result = Product.objects.filter(
        #     name__contains = "phone",
        # ).aggregate(
        #     Avg("price"),
        #     Max("price"),
        #     min_price = Min("price"),
        #     count=Count("id"),
        # )
        # print(result)

        orders = Order.objects.annotate(
            total=Sum("products__price", default=0),
            products_count=Count("products"),
        )

        for order in orders:
            print(
                f"Order #{order.id} "
                f"with {order.products_count} "
                f"products worth {order.total}"
            )

        self.stdout.write(self.style.SUCCESS(f"DONE"))