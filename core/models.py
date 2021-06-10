from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class Balance(models.Model):
    """
    Every new user automatically gets a balance object right after signing up with the sign up form.
    The balance is the money the user has in the monitor app.

    #### Attributes
    `user : django.contrib.auth.models.User` The user this balance object is related to.

    `balance : float` The balance value for this particular user. default = 0.

    `paypal_balance : float`The paypal balance value for this particular user. default = 0.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    balance = models.FloatField(default=0)
    paypal_balance = models.FloatField(default=0)

    def __str__(self):
        '''
        #### Example
        user = Daniel,
        balance = 541.62,
        paypal_balance = 1852.67.

        #### Daniel - 541.62 - 1852.67
        '''
        return f'{self.user} - {self.balance} - {self.paypal_balance}'


class SaleEntry(models.Model):
    """
    Every sale the user registers is a SaleEnrty object.

    The purpose of this model is to organize every sale registered to the same format which is described above.

    #### Attributes
    `date : datetime.date` The date this product has been sold.

    `ebay_price : float` Product selling price on ebay.

    `amazon_price : float` Product buying price from amazon.

    `ebay_tax : float` Tax ($) eBay claimed for this sale.

    `paypal_tax : float` Tax ($) paypal claimed for this sale.

    `tm_fee : float` Trademark (TM) fee. optinal (default = 0.3).

    `promoted : float` If your sale is promoted, enter the promotion fee. optinal (default = 0).

    `profit : float` Total profit

    `discount : float` If you got a discount from the monitor, enter the discount amount. optinal (default = 0).

    `country : str` If you bought this product from foreign country, enter the country name. optinal (default = -----).

    `user : django.contrib.auth.models.User` The user this balance object is related to.
    """
    
    date = models.DateField()
    ebay_price = models.FloatField()
    amazon_price = models.FloatField()
    ebay_tax = models.FloatField()
    paypal_tax = models.FloatField()
    tm_fee = models.FloatField(default=0.3)
    promoted = models.FloatField(default=0)
    profit = models.FloatField()
    discount = models.FloatField(default=0)
    country = models.CharField(max_length=100, default="-"*5)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)


    def calc_profit(self):
        '''
        Calculates and returned the profit
        '''
        
        profit = self.ebay_price - self.amazon_price - self.ebay_tax - self.paypal_tax - self.tm_fee - self.promoted + self.discount

        if self.country == '-'*5: 
            # country is default - profit stays normal
            return profit
        else:
            # country is something else - consider the hipshipper prices
            try:
                hipshipper_obj = HipShipper.objects.get(sale_entry=self)
            except ObjectDoesNotExist:
                hipshipper_obj = HipShipper(sale_entry=self, buyer_paid=0, seller_paid=0)
                hipshipper_obj.save()

            return profit + hipshipper_obj.buyer_paid - hipshipper_obj.seller_paid

    def save(self, *args, **kwargs):
        '''
        Changing the balance for amazon_price, tm_fee and discount parameters on update and on creation.

        #### Keyword Arguments
        `update_type : str` What field has been updated

        `update_value_diff : float` The change in that value
        '''
        change_balance = Balance.objects.get(user=self.user)

        if not self.pk:  
            # object is being created, thus no primary key field yet
            change_balance.balance -= self.amazon_price + self.tm_fee - self.discount
            change_balance.paypal_balance = change_balance.paypal_balance + self.ebay_price - self.paypal_tax
            
        else:
            # there is a primary key already, so the object updated.
            self.profit = self.calc_profit()
            if kwargs.get('update_type'):
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
        '''
        When a sale is deleted, I need to revert the changes to balance I did in the save() method.
        '''
        balance_obj = Balance.objects.get(user=self.user)

        if ReturnedSale.objects.filter(sale=self).count() > 0:
            # revert changes of returned sale save
            balance_obj.balance += self.tm_fee + self.discount
            balance_obj.paypal_balance += self.paypal_tax

        else:
            balance_obj.balance += self.amazon_price + self.tm_fee - self.discount
            balance_obj.paypal_balance = balance_obj.paypal_balance - self.ebay_price + self.paypal_tax

        balance_obj.save()
        
        super(SaleEntry, self).delete(*args, **kwargs)


    def __str__(self):
        '''
        #### Example
        user = Daniel,
        profit = 17.41

        #### Daniel - 17.41
        '''
        return f'{self.user} - {self.profit}'


class Gift(models.Model):
    """
    Gifts can be bought to add money to the user's monitor balance.

    This model is used to keep track of these gifts and organize them together.

    #### Attributes
    `is_gift : bool` Is this a gift or a manual change?

    `date : datetime.date` The date this gift was added.

    `gift_money : float` Gift worth ($) with taxes.

    `gift_tax : float` Gift Tax ($).

    `user : django.contrib.auth.models.User` The user this balance object is related to.
    """
    is_gift = models.BooleanField(default=True)
    date = models.DateField()
    gift_money = models.FloatField()
    gift_tax = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def calc_gift_value(self):
        '''Calculate the gift real value after taxes'''
        return self.gift_money - self.gift_tax


    def save(self, *args, **kwargs):
        '''
        Add the gift value to the balance.
        '''
        balance_obj = Balance.objects.get(user=self.user)
        balance_obj.balance += self.calc_gift_value()

        if self.is_gift:
            balance_obj.paypal_balance -= self.gift_money

        balance_obj.save()

        super(Gift, self).save(*args, **kwargs)
    

    def delete(self, *args, **kwargs):
        '''
        Subtract the gift value from the balance
        '''
        balance_obj = Balance.objects.get(user=self.user)
        balance_obj.balance -= self.calc_gift_value()
        if self.is_gift:
            balance_obj.paypal_balance += self.gift_money
        balance_obj.save()

        super(Gift, self).delete(*args, **kwargs)


    def __str__(self):
        '''
        #### Example
        date = 25/02/2021,
        gift_money = 103.0,
        gift_tax = 3.0,
        user = Daniel

        #### Daniel - 100.0
        '''
        return f'{self.user} - {self.calc_gift_value()}'

class Cost(models.Model):
    """
    Managing an eBay store has it's costs. it can be monitors, programs that are used to help manage the store, eBay store price, etc...

    We can help the users consider this costs in the total profit calculation.

    #### Attributes
    `name :str` Cost name.

    `value : float` Cost value (per month).

    `is_constant : float` Is the cost is a constant one or temporary?

    `exp_date : date` If the cost is constant then it has an expire date

    `user : django.contrib.auth.models.User` The user this balance object is related to.
    """
    name = models.CharField(max_length=100)
    value = models.FloatField()
    is_constant = models.BooleanField(default=False)
    exp_date = models.DateField(blank=True)
    start_date = models.DateField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=0)

    def __str__(self):
        '''
        ####Example
        name = Monitor,
        value = 400.0,
        user = Daniel

        #### Daniel: Monitor $400
        --------------------
        '''
        return f'{self.user}: {self.name} ${self.value}'

class HipShipper(models.Model):
    """
    When a product is being shipped from another country, it has a special cost.

    This model organizes all the times the user has paid for shipping and recalculating the profit.

    #### Attributes
    `buyer_paid : float` How much did the buyer paid for shipping.

    `seller_paid : float` How much did the seller (the user) paid for shipping.

    `sale_entry : models.SaleEntry` The sale related to this shipment.
    """
    buyer_paid = models.FloatField()
    seller_paid = models.FloatField()
    sale_entry = models.OneToOneField(SaleEntry, on_delete=models.CASCADE, default=0)

    def save(self, *args, **kwargs):
        '''Changing the paypal balance on save.
        '''
        change_balance = Balance.objects.get(user=self.sale_entry.user)

        if not self.pk:  
            # object is being created, thus no primary key field yet
            change_balance.paypal_balance = float(change_balance.paypal_balance) + float(self.buyer_paid) - float(self.seller_paid)
        else:
            old_buyer_paid = kwargs.pop("old_buyer_paid") # What was updated?
            old_seller_paid = kwargs.pop("old_seller_paid") # How did the value change?
            old_diff = old_buyer_paid - old_seller_paid
            change_balance.paypal_balance = float(change_balance.paypal_balance) + float(self.buyer_paid) - float(self.seller_paid) - old_diff
        
        change_balance.save()
            
        super(HipShipper, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        '''Change balance and paypal balance on delete
        '''
        change_balance = Balance.objects.get(user=self.sale_entry.user)
        change_balance.paypal_balance = float(change_balance.paypal_balance) - float(self.buyer_paid) + float(self.seller_paid)

    def __str__(self):
        '''
        #### Example
        buyer_paid = 15.0,
        seller_paid = 5.0,
        sale_entry = 171

        #### 171(Israel) - 10.0
        '''
        return f'{self.sale_entry.id}({self.sale_entry.country}) - {self.buyer_paid - self.seller_paid}'


class ReturnedSale(models.Model):
    """
    When a user returnes a sale, it is saved in this table for the report

    #### Attributes
    `sale : SaleEntry` The sale that was returned

    `is_pending : bool` Is the sale pending?

    `date_of_return : datetime.date` The date of return
    """
    sale = models.OneToOneField(SaleEntry, on_delete=models.CASCADE, default=0)
    is_pending = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        """Change the balance according to the pending status
        """
        balance_obj = Balance.objects.get(user=self.sale.user)
        if not self.pk: 
            # new object
            # sale is pending to be returned - substract ebay price from paypal balance
            balance_obj.paypal_balance -= self.sale.ebay_price
        else:
            # updated is_pending
            if not self.is_pending:
                # sale has returned - add amazon price to balance
                balance_obj.balance += self.sale.amazon_price - self.sale.tm_fee

        balance_obj.save()

        super(ReturnedSale, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs): 
        """Change the balance and paypal balance back to before the sale
        """
        balance_obj = Balance.objects.get(user=self.sale.user)

        # sale return was canceled - substract amazon price from balance
        balance_obj.balance -= self.sale.amazon_price

        # add ebay price to paypal balance
        balance_obj.paypal_balance += self.sale.ebay_price

        balance_obj.save()

        super(ReturnedSale, self).delete(*args, **kwargs)

    def __str__(self):
        return f'[returned] {self.sale}'


class Preferences(models.Model):
    """The preferences of the user

    #### Attributes
    `user : django.contrib.auth.User` The user

    `default_month : bool` True for selecting sales from last month else select all sales

    `start_month_day : int` Month will end in this day minus 1

    `sort_by_date : bool` True for sort by date, else don't sort
    """
    user = models.OneToOneField(User, models.CASCADE, default=0)
    default_month = models.BooleanField(default=True)
    start_month_day = models.IntegerField(default=16)
    sort_by_date = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            new_start_month_day = self.start_month_day

            # change temp costs dates' start day
            temp_costs = Cost.objects.filter(user=self.user, is_constant=False)
            for t in temp_costs:
                old_start_date = t.start_date
                old_exp_date = t.exp_date

                months_diff = old_exp_date.month - old_start_date.month
                if months_diff == 0:
                    months_diff = 1
                    
                t.start_date = datetime.date(old_start_date.year, old_start_date.month, new_start_month_day)
                t.exp_date = t.start_date + relativedelta(months=+months_diff, days=-1)

                t.save()
                    
        super(Preferences, self).save(*args, **kwargs)

    def __str__(self):
        """
        #### Example
        user = Daniel,
        default_month = True,
        start_month_day = 16,
        sort_by_date = True  

        #### Daniel | default_month = True | start_month_day = 16 | sort_by_date = True
        """
        s = "user = " + str(self.user) + " | "
        s += "default_month = " + str(self.default_month) + " | "
        s += "start_month_day = " + str(self.start_month_day) + " | "
        s += "sort_by_date = " + str(self.sort_by_date)
        
        return s
