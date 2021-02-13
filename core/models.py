from django.db import models
from django.contrib.auth.models import User

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    balance = models.FloatField(default=0)

    def __str__(self):
        return f'{self.user} - {self.balance}'


class SaleEntry(models.Model):
    date = models.DateField()
    ebay_price = models.FloatField()
    amazon_price = models.FloatField()
    ebay_tax = models.FloatField()
    paypal_tax = models.FloatField()
    tm_fee = models.FloatField(default=0.3)
    promoted = models.FloatField(default=0.0)
    profit = models.FloatField()
    discount = models.FloatField(default=0)
    country = models.CharField(max_length=100, default="-----")
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def save(self, *args, **kwargs):
        if not self.pk:  # object is being created, thus no primary key field yet
            change_balance = Balance.objects.get(user=self.user)
            change_balance.balance -= self.amazon_price - self.tm_fee + self.discount
            change_balance.save()
        
        super(SaleEntry, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        balance_obj = Balance.objects.get(user=self.user)
        balance_obj.balance += self.amazon_price + self.tm_fee - self.discount
        balance_obj.save()
        
        super(SaleEntry, self).delete(*args, **kwargs)
    
    def calc_profit(self):
        profit = self.ebay_price - self.amazon_price - self.ebay_tax - self.paypal_tax - self.tm_fee - self.promoted + self.discount
        if self.country == '-----':
            return profit
        else:
            hipshipper_obj = HipShipper.objects.get(sale_entry=self)
            return profit + hipshipper_obj.buyer_paid - hipshipper_obj.seller_paid
        

    def __str__(self):
        return f'{self.user} - {self.profit}'


class Gift(models.Model):
    date = models.DateField()
    gift_money = models.FloatField()
    gift_tax = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def save(self, *args, **kwargs):
        balance_obj = Balance.objects.get(user=self.user)
        balance_obj.balance += self.gift_money - self.gift_tax
        balance_obj.save()
        super(Gift, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} - {self.gift_money}'

class Cost(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return f'{user} - {name}'

class HipShipper(models.Model):
    buyer_paid = models.FloatField()
    seller_paid = models.FloatField()
    sale_entry = models.OneToOneField(SaleEntry, on_delete=models.CASCADE, default=0)

    def save(self, *args, **kwargs):
        self.sale_entry.profit += self.buyer_paid - self.seller_paid
        self.sale_entry.save()
        super(HipShipper, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.sale_entry.user}({self.sale_entry.country}) - {self.buyer_paid - self.seller_paid}'


