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
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Post, Like, Follower


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
        return render(request, "network/profile.html", {'user_id': user_id})

def profileposts(request, user_id): #trigger this url with a seperate component. 
    if request.method == "GET":
        posts = Post.objects.filter(user_id = user_id).all()
        #print(posts)
        posts = posts.order_by("-created_at").all()
        print(posts)
        return JsonResponse([post.serialize() for post in posts], safe=False)

def profilefollowers(request, user_id): #trigger this url with a seperate component. 
    if request.method == "GET":
        followercount = Follower.objects.filter(user_id = user_id).count()
        print(followercount)
        followingcount = Follower.objects.filter(follower_id = user_id).count()
        print(followingcount)
        logged_in_user_id = request.user.id
        #logic to deterime if profile page is logged in users and if not, is logged in user a follower?
        is_logged_in_users_profilepage = False
        #is_profile_following_logged_in_user  = False
        #Is logged in user a follower? Need a loop. 
        try:
            is_profile_following_logged_in_user = Follower.objects.get(follower_id = logged_in_user_id, user_id = user_id)     #filter(follower_id = user_id, ).values('follower')#some code to just get this userId
            print(is_profile_following_logged_in_user)
            is_profile_following_logged_in_user = True
        except ObjectDoesNotExist:
            is_profile_following_logged_in_user = False

        print("The logged in user ID is:", logged_in_user_id)
        print("The profile page been visited's user ID is:", user_id)
        print("is_profile_following_logged_in_user",is_profile_following_logged_in_user)

        if logged_in_user_id == user_id:
            is_logged_in_users_profilepage = True
        else:
            is_logged_in_users_profilepage = False


    print(f"Is this the users profile page:", is_logged_in_users_profilepage)
    print(f"Is the logged in user a follower:", is_profile_following_logged_in_user)

    profile_data = {
        'is_logged_in_users_profilepage' : is_logged_in_users_profilepage,
        'is_profile_following_logged_in_user' : is_profile_following_logged_in_user,
        'followingcount' : followingcount,
        'followercount' : followercount
    }
        
    return JsonResponse(profile_data, safe=False)

@csrf_exempt
def newfollow(request, user_id):
    if request.method == "PUT":
        follower = Follower(follower_id=request.user.id, user_id=user_id)
        follower.save()
        return JsonResponse("new follow added", safe=False)

@csrf_exempt
def unfollow(request, user_id):
    if request.method == "PUT":
        removed_this_follower = Follower.objects.get(follower_id=request.user.id, user_id=user_id)
        removed_this_follower.delete()
        return JsonResponse("unfollowed", safe=False)

@login_required(login_url='/login/') 
def following(request):
    return render(request, "network/following.html")

def following_profile_posts(request):
    if request.method == "GET":
        logged_in_user_id = request.user.id
        print(logged_in_user_id)
        #get following profile's user ids
        following_ids = Follower.objects.filter(follower_id=logged_in_user_id).values('user_id')
        print("These are the userIds of the profiles the logged in user followers:", following_ids)
        posts = Post.objects.filter(user_id_id__in=following_ids)
        posts = posts.order_by("-created_at").all()
        print(posts)
        return JsonResponse([post.serialize() for post in posts], safe=False)

@csrf_exempt
@login_required(login_url='/login/') 
def edit_post(request, user_id):
    if not request.user.id == user_id:
        return JsonResponse("Cannot edit other users posts", safe=False)
    if request.method == "PUT":
        data = json.loads(request.body)
        postId = data.get('post_id')
        postbody = data.get('post')
        print(data)
        post = Post.objects.get(pk=postId)
        print(post)
        post.post = postbody
        post.save()
        return JsonResponse("edit successful", safe=False)

@csrf_exempt
@login_required(login_url='/login/')
def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    logged_in_user = User.objects.get(pk=request.user.id)
    if request.method == "GET":
        print(request)
        try:
            likes = Like.objects.filter(post=post).count()
        except:
            likes = 0
        try: 
            user_like = Like.objects.get(user=logged_in_user, post=post)
            user_like = True
            print(user_like)
        except:
            user_like = False
        like_data = {
                "likes" : likes,
                "user_like" : user_like
            }
        print(like_data)
        return JsonResponse(like_data, safe=False)
    
    if request.method == "POST":
        like = Like(post=post, user=logged_in_user)
        like.save()
        return JsonResponse("posted", safe=False)
    #One more for puts to remove like. 
    if request.method == "PUT": 
        try:
            like = Like.objects.get(post=post, user=logged_in_user)
            like.delete()
        except:
            print("No like to delete")
        return JsonResponse("like deleted", safe=False)
        









    




