from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal



class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Auction(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))])
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('1.00'))])
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_auctions')
    image = models.ImageField(upload_to='auction_images/', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='auctions', null=True, blank=True)


    def __str__(self):
        return self.title
    def get_current_price(self):
        return self.current_price if self.current_price > 0 else self.starting_price

    def get_minimum_bid(self):
        current = self.get_current_price()
        return current + Decimal('0.01')

    def get_bid_count(self):
        return self.bids.count()

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('1.00'))])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Bid by {self.user.username} on {self.auction.title} for {self.amount}'
    
    def save(self, *args, **kwargs):
        current_price = self.auction.current_price if self.auction.current_price > 0 else self.auction.starting_price
        if self.amount <= current_price:
            raise ValueError("Bid amount must be greater than the current price.")
        super().save(*args, **kwargs)
        self.auction.current_price = self.amount
        self.auction.save()


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.auction.title}'

    
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='watchlist_items')

    class Meta:
        unique_together = ('user', 'auction')

    def __str__(self):
        return f'{self.user.username} watching {self.auction.title}'

class Listing(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings', null=True, blank=True)