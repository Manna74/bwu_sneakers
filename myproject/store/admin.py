from django.contrib import admin
from .models import Product, OTP, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'brand', 'price', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user_email', 'total_amount', 'status', 'order_date', 'payment_method']
    list_filter = ['status', 'payment_method', 'order_date']
    search_fields = ['order_id', 'user_email', 'first_name', 'last_name']
    readonly_fields = ['order_id', 'order_date']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'order_date', 'status', 'total_amount')
        }),
        ('User Information', {
            'fields': ('user_email', 'user_phone')
        }),
        ('Delivery Address', {
            'fields': ('first_name', 'last_name', 'address', 'city', 'state', 'pincode', 'landmark')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_status', 'transaction_id')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'brand', 'price', 'quantity', 'order']
    list_filter = ['brand']
    search_fields = ['product_name', 'order__order_id']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'category', 'featured', 'trending']
    list_filter = ['brand', 'category', 'featured', 'trending']
    search_fields = ['name', 'brand']

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp_code', 'created_at', 'is_verified']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email']