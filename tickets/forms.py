from django import forms

class TicketCheckForm(forms.Form):
    ticket_code = forms.CharField(max_length=10, label='كود التذكرة')
