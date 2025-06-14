# Generated by Django 4.2.15 on 2025-05-11 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0012_remove_service_order_cost_center_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='service_order',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='service_order',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='service_order_items',
            name='cgst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='service_order_items',
            name='igst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='service_order_items',
            name='sgst',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
