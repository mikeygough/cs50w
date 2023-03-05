from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Max

# make a custom primary key by setting primary_key=True for the fields
# many-to-one relationships are defined with models.ForeignKey

class User(AbstractUser):
    pass


class Listing(models.Model):
    FASHION = 'FA'
    TOYS = 'TO'
    ELECTRONICS = 'EL'
    HOME = 'HO'
    LISTING_CATEGORIES = [
        (FASHION, 'Fashion'),
        (TOYS, 'Toys'),
        (ELECTRONICS, 'Electronics'),
        (HOME, 'Home'),
    ]

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=280)
    starting_bid = models.FloatField()
    image = models.URLField(blank=True)
    category = models.CharField(max_length=2, blank=True,
                                choices=LISTING_CATEGORIES)

    created_at = models.DateTimeField(auto_now_add=True)
    auction_open = models.BooleanField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='winner')

    def highest_bid(self):
        return Bid.objects.filter(listing=self).aggregate(Max('bid'))['bid__max']

    def __str__(self):
        return f"{self.title}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing}"


class Bid(models.Model):
    bid = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing}: {self.bid}"


class Comment(models.Model):
    title = models.CharField(max_length=64)
    body = models.CharField(max_length=280)
    # provide related_name
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"