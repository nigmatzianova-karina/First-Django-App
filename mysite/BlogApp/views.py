from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from .models import Article


class ArticleListView(ListView):
    queryset = (
        Article.objects
        .select_related("author", "category")
        .prefetch_related("tags")
        .defer("content")
        .filter(pub_date__isnull=False)
        .order_by("-pub_date")
    )

class ArticleDetailView(DetailView):
    model = Article


class LatestArticleFeed(Feed):
    title = "Blog articles (latest)"
    description = 'Update of changes and additions blog articles'
    link = reverse_lazy("BlogApp:articles")

    def items(self):
        return (
            Article.objects
            .select_related("author", "category")
            .prefetch_related("tags")
            .defer("content")
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:200]
