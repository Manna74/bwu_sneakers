from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('home/', views.home, name='home'),
    path('address/', views.address_page, name='address'),
    path('payment/', views.payment_page, name='payment'),
    path('success/', views.success_page, name='success'),
    path('logout/', views.logout_view, name='logout'),
    path('save-cart/', views.save_cart, name='save_cart'),
    path('save-address/', views.save_address, name='save_address'),
    path('save-payment/', views.save_payment, name='save_payment'),
    path('debug-session/', views.debug_session, name='debug_session'),
]