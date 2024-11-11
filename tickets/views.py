import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import Ticket
import random
import string
from django.core.mail import send_mail
from .forms import TicketCheckForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required

# configure PayPal SDK
# paypalrestsdk.configure({
#     "mode": "sandbox", 
#     "client_id": "YOUR_CLIENT_ID",
#     "client_secret": "YOUR_CLIENT_SECRET"
# })
@login_required
def home(request):
    """عرض الصفحة الرئيسية لشراء التذاكر."""
    if request.method == 'POST':
        return redirect('create-payment')  # تحويل إلى صفحة الدفع عند الضغط على زر الشراء
    return render(request, 'home.html')

def generate_ticket_code():
    """توليد رمز عشوائي للتذكرة والتأكد من أنه فريد."""
    while True:
        ticket_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Ticket.objects.filter(ticket_code=ticket_code).exists():
            return ticket_code

def create_payment(request):
    """إنشاء عملية دفع جديدة وإرسال رمز التذكرة عبر البريد الإلكتروني."""
    user_email = "test@example.com"  # بريد إلكتروني تجريبي
    ticket_code = generate_ticket_code()
    ticket = Ticket.objects.create(user_email=user_email, ticket_code=ticket_code)

    send_mail(
        'Your Ticket Code',
        f'Your ticket code is: {ticket.ticket_code}',
        'm.seada2002@gmail.com',  # استبدلها ببريدك الإلكتروني الحقيقي
        [user_email],
        fail_silently=False,
    )

    remaining_attempts = ticket.usage_limit - ticket.usage_count
    return render(request, 'ticket_valid.html', {'ticket': ticket, 'allowed_attempts': ticket.usage_limit, 'remaining_attempts': remaining_attempts})

def payment_success(request):
    """معالجة نجاح الدفع وإرسال رمز التذكرة عبر البريد الإلكتروني."""
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        user_email = payment.payer.payer_info.email
        ticket_code = generate_ticket_code()
        ticket = Ticket.objects.create(user_email=user_email, ticket_code=ticket_code)

        send_mail(
            'Your Ticket Code',
            f'Your ticket code is: {ticket.ticket_code}',
            'm.seada2002@gmail.com',  # استبدلها ببريدك الإلكتروني الحقيقي
            [user_email],
            fail_silently=False,
        )

        remaining_attempts = ticket.usage_limit - ticket.usage_count
        return render(request, 'ticket_valid.html', {'ticket': ticket, 'allowed_attempts': ticket.usage_limit, 'remaining_attempts': remaining_attempts})
    else:
        print(payment.error)
        return render(request, 'error.html', {'error': payment.error})

@csrf_exempt
def validate_ticket(request):
    """التحقق من صلاحية التذكرة من خلال API."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_code = data.get('ticket_code')

            ticket = Ticket.objects.get(ticket_code=ticket_code, status='unused')
            if ticket.usage_count < ticket.usage_limit:
                ticket.use_ticket()  # استخدم التذكرة

                return JsonResponse({
                    'valid': True,
                    'message': 'التذكرة صالحة!',
                    'ticket_code': ticket.ticket_code,
                    'remaining_attempts': ticket.usage_limit - ticket.usage_count,
                    'allowed_attempts': ticket.usage_limit
                })
            else:
                return JsonResponse({'valid': False, 'message': 'تم استهلاك جميع المحاولات.'})
        except Ticket.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'تذكرة غير صالحة أو مستخدمة من قبل.'})
    return JsonResponse({'valid': False, 'message': 'طريقة غير صحيحة.'})

def payment_cancel(request):
    """عرض صفحة إلغاء الدفع."""
    return render(request, 'cancel.html')

def check_ticket(request):
    """التحقق من حالة التذكرة بناءً على الكود المدخل."""
    if request.method == 'POST':
        form = TicketCheckForm(request.POST)
        if form.is_valid():
            ticket_code = form.cleaned_data['ticket_code']
            try:
                ticket = Ticket.objects.get(ticket_code=ticket_code)
                if ticket.status == 'unused' and ticket.usage_count < ticket.usage_limit:
                    remaining_attempts = ticket.usage_limit - ticket.usage_count
                    return render(request, 'ticket_valid.html', {
                        'ticket': ticket,
                        'allowed_attempts': ticket.usage_limit,
                        'remaining_attempts': remaining_attempts
                    })
                else:
                    return render(request, 'ticket_invalid.html', {'ticket_code': ticket_code})
            except Ticket.DoesNotExist:
                return render(request, 'ticket_invalid.html', {'ticket_code': ticket_code})
    else:
        form = TicketCheckForm()

    return render(request, 'check_ticket.html', {'form': form})

def use_ticket(request, ticket_code):
    """استخدام التذكرة بناءً على الكود المدخل."""
    ticket = get_object_or_404(Ticket, ticket_code=ticket_code)

    # محاولة استخدام التذكرة
    if ticket.use_ticket():
        remaining_attempts = ticket.usage_limit - ticket.usage_count
        return render(request, 'ticket_used.html', {
            'ticket_code': ticket.ticket_code,
            'allowed_attempts': ticket.usage_limit,
            'remaining_attempts': remaining_attempts
        })
    else:
        # إذا تم استنفاد المحاولات، عرض رسالة مناسبة
        return render(request, 'ticket_invalid.html', {
            'ticket_code': ticket.ticket_code,
            'error': 'تم استهلاك جميع المحاولات المتاحة.'
        })
    
# <h2>التحقق من التذكرة</h2>
# <form id="ticket-form">
#     <label for="ticket_code">ادخل كود التذكرة:</label>
#     <input type="text" id="ticket_code" name="ticket_code" required>
#     <button type="submit">تحقق</button>
# </form>
# <div id="message"></div>

# <script>
#     document.getElementById("ticket-form").addEventListener("submit", function(event) {
#         event.preventDefault();

#         const ticketCode = document.getElementById("ticket_code").value;
#         const apiUrl = "http://127.0.0.1:8000/home/paypal-payment/";

#         fetch(apiUrl, {
#             method: "POST",
#             headers: {
#                 "Content-Type": "application/json"
#             },
#             body: JSON.stringify({ ticket_code: ticketCode })
#         })
#         .then(response => response.json())
#         .then(data => {
#             const messageDiv = document.getElementById("message");
#             if (data.valid) {
#                 messageDiv.innerHTML = "<p>التذكرة صالحة!</p>";
#                 window.location.href = "https://tamreh.com/success/";  // هنا رابط صفحة النجاح
#             } else {
#                 messageDiv.innerHTML = "<p>كود التذكرة غير صحيح أو انتهت صلاحيته.</p>";
#             }
#         })
#         .catch(error => {
#             const messageDiv = document.getElementById("message");
#             messageDiv.innerHTML = "<p>حدث خطأ أثناء التحقق من التذكرة. يرجى المحاولة لاحقاً.</p>";
#             console.error("Error:", error);  // طباعة الخطأ في وحدة التحكم للمساعدة في التشخيص
#         });
#     });
# </script>

