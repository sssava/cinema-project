from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from core.managers import ExtendedUserManager
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import make_aware


class User(AbstractUser):
    money = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_request = models.DateTimeField(auto_now_add=True)
    objects = ExtendedUserManager()

    def __str__(self):
        return f"{self.username}, {self.last_request}"

    def save(self, *args, **kwargs):
        if self.last_request.tzinfo is None:
            self.last_request = make_aware(self.last_request)
        self.last_request = timezone.localtime(self.last_request)

        if not self.pk:
            self.money = 200
        super().save(*args, **kwargs)

    def buy_ticket(self, price):
        self.money -= price
        self.save()

    def total_spent(self):
        return self.orders.aggregate(total_spent=Sum('purchase_price'))['total_spent'] or 0.00

    def update_last_request(self):
        self.last_request = datetime.now()
        self.save()
        return self.last_request
