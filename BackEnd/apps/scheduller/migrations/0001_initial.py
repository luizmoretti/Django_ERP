# Generated by Django 4.2.9 on 2025-04-15 12:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0003_alter_companie_type'),
        ('employeers', '0003_alter_employeer_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobsTypeSchedullerRegister',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('companie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_companie', to='companies.companie')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to='employeers.employeer')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated_by', to='employeers.employeer')),
            ],
            options={
                'verbose_name': 'Jobs Type Scheduller Register',
                'verbose_name_plural': 'Jobs Type Scheduller Registers',
            },
        ),
        migrations.CreateModel(
            name='Scheduller',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('start_time', models.TimeField(auto_now_add=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=250, null=True)),
                ('companie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_companie', to='companies.companie')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created_by', to='employeers.employeer')),
                ('jobs', models.ManyToManyField(blank=True, related_name='scheduller', to='scheduller.jobstypeschedullerregister')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated_by', to='employeers.employeer')),
            ],
            options={
                'verbose_name': 'Scheduller',
                'verbose_name_plural': 'Schedullers',
                'ordering': ['-created_at'],
            },
        ),
    ]
