# Generated by Django 4.2.9 on 2025-03-19 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendanceregister',
            name='acess_code',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
    ]
