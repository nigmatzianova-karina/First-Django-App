from django.contrib.sitemaps import Sitemap

from .models import Product

class ShopSitemap(Sitemap):
    changefreq = "never"
    priority = 0.9

    def items(self):
        return Product.objects.order_by("name")

    def lastmod(self, obj: Product):
        return obj.created_at
