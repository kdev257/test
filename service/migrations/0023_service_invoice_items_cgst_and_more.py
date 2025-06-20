# Generated by Django 4.2.15 on 2025-05-31 17:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0022_service_invoice_inr_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service_invoice_items',
            name='cgst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='service_invoice_items',
            name='igst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='service_invoice_items',
            name='inr_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service_invoice_items',
            name='sgst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='service_invoice_items',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_invoice_items_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
