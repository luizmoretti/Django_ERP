# Generated by Django 4.2.9 on 2025-02-17 09:18

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0001_initial'),
        ('companies', '0003_alter_companie_type'),
        ('employeers', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSupplierID',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('in_store_id', models.CharField(blank=True, help_text='The id of the product in the supplier store', max_length=100, null=True)),
                ('companie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_companie', to='companies.companie')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to='employeers.employeer')),
                ('product', models.ForeignKey(help_text='The product of the sku', on_delete=django.db.models.deletion.CASCADE, related_name='supplier_ids', to='product.product')),
                ('supplier', models.ForeignKey(help_text='The supplier of the product', on_delete=django.db.models.deletion.CASCADE, related_name='product_supplier_ids', to='supplier.supplier')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated_by', to='employeers.employeer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
