from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    ticket_code = models.CharField(max_length=10, unique=True)
    user_email = models.EmailField()
    status = models.CharField(max_length=10, choices=[('unused', 'Unused'), ('used', 'Used')], default='unused')
    purchase_date = models.DateTimeField(default=timezone.now)
    usage_limit = models.PositiveIntegerField(default=1)
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.ticket_code

    def use_ticket(self):
        """تستخدم التذكرة وتزيد عدد الاستخدامات"""
        if self.usage_count < self.usage_limit:
            self.usage_count += 1
            if self.usage_count >= self.usage_limit:
                self.status = 'used'  # تحديث الحالة إذا تم استهلاك كل المحاولات
            self.save()
            return True
        return False
