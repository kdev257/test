# Generated by Django 4.2.15 on 2025-03-10 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0010_brand_finished_blend_item_brand_finished_goods_item_and_more'),
        ('production', '0033_production_report_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='map_brand_sku_item',
            name='stock_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit_stock_location'),
        ),
    ]
