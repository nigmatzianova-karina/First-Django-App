from django.contrib.auth.views import LoginView
from django.urls import path
# from .views import login_view, logout_view,
from .views import (
    set_cookie_view,
    get_cookie_view,
    get_session_view,
    set_session_view,
    MyLogoutView,
    AboutMeView,
    RegisterView,
    FooBarView,
    UsersListView,
    AvatarUpdateView,
    UserDetailView,
    HelloView,
)

app_name = "myauth"

urlpatterns = [
    # path("login/", login_view, name="login"),
    path(
        "login/",
        LoginView.as_view(
            template_name="myauth/login.html",
            redirect_authenticated_user=True,
        ),
        name="login"
    ),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("hello/", HelloView.as_view(), name="hello"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("avatar-update/<int:pk>/", AvatarUpdateView.as_view(), name="avatar-update"),
    path("register/", RegisterView.as_view(), name="register"),
    path("users/", UsersListView.as_view(), name="users"),
    path("user-details/<int:pk>/", UserDetailView.as_view(), name="user-details"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]