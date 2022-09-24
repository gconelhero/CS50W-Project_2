from sre_parse import CATEGORIES
from unicodedata import category
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.validators import get_available_image_extensions


from .models import User, ItemAuction, Bid, Comment, Watchlist
from datetime import datetime, timedelta
from djmoney.utils import Money
from pytz import timezone
import filetype
import mimetypes
VALID_IMAGE_MIMETYPES = [
    "image"
]

categories = ['Electronics', 'Collectibles', 'Others']

def valid_url_mimetype(url, mimetype_list=VALID_IMAGE_MIMETYPES):
    # http://stackoverflow.com/a/10543969/396300
    mimetype, encoding = mimetypes.guess_type(url)
    if mimetype:
        return any([mimetype.startswith(m) for m in mimetype_list])
    else:
        return False


def index(request):
    category = request.get_full_path().split('/')[1].capitalize()
    title_h2 = "Active Listings"
    print(category)
    if request.user.is_authenticated:
        watchlist_count = Watchlist.objects.all().filter(user=request.user).count
        watchlist = [watch.item_auction for watch in Watchlist.objects.all().filter(user=request.user)]
    else:
        watchlist_count = None
        watchlist = None
    listings = ItemAuction.objects.all().filter(active=1)
    for item in listings:
        if item.date_end <= datetime.now(timezone('US/Pacific')):
            item.active = 0
            item.save()
    if request.get_full_path() == '/electronics':
        listings = ItemAuction.objects.all().filter(category='Electronics', active=1)
    elif request.get_full_path() == '/collectibles':
        listings = ItemAuction.objects.all().filter(category='Collectibles', active=1)
    elif request.get_full_path() == '/others':
        listings = ItemAuction.objects.all().filter(category='Others', active=1)
    elif request.get_full_path() == '/all_listings':
        listings = ItemAuction.objects.all().order_by('date_end')
        title_h2 = "All Listings"
        category = "All"
    else:
        listings = ItemAuction.objects.all().filter(active=1)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "title_h2": title_h2,
        "watchlist_count": watchlist_count,
        "watchlist": watchlist,
        "category": category,
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

class FormItemAuction(forms.ModelForm):
    class Meta:
        model = ItemAuction

        fields = ['item_name', 'category', 'description', 'initial_price', 'date_end', 'image', 'image_url']

        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', }),
            'initial_price': "", # Defined in the views.py
            'date_end': forms.DateTimeInput(format=('%d-%m-%Y %H:%M'), attrs={'class': 'form-control datepicker', 'type': 'date'}),
            'image': forms.FileInput(),
            'iamge_url': forms.TextInput(attrs={'class': 'form-control'}),
        }   

        labels = {
            'item_name': 'Item Name',
            'category': 'Category',
            'description': 'Description',
            'initial_price': 'Initial Price',
            'date_end': 'Date & Time End',
            'image': 'Image File',
            'image_url': 'Image URL'
        }

class FormBid(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': "", # Defined in the views.py 
        }
        labels = {
            'amount': 'Amount',
        }

class FormComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your comment...',}),
        }
        labels = {
            'content': 'Comment Here!',
        }

