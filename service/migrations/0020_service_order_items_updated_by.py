# Generated by Django 4.2.15 on 2025-05-24 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0019_service_order_items_status_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='service_order_items',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_order_items_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
