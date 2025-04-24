from random import choices
from string import ascii_letters

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from .models import Product, Order
from .utils import add_two_number

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_number(2, 3)
        self.assertEqual(result, 5)

class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testik",
                                            password="qwerty123",)
        content_type = ContentType.objects.get_for_model(Product)
        permission = Permission.objects.get(
            codename="add_product",
            content_type=content_type,
        )
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "Nice table",
                "discount": "10",
            },
            HTTP_USER_AGENT='Mozilla/5.0',
        )

        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )

class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(csl) -> None:
        csl.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk}),
            HTTP_USER_AGENT = 'Mozilla/5.0'
        )
        self.assertEqual(response.status_code, 200)

    def test_check_content_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk}),
            HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertContains(response, self.product.name)

class ProductsListViewTestCase(TestCase):
    fixture = [
        "products-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products_list.html")

class OrderListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testik",
                                            password="qwerty123")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:order_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertContains(response, "Orders")

    def test_orders_view_for_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

class OrderDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username="testik",
                                            password="qwerty123",)
        content_type = ContentType.objects.get_for_model(Order)
        permission = Permission.objects.get(
            codename="view_order",
            content_type=content_type,
        )
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(delivery_address="test 8",
                                          promocode="TEST20",
                                          user=self.user)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk}),
            HTTP_USER_AGENT = 'Mozilla/5.0'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertTrue(
            Order.objects.filter(pk=self.order.pk).exists()
        )

class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "orders-fixtures.json",
        "products-fixtures.json",
        "users-fixtures.json",
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse("shopapp:products_export"),
            HTTP_USER_AGENT='Mozilla/5.0'
        )

        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]

        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data
        )


class OrderExportViewTestCase(TestCase):
    fixtures = [
        "orders-fixtures.json",
        "products-fixtures.json",
        "users-fixtures.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username="testik",
                                            password="qwerty123",)
        permission = Permission.objects.get(
            codename="can_stuff",
        )
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.user)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()


    def test_get_orders_view(self):
        response = self.client.get(
            reverse("shopapp:order_export"),
            HTTP_USER_AGENT='Mozilla/5.0'
        )

        self.assertEqual(response.status_code, 200)

        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user,
                "products": order.products,
            }
            for order in orders
        ]

        orders_data = response.json()
        self.assertEqual(
            orders_data["orders"],
            expected_data
        )

