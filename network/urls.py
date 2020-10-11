
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
    path("profileposts/<int:user_id>", views.profileposts , name="profileposts"),
    path("profilefollowers/<int:user_id>", views.profilefollowers , name="profilefollowers"),
    path("newfollow/<int:user_id>", views.newfollow , name="newfollow"),
    path("unfollow/<int:user_id>", views.unfollow , name="unfollow"),
    path("following/", views.following, name="logged_in_user_following"),
    path("following_profiles_posts/", views.following_profile_posts, name="following_profile_posts")
]
