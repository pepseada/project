from django.urls import path
from .views import create_payment, payment_success, payment_cancel, home
from .views import validate_ticket, check_ticket, use_ticket
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(home), name='home'),  # يتطلب تسجيل الدخول
    path('paypal-payment/', create_payment, name='create-payment'),
    path('payment-success/', payment_success, name='payment-success'),
    path('payment-cancel/', payment_cancel, name='payment-cancel'),
    path('validate-ticket/', validate_ticket, name='validate-ticket'),
    path('check-ticket/', check_ticket, name='check-ticket'),
    path('use-ticket/<str:ticket_code>/', use_ticket, name='use-ticket'),
]