def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    watchlist_count = Watchlist.objects.all().filter(user=request.user).count
    form = FormItemAuction()
    form.fields['initial_price'].widget.attrs = {'class': 'form-control', 'placeholder': '$0.00'}
    
    form.fields['image_url'].widget.attrs = {'class': ' image-url-input form-control', 'placeholder': 'Image URL','style': 'display:none'}
    form.fields['image'].label = ""
    form.fields['image_url'].label = ""
    if request.method == "POST":
        form = FormItemAuction(request.POST, request.FILES)
        form.fields['initial_price'].widget.attrs = {'class': 'form-control', 'placeholder': '$0.00'}
        form.fields['image_url'].widget.attrs = {'class': ' image-url-input form-control', 'placeholder': 'Image URL','style': 'display:none'}
        form.fields['image'].label = ""
        form.fields['image_url'].label = ""
        if form.is_valid():
            try:
                image_file = request.FILES.get('image')
                image_file_type = filetype.guess(image_file).mime
                print(image_file_type)
            except:
                image_file = None
                pass
            if form.cleaned_data['initial_price'] <= Money('0.00', 'USD'):
                return render(request, "auctions/create_listing.html", {
                    "form": form,
                    "title_h2": "Create Listing",
                    "title": "Create Listing",
                    "watchlist_count": watchlist_count,
                    "message": "Initial price must be greater than $0.00",
                })
            if form.cleaned_data['date_end'] - datetime.now(timezone('US/Pacific')) < timedelta(hours=24):
                return render(request, "auctions/create_listing.html", {
                        "form": form,
                        "title_h2": "Create Listing",
                        "title": "Create Listing",
                        "watchlist_count": watchlist_count,
                        "message": "The listing must be at least 24 hours long!"
                })
            if image_file == None :
                print(form.cleaned_data['image_url'])
                if form.cleaned_data['image_url'] == None:
                    return render(request, "auctions/create_listing.html", {
                        "form": form,
                        "title_h2": "Create Listing",
                        "title": "Create Listing",
                        "watchlist_count": watchlist_count,
                        "message": "You must either upload an image or provide an image url!"
                    })
                if not valid_url_mimetype(form.cleaned_data['image_url']):
                    return render(request, "auctions/create_listing.html", {
                        "form": form,
                        "title_h2": "Create Listing",
                        "title": "Create Listing",
                        "watchlist_count": watchlist_count,
                        "message": "Invalid image URL"
                    })
                else:
                    item = ItemAuction.objects.create(item_name=form.cleaned_data['item_name'],
                                                    category=form.cleaned_data['category'],
                                                    description=form.cleaned_data['description'],
                                                    initial_price=form.cleaned_data['initial_price'],
                                                    date_end=form.cleaned_data['date_end'],
                                                    image_url=form.cleaned_data['image_url'],
                                                    user=request.user)
                    item.save()
                    return HttpResponseRedirect(reverse("index"))
            else:
                print(image_file_type)
                if image_file_type.split('/')[0] != 'image':
                    return render(request, "auctions/create_listing.html", {
                        "form": form,
                        "title_h2": "Create Listing",
                        "title": "Create Listing",
                        "watchlist_count": watchlist_count,
                        "message": "File is not a image!"
                    })
                item = ItemAuction.objects.create(item_name=form.cleaned_data['item_name'],
                                                category=form.cleaned_data['category'],
                                                description=form.cleaned_data['description'],
                                                initial_price=form.cleaned_data['initial_price'],
                                                date_end=form.cleaned_data['date_end'],
                                                image=image_file,
                                                user=request.user)
                item.save()
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create_listing.html", {
                "form": form,
                "title_h2": "Create Listing",
                "title": "Create Listing",
                "watchlist_count": watchlist_count,
                "message": "Invalid form data.",
                "form": form
            })

    return render(request, "auctions/create_listing.html", {
                "form": form,
                "title_h2": "Create Listing",
                "title": "Create Listing",
                "watchlist_count": watchlist_count,
            })


