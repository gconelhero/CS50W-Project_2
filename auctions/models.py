from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib import admin

from djmoney.models.fields import MoneyField


class User(AbstractUser):
    pass

admin.site.register(User)


class ItemAuction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=64)
    category = models.CharField(max_length=64, choices=[('Electronics', 'Electronics'),('Collectibles', 'Collectibles'),('Others', 'Others')], blank=False, null=False)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    date_end = models.DateTimeField()
    image_url = models.CharField(max_length=200, blank=True, null=True)
    initial_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    current_price = MoneyField(max_digits=10,decimal_places=2, blank=True, null=True, default_currency='USD')
    active = models.BooleanField(default=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='winner', blank=True)

    def __str__(self):
        return f"{self.item_name} - {self.initial_price} - {self.current_price} - {self.user}"

admin.site.register(ItemAuction)


class Bid(models.Model):
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_auction = models.ForeignKey(ItemAuction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} - {self.user}"

admin.site.register(Bid)


class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_auction = models.ForeignKey(ItemAuction, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.content} - {self.user}"

admin.site.register(Comment)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_auction = models.ForeignKey(ItemAuction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item_auction} - {self.user}"