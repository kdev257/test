# Generated by Django 4.2.15 on 2025-02-22 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0010_brand_finished_blend_item_brand_finished_goods_item_and_more'),
        ('production', '0025_production_report_production_report_line'),
    ]

    operations = [
        migrations.CreateModel(
            name='Map_Brand_SKU_Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brand_sku_item', to='masters.brand')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_sku', to='masters.item')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sku_item', to='masters.sku')),
            ],
        ),
    ]
