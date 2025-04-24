from django.contrib import admin


from .models import Article, Author, Tag, Category

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
     list_display = "id", "title", "pub_date", "content"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = "name", "bio"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "name",


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = "name",
