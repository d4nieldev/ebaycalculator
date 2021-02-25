from django.db import models
from django.contrib.auth.models import User


class Balance(models.Model):
    """Balance Class

    This class has only one 2 parameters:
    user (type - django.contrib.auth.models.User): The user this balance object is related to.
    balance (type - int): The balance value for this particular user. default = 0.

    Purpose:
    Every new user automatically gets a balance object right after signing up with the sign up form.
    The balance is the money the user has in the monitor app.

    Balance Calculation:
    ask dad.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    balance = models.FloatField(default=0)

    def __str__(self):
        '''Example:

        user = Daniel
        balance = 541.62

        Daniel - 541.62
        '''
        return f'{self.user} - {self.balance}'


class SaleEntry(models.Model):
    """SaleEntry Class

    This class has 11 parameters:
    date (type - datetime.date): The date this product has been sold.
    ebay_price (type - float): Product selling price on ebay.
    amazon_price (type - float): Product buying price from amazon.
    ebay_tax (type - float): Tax ($) eBay claimed for this sale.
    paypal_tax (type - float): Tax ($) paypal claimed for this sale.
    tm_fee (type - float): Trademark (TM) fee. default = 0.3. 
    promoted (type - float): If your sale is promoted, enter the promotion fee. default = 0. (not promoted)
    profit (type - float): Total profit
    discount (type - float): If you got a discount from the monitor, enter the discount amount. default = 0. (no discount)
    country (type - str): If you bought this product from foreign country, enter the country name. default = ----- (USA or some default country).
    user (type - django.contrib.auth.models.User): The user this balance object is related to.

    Purpose:
    Every sale the user registers is a SaleEnrty object.
    The purpose of this model is to organize every sale registered to the same format which is described above.
    """
    
    date = models.DateField()
    ebay_price = models.FloatField()
    amazon_price = models.FloatField()
    ebay_tax = models.FloatField()
    paypal_tax = models.FloatField()
    tm_fee = models.FloatField(default=0.3)
    promoted = models.FloatField(default=0.0)
    profit = models.FloatField()
    discount = models.FloatField(default=0)
    country = models.CharField(max_length=100, default="-"*5)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)


    def calc_profit(self):
        '''This method is used for calculating the profit from the other parameters given to the equation'''
        
        profit = self.ebay_price - self.amazon_price - self.ebay_tax - self.paypal_tax - self.tm_fee - self.promoted + self.discount

        if self.country == '-'*5: 
            # country is default - profit stays normal
            return profit
        else:
            # country is something else - consider the hipshipper prices
            hipshipper_obj = HipShipper.objects.get(sale_entry=self)
            return profit + hipshipper_obj.buyer_paid - hipshipper_obj.seller_paid


    def save(self, *args, **kwargs):
        '''When the object is being created or updated, this method is executing
        
        My modifications:
        Changing the balance for amazon_price, tm_fee and discount parameters on update and on creation.
        '''
        change_balance = Balance.objects.get(user=self.user)

        if not self.pk:  
            # object is being created, thus no primary key field yet
            change_balance.balance -= self.amazon_price - self.tm_fee + self.discount
            
        else:
            # there is a primary key already, so the object updated.
            if kwargs["update_type"]:
                type = kwargs.pop("update_type") # What was updated?
                value = kwargs.pop("update_value_diff") # How did the value change?

                matter_types = ['amazon_price', 'tm_fee', 'discount']

                if type in matter_types:
                    if type == 'discount':
                        change_balance.balance += float(value)
                    else:
                        change_balance.balance -= float(value)

        change_balance.save() 
        
        super(SaleEntry, self).save(*args, **kwargs)
    

    def delete(self, *args, **kwargs):
        '''When the object is being deleted, this method is called
        
        My modifications:
        When a sale is deleted, I need to revert the changes to balance I did in the save() method.
        '''
        balance_obj = Balance.objects.get(user=self.user)
        balance_obj.balance += self.amazon_price + self.tm_fee - self.discount
        balance_obj.save()
        
        super(SaleEntry, self).delete(*args, **kwargs)


    def __str__(self):
        '''Example:

        user = Daniel
        profit = 17.41

        Daniel - 17.41
        '''
        return f'{self.user} - {self.profit}'


class Gift(models.Model):
    """Gift Clasas

    This class has 4 parameters:
    date (type - datetime.date): The date this gift was added.
    gift_money (type - float): Gift worth ($) with taxes.
    gift_tax (type - float): Gift Tax ($).
    user (type - django.contrib.auth.models.User): The user this balance object is related to.

    Purpose:
    Gifts can be bought to add money to your monitor balance.
    This model is used to keep track of these gifts and organize them together.
    """
    date = models.DateField()
    gift_money = models.FloatField()
    gift_tax = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)


    def calc_gift_value(self):
        '''Calculate the gift real value (after taxes)'''
        return self.gift_money - self.gift_tax


    def save(self, *args, **kwargs):
        '''When the object is being created or updated, this method is executing

        My modifications:
        Add the gift value to the balance.
        '''
        balance_obj = Balance.objects.get(user=self.user)
        balance_obj.balance += self.calc_gift_value()
        balance_obj.save()

        super(Gift, self).save(*args, **kwargs)

    def __str__(self):
        '''Example:

        date = 25/02/2021
        gift_money = 103.0
        gift_tax = 3.0
        user = Daniel

        Daniel - 100.0
        '''
        return f'{self.user} - {self.calc_gift_value()}'

class Cost(models.Model):
    """Cost Class

    This class has 3 parameters:
    name (type - str): Cost name.
    value (type - float): Cost value (per month).
    user (type - django.contrib.auth.models.User): The user this balance object is related to.

    Purpose:
    Managing an eBay store has it's costs, it can be monitors, programs that are used to help manage the store, eBay store price, etc...
    We can help the users consider this costs in the total profit calculation.
    """
    name = models.CharField(max_length=100)
    value = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        '''Example:

        name = Monitor
        value = 400.0
        user = Daniel

        Daniel: Monitor $400
        '''
        return f'{self.user}: {self.name} ${self.value}'

class HipShipper(models.Model):
    """HipShipper Class

    This class has 3 parameters:
    buyer_paid (type - float): How much did the buyer paid for shipping.
    seller_paid (type - float): How much did the seller (the user) paid for shipping.
    sale_entry (type - .models.SaleEntry): The sale related to this shipment.

    Purpose:
    When a product is being shipped from another country, it has a special cost.
    This model organizes all the times the user has paid for shipping and recalculating the profit.
    """
    buyer_paid = models.FloatField()
    seller_paid = models.FloatField()
    sale_entry = models.OneToOneField(SaleEntry, on_delete=models.CASCADE, default=0)

    def save(self, *args, **kwargs):
        '''Adding the profit from shipping to total profit'''
        self.sale_entry.profit += self.buyer_paid - self.seller_paid
        self.sale_entry.save()

        super(HipShipper, self).save(*args, **kwargs)

    def __str__(self):
        '''Example: 

        buyer_paid = 15.0
        seller_paid = 5.0
        user = Daniel

        Daniel(Israel) - 10.0
        '''
        return f'{self.sale_entry.user}({self.sale_entry.country}) - {self.buyer_paid - self.seller_paid}'


