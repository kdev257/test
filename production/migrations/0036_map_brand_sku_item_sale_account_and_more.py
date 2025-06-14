# Generated by Django 4.2.15 on 2025-03-30 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0028_tcs_head_tcs'),
        ('production', '0035_alter_map_brand_sku_item_stock_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='map_brand_sku_item',
            name='sale_account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mapped_sale_account', to='masters.account_chart'),
        ),
        migrations.AlterField(
            model_name='map_brand_sku_item',
            name='account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mapped_finished_goods_account', to='masters.account_chart'),
        ),
    ]
