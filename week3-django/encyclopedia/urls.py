from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("randompage", views.randompage, name="randompage"),
    path("<str:entry>", views.entry, name="entry"),
    path("wiki/<str:entry>", views.entry, name="entrylink"),
    path("search/", views.search, name="search"),
    path("newpage/", views.newpage, name="newpage"),
    path("editpage/<str:entry>", views.editpage, name="editpage")
]
