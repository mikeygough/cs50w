from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

import datetime

from .models import User, Listing, Comment, Watchlist, Bid
from .forms import CreateListingForm, CreateBidForm, CreateCommentForm


def index(request):
    all_listings = Listing.objects.all()
    all_bids = Bid.objects.all()
    return render(request, "auctions/index.html", {
        "all_listings": all_listings,
        "all_bids": all_bids
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


def create_listing(request):
    if request.method == "POST":
        user = User.objects.get(pk=int(request.user.id))
        listing_form = CreateListingForm(request.POST)
        if listing_form.is_valid():
            submitted_listing = listing_form.save(commit=False)
            # add user, listing and timestamp values
            submitted_listing.created_at = datetime.datetime.now()
            submitted_listing.auction_open = True
            submitted_listing.creator = user
            # save form
            submitted_listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        listing_form = CreateListingForm()

    return render(request, "auctions/create_listing.html", {
        'listing_form': listing_form
    })


def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    comments = listing.comments.all()
    highest_bid = 0
    # get highest bid, implemented on model
    if listing.highest_bid() == None:
        highest_bid += listing.starting_bid
    else:
        highest_bid = listing.highest_bid()

    if request.user.is_authenticated:
        if User.objects.get(pk=int(request.user.id)):
            # get watchlist items backwards from User object, flatten to list
            watchlist = User.objects.get(pk=int(request.user.id)).watchlist_set.all().values_list('listing', flat=True)
        else:
            # if no objects in wantlist, just send empty list
            watchlist = []

        if request.method == "POST":
            # get user
            user = User.objects.get(pk=int(request.user.id))

            # CLOSE AUCTION
            if 'closeauction' in request.POST:
                listing.auction_open = False
                listing.winner = Bid.objects.filter(listing=listing).get(bid=highest_bid).user
                listing.save()

            # WATCHLIST
            if 'additem' in request.POST:
                i = Watchlist(user=user, listing=listing)
                i.save()
            elif 'removeitem' in request.POST:
                Watchlist.objects.get(listing=listing).delete()

            # COMMENT
            comment_form = CreateCommentForm(request.POST)
            if comment_form.is_valid():
                # preliminary form save
                submitted_comment = comment_form.save(commit=False)
                # add user, listing and timestamp values
                submitted_comment.listing = listing
                submitted_comment.author = user
                submitted_comment.created_at = datetime.datetime.now()
                # save form
                submitted_comment.save()

            # BID
            bid_form = CreateBidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.cleaned_data['bid']
                if bid < float(listing.starting_bid) or bid < highest_bid:
                    return HttpResponse("Bid must be larger than the current largest bid")
                else:
                    # preliminary form save
                    submitted_bid = bid_form.save(commit=False)
                    # add user and listing values
                    submitted_bid.user = user
                    submitted_bid.listing = listing
                    # save form
                    submitted_bid.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        else:
            # GET
            bid_form = CreateBidForm()
            comment_form = CreateCommentForm()

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "watchlist": watchlist,
                "highest_bid": highest_bid,
                "bid_form": bid_form,
                "comment_form": comment_form,
            })
    else: # not authenticated
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "highest_bid": highest_bid,
            })


def watchlist(request, user_id):

    watchlist = Watchlist.objects.filter(user__id=user_id)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


def categories(request):
    # returns a list of tuples
    categories = Listing.LISTING_CATEGORIES
    # create list of categories
    categories = [lis[1].lower() for lis in categories]
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_id):
    # returns a list of tuples
    categories = Listing.LISTING_CATEGORIES
    # create space for correct db category
    db_code = []
    # if category in list of categories
    for cat in categories:
        # need to capitalize
        if str(category_id).capitalize() in cat:
            db_code.append(cat)
    # fetch objects with same category, reformatted for db query
    listings = Listing.objects.filter(category__contains=db_code[0][0])
    return render(request, "auctions/category.html", {
        "category": category_id,
        "listings": listings
    })