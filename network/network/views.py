from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Follow    


def index(request):
    posts = Post.objects.all()
    
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')   
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user)
    
    # Pagination for profile posts
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate actual counts
    followers_count = profile_user.followers_count()
    following_count = profile_user.following_count()
    
    # Check if current user is following this profile user
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = request.user.is_following(profile_user)

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,  # Changed from posts to page_obj
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    })


@login_required
def following(request):
    # Get users that current user follows
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=following_users)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


@login_required
@csrf_exempt
def toggle_follow(request, username):
    if request.method == "POST":
        profile_user = get_object_or_404(User, username=username)
        
        if request.user == profile_user:
            return JsonResponse({"error": "Cannot follow yourself"}, status=400)
        
        follow_obj, created = Follow.objects.get_or_create(
            follower=request.user,
            following=profile_user
        )
        
        if not created:
            # Already following, so unfollow
            follow_obj.delete()
            is_following = False
        else:
            # Just started following
            is_following = True
        
        return JsonResponse({
            "is_following": is_following,
            "followers_count": profile_user.followers_count()
        })
    
    return JsonResponse({"error": "POST request required"}, status=400)


@login_required
@csrf_exempt
def toggle_like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        
        if request.user in post.likes.all():
            # Unlike the post
            post.likes.remove(request.user)
            liked = False
        else:
            # Like the post
            post.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            "liked": liked,
            "like_count": post.like_count()
        })
    
    return JsonResponse({"error": "POST request required"}, status=400)


@login_required
@csrf_exempt
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user owns this post
    if request.user != post.user:
        return JsonResponse({"error": "Cannot edit another user's post"}, status=403)
    
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        
        if not content:
            return JsonResponse({"error": "Post content cannot be empty"}, status=400)
        
        if len(content) > 280:
            return JsonResponse({"error": "Post content cannot exceed 280 characters"}, status=400)
        
        post.content = content
        post.save()
        
        return JsonResponse({
            "success": True,
            "content": post.content
        })
    
    return JsonResponse({"error": "POST request required"}, status=400)


@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        
        # Validate content
        if not content:
            # Get posts for index page with error
            posts = Post.objects.all()
            paginator = Paginator(posts, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            return render(request, "network/index.html", {
                "page_obj": page_obj,
                "error": "Post content cannot be empty."
            })
        
        if len(content) > 280:
            # Get posts for index page with error
            posts = Post.objects.all()
            paginator = Paginator(posts, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            return render(request, "network/index.html", {
                "page_obj": page_obj,
                "error": "Post content cannot exceed 280 characters."
            })
        
        # Create new post
        post = Post.objects.create(
            user=request.user,
            content=content
        )
        
        return HttpResponseRedirect(reverse("index"))
    
    # If GET request, redirect to index
    return HttpResponseRedirect(reverse("index"))


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