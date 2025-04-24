from django.db import models
from django.urls import reverse

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(null=False, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=40)

class Tag(models.Model):
    name = models.CharField(max_length=20)

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(null=False, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

    def get_absolute_url(self):
        return reverse("BlogApp:article", kwargs={"pk": self.pk})

