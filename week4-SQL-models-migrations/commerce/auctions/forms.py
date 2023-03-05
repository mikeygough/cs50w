from django import forms
from .models import Listing, Bid, Comment

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'category']


class CreateBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['title', 'body']