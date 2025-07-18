# Generated by Django 5.2 on 2025-05-08 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_alter_companie_type'),
        ('customers', '0004_alter_customerleads_options_and_more'),
        ('employeers', '0003_alter_employeer_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customerleads',
            options={'ordering': ['-created_at'], 'verbose_name': 'Customer Lead', 'verbose_name_plural': 'Customer Leads'},
        ),
        migrations.AlterField(
            model_name='customerleads',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Contacted', 'Contacted'), ('Interested', 'Interested'), ('Converted', 'Converted'), ('Rejected', 'Rejected')], default='New', max_length=50),
        ),
        migrations.AddIndex(
            model_name='customerleads',
            index=models.Index(fields=['-created_at'], name='customers_c_created_6b051f_idx'),
        ),
    ]
