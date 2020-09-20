
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createpost", views.createpost, name="createpost"),
    path("viewposts", views.viewposts , name="viewposts"),
    path("profile/<int:user_id>", views.profile , name="profile"),
    path("profileposts/<int:user_id>", views.profileposts , name="profileposts")
]
