# Generated by Django 5.2 on 2025-04-29 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_alter_profile_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='department',
            field=models.CharField(blank=True, choices=[('Executive', 'Executive'), ('Management', 'Management'), ('Sales', 'Sales'), ('Installation', 'Installation'), ('Warehouse', 'Warehouse'), ('Administration', 'Administration'), ('Finance', 'Finance'), ('HR', 'Human Resources')], help_text='Department of the user in the company', max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='position',
            field=models.CharField(blank=True, choices=[('Owner', 'Owner'), ('Director', 'Director'), ('Manager', 'Manager'), ('Salesperson', 'Salesperson'), ('Installer', 'Installer'), ('Stockist', 'Stockist')], help_text='Current position of the user', max_length=100),
        ),
    ]
