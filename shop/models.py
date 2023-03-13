from django.db import models
from django.conf import settings

class Category(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    slug = models.SlugField()

    def __str__(self):
        return self.title

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    brand = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    def getSavingPercent(self):
        result = ((self.price - self.discount_price) / self.price) * 100
        return round(result)
    
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product,on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)

    def __str__(self):
        return self.item.name

    def get_discount_price(self):
        return self.item.discount_price * self.qty 

    def get_price(self):
        return self.item.price * self.qty
    
    def get_final_amount(self):
        if self.item.discount_price:
            return self.get_discount_price()
        else:
            return self.get_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey('Coupon',on_delete=models.CASCADE,null=True, blank=True)
    address = models.ForeignKey("Address",on_delete=models.CASCADE, null=True, blank=True)
    # address, payments details add further

    def __str__(self):
        return self.user.username
    
    def get_total_amount(self):
        total = 0
        for oi in self.items.all():
            total += oi.get_final_amount()
        
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_price_amount(self):
        total = 0
        for oi in self.items.all():
            total += oi.get_price()
        return total

    def get_tax_amount(self):
        return int(self.get_total_amount() * 0.18)
    
    def get_payable_amount(self):
        return self.get_total_amount() + self.get_tax_amount()
    
    def get_discount_amount(self):
        return self.get_price_amount() - self.get_total_amount()

    
class Coupon(models.Model):
    code = models.CharField(max_length=20)
    amount = models.FloatField()

    def __str__(self):
        return self.code
    

class Address(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    alt_contact = models.CharField(max_length=200, null=True, blank=True)
    street = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    pincode = models.IntegerField()
    type = models.CharField(max_length=20,choices=(("Home","Home"),("Office","Office")))
    isDefault = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.user.username