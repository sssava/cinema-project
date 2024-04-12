from django.db import models
from django.contrib.auth.models import AbstractUser
from core.managers import ExtendedUserManager
from django.db.models import Sum


class User(AbstractUser):
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    objects = ExtendedUserManager()

    def __str__(self):
        return f"{self.username}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.money = 200
        super().save(*args, **kwargs)

    def buy_ticket(self, price):
        self.money -= price
        self.save()

    def total_spent(self):
        return self.orders.aggregate(total_spent=Sum('purchase_price'))['total_spent'] or 0.00
