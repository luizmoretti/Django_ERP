# Generated by Django 4.2.9 on 2025-04-14 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='delivery',
            options={'ordering': ['-created_at'], 'permissions': [('view_own_delivery', 'Can view own delivery'), ('change_own_delivery_status', 'Can change own delivery status')], 'verbose_name': 'Delivery', 'verbose_name_plural': 'Deliveries'},
        ),
    ]
