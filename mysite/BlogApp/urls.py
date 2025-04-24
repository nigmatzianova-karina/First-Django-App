from django.urls import path
from .views import  (ArticleListView,
                     ArticleDetailView,
                     LatestArticleFeed,
                     )

app_name = "BlogApp"

urlpatterns = [
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path("articles/latest/feed/", LatestArticleFeed(), name="articles-feed"),
]