def view_listing(request, pk):
    #if not request.user.is_authenticated:
    #    return HttpResponseRedirect(reverse("login"))
    listing = ItemAuction.objects.get(pk=pk)
    comments = Comment.objects.all().filter(item_auction=listing)
    form = FormBid()
    form_comment = FormComment()
    form.fields['amount'].widget.attrs = {'class':'bid-form-input', 'placeholder': '$0.00'}
    message = None
    btn_text = ""
    watchlist_count = None
    if request.user.is_authenticated:
        watchlist_count = Watchlist.objects.all().filter(user=request.user).count
        if Watchlist.objects.all().filter(user=request.user, item_auction=ItemAuction.objects.get(pk=pk)):    
            btn_text = "Remove to Watchlist"
        else:
            btn_text = "Add  to Watchlist"
    if request.method == "POST":
        form = FormBid(request.POST)
        form_comment = FormComment(request.POST)
        if form_comment.is_valid():
            comment = Comment.objects.create(item_auction=listing, user=request.user, content=form_comment.cleaned_data['content'])
            comment.save()
            return HttpResponseRedirect(reverse("view_listing", args=[pk]))
        form.fields['amount'].widget.attrs = {'class':'bid-form-input', 'placeholder': '$0.00'}
        if form.is_valid():
            if not listing.current_price:
                message = "The bid must be greater than or equal to the Initial Price and greater than the Current Price"
                if form.cleaned_data['amount'] >= listing.initial_price:
                    listing.current_price = form.cleaned_data['amount']
                    listing.buyer = request.user
                    bid = Bid.objects.create(item_auction=listing, user=request.user, amount=form.cleaned_data['amount'])
                    bid.save()
                    listing.save()
                    return HttpResponseRedirect(reverse("view_listing", args=(pk,)))
            elif form.cleaned_data['amount'] > listing.current_price:
                listing.current_price = form.cleaned_data['amount']
                bid = Bid.objects.create(item_auction=listing, user=request.user, amount=form.cleaned_data['amount'])
                listing.buyer = request.user
                bid.save()
                listing.save()
                return HttpResponseRedirect(reverse("view_listing", args=(pk,)))
            else:
                message = "The bid must be greater than or equal to the Initial Price and greater than the Current Price"
                return render(request, "auctions/view_listing.html", {
                    "listing": listing,
                    "title_h2": "View Listing",
                    "title": "View Listing",
                    "btn_text": btn_text,
                    "comments": comments,
                    "watchlist_count": watchlist_count,
                    "bid_btn_text": "Place Bid",
                    "form": form,
                    "form_comment": form_comment,
                    "message": message
                })    
        
    return render(request, "auctions/view_listing.html", {
                "listing": listing,
                "title_h2": "View Listing",
                "title": "View Listing",
                "btn_text": btn_text,
                "comments": comments,
                "watchlist_count": watchlist_count,
                "bid_btn_text": "Place Bid",
                "form": form,
                "form_comment": form_comment,
                "message": message,
            })


def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    watchlist = Watchlist.objects.all().filter(user=request.user)
    watchlist_count = watchlist.count()
    return render(request, "auctions/watchlist.html", {
                "watchlist": watchlist,
                "title_h2": "Watchlist",
                "title": "Watchlist",
                "watchlist_count": watchlist_count,
            })


def add_watchlist(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if Watchlist.objects.all().filter(user=request.user, item_auction=ItemAuction.objects.get(pk=pk)).count() == 0:
        listing = Watchlist.objects.create(user=request.user, item_auction=ItemAuction.objects.get(pk=pk))
        listing.save()
    else:
        listing = Watchlist.objects.all().filter(user=request.user, item_auction=ItemAuction.objects.get(pk=pk))
        listing.delete()
    return HttpResponseRedirect(reverse("view_listing", args=(pk,)))

# REMOVE LISTING FROM WATCHLIST IN WATCHLIST VIEW
def add_watchlist_watchlist(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if Watchlist.objects.all().filter(user=request.user, item_auction=ItemAuction.objects.get(pk=pk)).count() == 0:
        listing = Watchlist.objects.create(user=request.user, item_auction=ItemAuction.objects.get(pk=pk))
        listing.save()
    else:
        listing = Watchlist.objects.all().filter(user=request.user, item_auction=ItemAuction.objects.get(pk=pk))
        listing.delete()
    return HttpResponseRedirect(reverse("watchlist" ))


def close_auction(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    # COLOCAR UMA REGRA PARA NÃO ACESSAR ESSE VIEW SE O LISTING NÃO FOR DO USUÁRIO LOGADO
    # COLOCAR UMA REGRA PARA NÃO ACESSAR ESSE VIEW SE O LLISTING JÁ TIVER SIDO FINALIZADO
    listing = ItemAuction.objects.get(pk=pk)
    if not listing.active:
        return HttpResponseRedirect(reverse("index"))
    listing.active = 0
    listing.date_end = datetime.now() #"2023-01-01"
    listing.save()
    return HttpResponseRedirect(reverse("view_listing", args=(pk,)))


def comment_save(request, comment, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = ItemAuction.objects.get(pk=pk)
    comment = Comment.objects.create(item_auction=listing, user=request.user, content=comment)
    comment.save()
    return HttpResponseRedirect(reverse("view_listing", args=(pk,)))
