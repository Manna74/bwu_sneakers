from django.db import models
import random
import string
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, default='Nike')
    featured = models.BooleanField(default=False)
    size_range = models.CharField(max_length=50, default='6-12')
    trending = models.BooleanField(default=False)
    limited_edition = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.email} - {self.otp_code}"
    
    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    # Order Information
    order_id = models.CharField(max_length=20, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # User Information
    user_email = models.EmailField()
    user_phone = models.CharField(max_length=15)
    
    # Address Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=200, blank=True)
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.user_email}"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_order_id(cls):
        return 'SNK' + ''.join(random.choices(string.digits, k=7))

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.product_name} - Order {self.order.order_id}"
    
    def get_total_price(self):
        return self.price * self.quantity