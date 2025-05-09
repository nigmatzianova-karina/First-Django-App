from django import forms
from django.core import validators
from django.forms import ClearableFileInput, FileField

from .models import Product, Order
from django.contrib.auth.models import Group


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=1, max_value=100000, decimal_places=2)
#     description = forms.CharField(label="Product description",
#                                   widget=forms.Textarea(attrs={"rows": 5,
#                                                                "cols": 30}),
#                                   validators=[validators.RegexValidator(
#                                       regex=r"great",
#                                       message="Field must contain word 'great'",
#                                   )],
#                                   )

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"
    images = MultipleFileField()


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = "name", "price", "description", "discount", "preview"

    # images = forms.ImageField(
    #     widget=forms.ClearableFileInput(attrs={"multiple": True})
    # )
    # images = forms.FileField(
    #     widget=forms.FileInput(attrs={"multiple": True})
    # )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promocode", "user", "products"


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name',]


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
