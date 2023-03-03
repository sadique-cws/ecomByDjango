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
    
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product,on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)

    def __str__(self):
        return self.item.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # address, coupon, payments details add further

    def __str__(self):
        return self.user.username
    
    