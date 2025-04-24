from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products, save_csv_orders
from .models import Product, Order, ProductImages
from .admin_mixin import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInLine(admin.TabularInline):
    model = Product.orders.through

class ProductInLines(admin.StackedInline):
    model = ProductImages


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset:QuerySet):
    queryset.update(archived=True)

@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset:QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "exropt_csv",
    ]
    inlines = [
        OrderInLine,
        ProductInLines,
    ]
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name",
    ordering = "pk", "name"
    search_fields = "name", "description"

    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("collapse", "wide",),
        }),
        ("Images", {
            "fields": ("preview", ),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options, field 'archived' is for soft delete."
        }),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context=context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
            "form": form,
            }
            return render(request, "admin/csv_form.html", context=context, status=400)

        save_csv_products(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data form CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import_products_csv/",
                self.import_csv,
                name="import_products_csv",
            )
        ]
        return new_urls + urls


# admin.site.register(Product, ProductAdmin)


# class ProductInLine(admin.TabularInline):
class ProductInLine(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        ProductInLine,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"


    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")


    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username


    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context=context)

        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
            "form": form,
            }
            return render(request, "admin/csv_form.html", context=context, status=400)

        save_csv_orders(
            form.files["csv_file"].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data form CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import_orders_csv/",
                self.import_csv,
                name="import_orders_csv",
            )
        ]
        return new_urls + urls

