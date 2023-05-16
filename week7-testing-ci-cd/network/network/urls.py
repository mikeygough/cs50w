
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user/<str:username>", views.user_view, name="user_view"),
    path("following", views.following_view, name="following_view"),

    # API Routes
    path("editpost", views.edit_post, name="edit_post"),
    path("likepost", views.like_post, name="like_post")
]
