from django.db import models
from django.contrib.auth.models import User

class SaleEntry(models.Model):
    date = models.DateField()
    ebay_price = models.FloatField()
    amazon_price = models.FloatField()
    ebay_tax = models.FloatField()
    paypal_tax = models.FloatField()
    tm_fee = models.FloatField(default=0.3)
    promoted = models.FloatField(default=0.0)
    profit = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return f'{self.user} - {self.profit}'
