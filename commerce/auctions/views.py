from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import User , Auction, Bid, Comment, Watchlist, Category
from .forms import AuctionForm
from decimal import Decimal,InvalidOperation
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError 
from datetime import timedelta
from django.utils import timezone 


def index(request):
    listings = Auction.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required 
def CreateAuction(request):
    if request.method == "POST":
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.current_price = listing.starting_price
            days = int(form.cleaned_data['duration'])
            listing.end_time = timezone.now() + timedelta(days=days)
            listing.save()
            messages.success(request, "Auction created successfully!")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AuctionForm()
        
    return render(request, "auctions/create_auction.html", {
        "form": form
    })

def listings_details(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    if request.method == "POST"and request.user.is_authenticated:
        if "watchlist" in request.POST:
            watchlist_item, created = Watchlist.objects.get_or_create(
                user=request.user,
                auction=auction
            )
  
            
            if not created:
                watchlist_item.delete()  # Remove from watchlist if it already exists
        
        elif "bid" in request.POST:
            bid_amount = Decimal(request.POST.get("bid_amount", ))
            current_price = auction.current_price if auction.current_price > 0 else auction.starting_price

            if bid_amount > auction.starting_price and bid_amount > current_price:
                Bid.objects.create(
                    auction=auction,
                    user=request.user,
                    amount=bid_amount
                )
                auction.current_price = bid_amount
                auction.save()
            else:
                messages.error(request, "Bid amount must be greater than the current price.")

        elif "close_auction" in request.POST and auction.owner == request.user:
            auction.is_active = False
            highest_bid = auction.bids.order_by('-amount').first()
            if highest_bid:
                auction.winner = highest_bid.user
            auction.save()

        elif "comment" in request.POST:
            Comment.objects.create(
                user=request.user,
                auction=auction,
                content=request.POST.get("comment_content")
            )
    is_watchlisted = False
    if request.user.is_authenticated:
        is_watchlisted = Watchlist.objects.filter(user=request.user, auction=auction).exists()
    context = {
        "auction": auction,
        "is_watchlisted": is_watchlisted,
        "watchlist": is_watchlisted,
        "bids": auction.bids.order_by('-timestamp'),
        "highest_bid": auction.bids.order_by('-amount').first(),
        "minimum_bid": auction.get_minimum_bid(),
        "bid_count": auction.get_bid_count(),
        "comments": auction.comments.all(),
        "is_owner": request.user == auction.owner if request.user.is_authenticated else False,
        "is_winner": request.user == auction.winner if request.user.is_authenticated and auction.winner else False,

    }
    return render(request, "auctions/listing_details.html", context)

@login_required
def watchlist(request):
    if request.user.is_authenticated:
        watchlist_items = Watchlist.objects.filter(user=request.user)
        return render(request, "auctions/watchlist.html", {
            "watchlist_items": watchlist_items
        })
    else:
        messages.error(request, "You must be logged in to view your watchlist.")
        return HttpResponseRedirect(reverse("login"))

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_listings(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = Auction.objects.filter(
        category=category, 
        is_active=True)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })   

@login_required
def place_bid(request, auction_id):
    """Handle bid placement"""
    auction = get_object_or_404(Auction, id=auction_id)
    
    if request.method == 'POST':
        try:
            bid_amount = Decimal(request.POST.get('bid_amount', '0'))
        except (InvalidOperation, ValueError):
            messages.error(request, 'Please enter a valid bid amount.')
            return redirect('listing_detail', auction_id=auction_id)
        
        # Check if auction is active
        if not auction.is_active:
            messages.error(request, 'This auction is no longer active.')
            return redirect('listing_detail', auction_id=auction_id)
        
        # Check if user is the owner
        if auction.owner == request.user:
            messages.error(request, 'You cannot bid on your own auction.')
            return redirect('listing_detail', auction_id=auction_id)
        
        # Validate bid amount
        minimum_bid = auction.get_minimum_bid()
        if bid_amount < minimum_bid:
            messages.error(request, f'Bid must be at least ${minimum_bid}.')
            return redirect('listing_detail', auction_id=auction_id)

        try:
            # Create the bid
            bid = Bid.objects.create(
                auction=auction,
                user=request.user,
                amount=bid_amount
            )
            messages.success(request, f'Your bid of ${bid_amount} has been placed successfully!')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, 'An error occurred while placing your bid. Please try again.')

    return redirect('auction_detail', auction_id=auction_id)

@login_required
def close_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    if request.user != auction.owner:
        return HttpResponseForbidden("You can only close your own auctions.")
    
    if not auction.is_active:
        messages.error(request, "This auction is already closed.")
        return redirect('listing_details', auction_id=auction_id)
    
    auction.is_active = False
    highest_bid = auction.bids.order_by('-amount').first()
    if highest_bid:
        auction.winner = highest_bid.user
    auction.save()
    
    messages.success(request, "Auction closed successfully.")
    return redirect('listing_details', auction_id=auction_id)