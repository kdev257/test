# Generated by Django 4.2.15 on 2025-04-07 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_purchase_order_service_supplier_invoice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotation',
            name='inland_haulage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
