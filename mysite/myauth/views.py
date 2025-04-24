from random import random

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.utils.translation import gettext_lazy as _, ngettext
from .forms import ProfileForm
from .models import Profile


class HelloView(View):
    welcome_message = _("Welcome, Hello world!")

    def get(self, request: HttpRequest):
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)

        return response


class AboutMeView(UpdateView):
    template_name = "myauth/about_me.html"
    model = Profile
    fields = ("avatar",)

    success_url = reverse_lazy("myauth:about-me")

    def get_object(self, queryset=None):
        return self.request.user.profile


# class ChangeAvatarView(UserPassesTestMixin, LoginRequiredMixin, View):
#     def test_func(self):
#         return self.request.user.is_staff or (self.get_object().user == self.request.user)
#
#
#     def get(self, request: HttpRequest, *args, **kwargs):
#         profile = request.user.profile
#         avatar_url = profile.avatar.url if profile.avatar else "static/uploads/avatars/default.jpg"
#         context = {
#             "form": ProfileForm(instance=profile),
#             "avatar": avatar_url,
#         }
#         return render(request, "myauth/update_avatar.html", context=context)
#
#     def post(self, request: HttpRequest, *args, **kwargs):
#         profile = request.user.profile
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect("myauth:about-me")
#
#         avatar_url = profile.avatar.url if profile.avatar else "static/uploads/avatars/default.jpg"
#         context = {
#             "form": ProfileForm(instance=profile),
#             "avatar": avatar_url,
#         }
#         return render(request, "myauth/update_avatar.html", context=context )

class AvatarUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_staff or (self.get_object().user == self.request.user)

    model = Profile
    template_name = "myauth/update_avatar.html"
    form_class = ProfileForm

    def get_success_url(self):
        return reverse("myauth:users")


class UserDetailView(DetailView):
    template_name = "myauth/user_details.html"
    queryset = User.objects.select_related("profile")
    context_object_name = "user"


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)

    if user:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", {"error": "Invalid login or password"})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

@cache_page(120)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


class UsersListView(ListView):
    template_name = "myauth/user_list.html"
    context_object_name = "user_list"
    queryset = User.objects.all()
