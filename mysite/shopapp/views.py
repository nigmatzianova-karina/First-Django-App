"""
View func for shop.

For products, orders, ...
"""
from timeit import default_timer
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from yaml import serialize

from .common import save_csv_products
from .forms import ProductForm, GroupForm
from .models import Product, Order, ProductImages
from .serializers import ProductSerializer, OrderSerializer
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging
from rest_framework.decorators import action
from rest_framework.request import Request
from csv import DictWriter

log = logging.getLogger(__name__)

class UserOrdersExportView(View):
    def get(self, request: HttpRequest, pk):
        cache_key = f"{pk}_user_orders_data_cache"
        orders_data = cache.get(cache_key)
        user = get_object_or_404(User, pk=pk)
        if orders_data is None:
            orders = Order.objects.filter(user=user)

            orders_data = [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "created_at": order.created_at,
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)

        return JsonResponse({"user_id": user.pk, "orders": orders_data})


class UserOrdersListView(ListView):
    template_name = "shopapp/users_orders_list.html"
    def get_queryset(self):
        user_id = self.kwargs.get("pk")

        self.owner = get_object_or_404(User, pk=user_id)

        return Order.objects.filter(user=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["owner"] = self.owner
        return context


class LatestProductsFeed(Feed):
    title = "Products (latest)"
    description = 'Update of changes and additions products'
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Product.objects
            .order_by("-name")[:5]
        )

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description[:100]


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    search_fields = [
        "delivery_address",
        "user",
        "products",
    ]
    ordering_fields = [
        "delivery_address",
        "user",
    ]

@extend_schema(description="Products Views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Set View for change Product
    Same info
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_fields = [
        "name",
        "price",
        "description",
        "discount",
        "archived",
    ]
    search_fields = [
        "name",
        "description",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]
    @method_decorator(cache_page(120))
    def list(self, *args, **kwargs):
        # print("HELLO PRODUCT LIST")
        return super().list(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_cdv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Contrnt-Disposition"] = f"attachment; filename = {filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "price",
            "description",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        methods=["post"],
        detail=False,
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by id",
        description="Retrieves **product**, return 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found")
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class ShopIndexView(View):
    def get(self, request: HttpRequest):
        products = [
            ('Laptop', 1999),
            ("Desktop", 5999),
            ("Phone", 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 12,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        print("shop index context", context)
        return render(request, "shopapp/shop_index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest):
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups_list.html", context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product_details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products_list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.select_related("user")

class ProductCreateView(PermissionRequiredMixin, CreateView):
    # def test_func(self):
    #     # return self.request.user.groups. filter(name="secret-group").exists()
    #     return self.request.user.is_superuser

    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        return super().form_valid(form)



class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            self.object = self.get_object()
            has_edit_perm = self.request.user.has_perm("shopapp.change_product")
            created_by_current_user = self.object.user == self.request.user
            return has_edit_perm and created_by_current_user

    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        for img in form.files.getlist("images"):
            ProductImages.objects.create(
                product=self.object,
                image=img
            )
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.success_url
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp.view_order", ]
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:order_list")


class ProductsExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": str(product.price),
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        # elem = products_data[0]
        # name = elem["nae"]
        # print("name:", name)

        return JsonResponse({"products":products_data})


class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk")

        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
            }
            for order in orders
        ]
        return JsonResponse({"orders":orders_data})