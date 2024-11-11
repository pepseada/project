# Generated by Django 5.1.2 on 2024-10-24 04:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_code', models.CharField(max_length=10, unique=True)),
                ('user_email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('unused', 'Unused'), ('used', 'Used')], default='unused', max_length=10)),
                ('purchase_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
