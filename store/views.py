from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Product, OTP, Order, OrderItem
import json

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            # Generate OTP
            otp_code = OTP.generate_otp()
            
            # Delete old OTPs for this email
            OTP.objects.filter(email=email).delete()
            
            # Create new OTP
            otp = OTP.objects.create(email=email, otp_code=otp_code)
            
            # Send OTP email
            try:
                send_mail(
                    'Your Sneaker Store OTP',
                    f'Your OTP for Sneaker Store login is: {otp_code}\nThis OTP will expire in 10 minutes.',
                    'sagarmanna1980@gmail.com',
                    [email],
                    fail_silently=False,
                )
                request.session['login_email'] = email
                messages.success(request, 'OTP sent to your email!')
                return redirect('verify_otp')
            except Exception as e:
                messages.error(request, 'Failed to send OTP. Please try again.')
        
    return render(request, 'login.html')

def verify_otp(request):
    email = request.session.get('login_email')
    
    if not email:
        return redirect('login')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        try:
            otp_obj = OTP.objects.get(email=email, otp_code=entered_otp, is_verified=False)
            
            # Check if OTP is expired (10 minutes)
            if timezone.now() - otp_obj.created_at > timedelta(minutes=10):
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('login')
            
            # Mark OTP as verified
            otp_obj.is_verified = True
            otp_obj.save()
            
            # Set session for logged in user
            request.session['user_email'] = email
            request.session['is_authenticated'] = True
            
            messages.success(request, 'Login successful!')
            return redirect('home')
            
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'verify_otp.html', {'email': email})

def home(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    
    if Product.objects.count() == 0:
        create_sample_products()
    
    featured_products = Product.objects.filter(featured=True)
    trending_products = Product.objects.filter(trending=True)
    all_products = Product.objects.all()
    
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'all_products': all_products,
        'user_email': request.session.get('user_email')
    })

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

def address_page(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    return render(request, 'address.html')

def payment_page(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        request.session['payment_method'] = payment_method
        return redirect('success')
    
    return render(request, 'payment.html')

def success_page(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    
    # Get data from session
    cart_json = request.session.get('cart', '[]')
    address_json = request.session.get('delivery_address', '{}')
    payment_method = request.session.get('payment_method', 'upi')
    user_email = request.session.get('user_email', '')
    
    try:
        cart = json.loads(cart_json)
        address = json.loads(address_json)
    except:
        cart = []
        address = {}
    
    order_id = None
    
    # Create order only if we have all required data
    if cart and address and user_email:
        try:
            # Calculate total amount
            total_amount = sum(float(item['price']) for item in cart)
            
            # Create Order in database
            order = Order.objects.create(
                user_email=user_email,
                user_phone=address.get('phone', ''),
                first_name=address.get('firstName', ''),
                last_name=address.get('lastName', ''),
                address=address.get('address', ''),
                city=address.get('city', ''),
                state=address.get('state', ''),
                pincode=address.get('pincode', ''),
                landmark=address.get('landmark', ''),
                payment_method=payment_method,
                payment_status=True,
                total_amount=total_amount
            )
            
            # Create Order Items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    brand=item.get('brand', 'Unknown'),
                    price=item['price'],
                    quantity=1
                )
            
            order_id = order.order_id
            
            # Clear session data after successful order creation
            request.session.pop('cart', None)
            request.session.pop('delivery_address', None)
            request.session.pop('payment_method', None)
            
        except Exception as e:
            print(f"Error creating order: {e}")
            messages.error(request, 'Error creating order. Please contact support.')
    
    return render(request, 'success.html', {
        'order_id': order_id
    })

def save_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['cart'] = json.dumps(data['cart'])
            request.session['cart_total'] = data['total']
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'})

def save_address(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['delivery_address'] = json.dumps(data)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'})

def save_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['payment_method'] = data['payment_method']
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error'})

def debug_session(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    
    session_data = {
        'cart': request.session.get('cart', 'Not found'),
        'delivery_address': request.session.get('delivery_address', 'Not found'),
        'payment_method': request.session.get('payment_method', 'Not found'),
        'user_email': request.session.get('user_email', 'Not found'),
    }
    
    return JsonResponse(session_data)

def create_sample_products():
    if Product.objects.exists():
        return
    
    products_data = [
        {'name': 'Nike Air Jordan 1 Chicago', 'price': 45999, 'category': 'Limited Edition', 'brand': 'Nike', 'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500', 'featured': True, 'size_range': '6-12', 'trending': True, 'limited_edition': True},
        {'name': 'Adidas Yeezy Boost 350 V2', 'price': 29999, 'category': 'Limited Edition', 'brand': 'Adidas', 'image_url': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500', 'featured': True, 'size_range': '7-13', 'trending': True, 'limited_edition': True},
        {'name': 'Nike Air Force 1 White', 'price': 8999, 'category': 'Casual', 'brand': 'Nike', 'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500', 'featured': False, 'size_range': '6-12', 'trending': True, 'limited_edition': False},
        {'name': 'Adidas Ultraboost 21', 'price': 17999, 'category': 'Running', 'brand': 'Adidas', 'image_url': 'https://images.unsplash.com/photo-1549289524-06cf8837ace5?w=500', 'featured': True, 'size_range': '7-13', 'trending': False, 'limited_edition': False},
        {'name': 'Puma RS-X Toys', 'price': 12999, 'category': 'Casual', 'brand': 'Puma', 'image_url': 'https://images.unsplash.com/photo-1604671368394-97cbc3f2ec0f?w=500', 'featured': False, 'size_range': '6-12', 'trending': True, 'limited_edition': True},
        {'name': 'New Balance 550 White', 'price': 14999, 'category': 'Luxury', 'brand': 'New Balance', 'image_url': 'https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=500', 'featured': True, 'size_range': '7-13', 'trending': False, 'limited_edition': False},
    ]
    
    for data in products_data:
        Product.objects.create(
            name=data['name'],
            description=f"Premium {data['name']}. Authentic {data['brand']} product with premium materials and exclusive design.",
            price=data['price'],
            category=data['category'],
            brand=data['brand'],
            image_url=data['image_url'],
            featured=data['featured'],
            size_range=data['size_range'],
            trending=data['trending'],
            limited_edition=data['limited_edition']
        )