from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core import serializers

from .models import User, Post, Like, Followers


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

#view code for adding a new post
#maybe it requires a decorater to confirm/check user is logged in. 
@csrf_exempt
@login_required(login_url='/login/') 
def createpost(request):
    print(request)
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        post = data['post']
        userId = data['userId']
        user = User.objects.get(pk = int(userId))
        print(user)
        #pretty sure I need to grab the user from the DB instead of frontend. -> yes you do when playing in shell i didnt get an instance, i just forced a value in name field which is incorrect. 
        newpost = Post(post=post, user_id=user)
        newpost.save()
        return JsonResponse({"message": "Post created successfully."}, status=201)
    else:
         return JsonResponse({"message": "Failed to save post"}, status=201)

#code for retrieving all the posts
@login_required(login_url='/login/') 
def viewposts(request):
    print(request)
    if request.method == "GET":
        posts = Post.objects.all()
        #print(posts)
        posts = posts.order_by("-created_at").all()
        posts = posts.exclude(user_id=None)
        print(posts)
        return JsonResponse([post.serialize() for post in posts], safe=False)

def profile(request, user_id):  
        return render(request, "network/profile.html")

def profileposts(request, user_id): #trigger this url with a seperate component. 
    if request.method == "GET":
        posts = Post.objects.filter(user_id = user_id).all()
        #print(posts)
        posts = posts.order_by("-created_at").all()
        print(posts)
        return JsonResponse([post.serialize() for post in posts], safe=False)

def profilefollowers(request, user_id): #trigger this url with a seperate component. 
    if request.method == "GET":
        followers = Followers.objects.filter(user_id = user_id).count()
        #print(posts)
        print(followers)
        return JsonResponse(followers, safe=False)