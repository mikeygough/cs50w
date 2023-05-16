import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import datetime

from .models import User, Post, UserFollowing, UserLikes
from .forms import CreatePostForm


def index(request):
    if request.method == "POST":
        user = User.objects.get(pk=int(request.user.id))
        post_form = CreatePostForm(request.POST)
        if post_form.is_valid():
            submitted_post = post_form.save(commit=False)
            # add additional information to form (hidden fields)
            submitted_post.created_at = datetime.datetime.now()
            submitted_post.author = user
            # save form
            submitted_post.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        post_form = CreatePostForm()
        # get all posts
        all_posts = Post.objects.all().order_by(
                    '-created_at__year', '-created_at__month', '-created_at__day', '-created_at__hour', '-created_at__minute')
        # instantiate Paginator, 10 posts
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # get all liked posts from signed in user
        # flatten to list
        try:
            all_likes = UserLikes.objects.all().filter(user_id=request.user).values_list('liked_post_id', flat=True)
        except:
            all_likes = None

    return render(request, "network/index.html", {
        'page_obj': page_obj,
        'post_form': post_form,
        'all_posts': all_posts,
        'all_likes': all_likes
    })

@csrf_exempt
@login_required
def edit_post(request):

    # editing a post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get data
    data = json.loads(request.body)
    new_body = data['new_body']
    post_id = data['post_id']

    # edit the post in the database
    post = Post.objects.get(pk=post_id)
    post.body = new_body
    post.save()

    # return HttpResponseRedirect(reverse("index"))
    return JsonResponse({"message": "Success."}, status=201)


@csrf_exempt
@login_required
def like_post(request):

    # editing a post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get data
    data = json.loads(request.body)
    post_id = data['post_id']
    post_author = data['author']
    post_liker = request.user
    # if like relationship already exists

    uid = User.objects.get(username=post_author)
    pid = Post.objects.get(pk=post_id)
    if UserLikes.objects.filter(user_id=post_liker, liked_post_id=pid).exists():
        # print("Remove Like")
        # delete entry
        UserLikes.objects.get(user_id=post_liker, liked_post_id=pid).delete()
        # decrement likes
        post = Post.objects.get(pk=post_id)
        post.likes -= 1
        post.save()
    else:
        # print("Added Like")
        # create like relationship
        likes = UserLikes(user_id=post_liker, liked_post_id=pid)
        likes.save()
        # increment likes
        post = Post.objects.get(pk=post_id)
        post.likes += 1
        post.save()

    # return HttpResponseRedirect(reverse("index"))
    return JsonResponse({"message": "Success."}, status=201)


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


# profile page requirement
def user_view(request, username):
    try: # get user
        searched_user = User.objects.get(username=username)
    except:
        return render(request, "network/error.html", {
            "searched_user": username,
            "message": "does not exist."
        })

    try: # get posts from user and order reverse chronologically
        all_posts = Post.objects.all().filter(author=searched_user).order_by(
                    'created_at__year', 'created_at__month', 'created_at__day', 'created_at__hour', 'created_at__minute')
    except:
        # no posts
        pass
    # get following
    all_following = searched_user.following.all()
    # get followers
    all_followers = searched_user.followers.all()
    # if signed in user following searched_user, following = True
    if all_followers.filter(user_id=request.user.id).exists():
        # print(f"YES, {request.user.username} following {searched_user.username}")
        following = True
    else:
        # print(f"NO, {request.user.username} not following {searched_user.username}")
        following = False

    if request.method == "POST":
        # FOLLOW / UNFOLLOW
        if 'follow' in request.POST:
            # follow relationship
            x = UserFollowing(user_id=request.user, following_user_id=searched_user)
            x.save()
            # follower count
            searched_user.follower_count += 1
            searched_user.save()
            # following count
            active_user = User.objects.get(username=request.user.username)
            active_user.following_count += 1
            active_user.save()
        elif 'un' in request.POST:
            # following relationship
            UserFollowing.objects.get(user_id=request.user, following_user_id=searched_user).delete()
            # follower count
            searched_user.follower_count -= 1
            searched_user.save()
            # following count
            active_user = User.objects.get(username=request.user.username)
            active_user.following_count -= 1
            active_user.save()
        return HttpResponseRedirect(reverse("user_view", args=(searched_user.username, )))
    else:
        return render(request, "network/user.html", {
            'searched_user': searched_user,
            'all_posts': all_posts,
            'following': following,
        })


def following_view(request):
    # get following LIST
    all_following = request.user.following.all().values_list('following_user_id', flat=True)
    # get posts by those users
    all_posts = Post.objects.all().filter(author__in=all_following).order_by(
                    '-created_at__year', '-created_at__month', '-created_at__day', '-created_at__hour', '-created_at__minute')

    # instantiate Paginator, 10 posts
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        'page_obj': page_obj,
        'all_posts': all_posts,
    })