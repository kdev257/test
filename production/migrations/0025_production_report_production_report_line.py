# Generated by Django 4.2.15 on 2025-02-22 17:48

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0010_brand_finished_blend_item_brand_finished_goods_item_and_more'),
        ('stock', '0013_alter_stock_ledger_stock_entry'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('production', '0024_daily_production_plan_bottled'),
    ]

    operations = [
        migrations.CreateModel(
            name='Production_Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_number', models.CharField(max_length=30)),
                ('transaction_date', models.DateField()),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_report_created_by', to=settings.AUTH_USER_MODEL)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_report_plan', to='production.daily_production_plan')),
                ('transaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_report_unit', to='masters.unit')),
            ],
        ),
        migrations.CreateModel(
            name='Production_Report_Line',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Production in Cases')),
                ('production_value', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('average_cost', models.DecimalField(decimal_places=4, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('blend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_report_blend', to='stock.blend')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='production_report_brand', to='masters.brand')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='production_report_item', to='masters.item')),
                ('line', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='production_report_line', to='production.bottling_lines')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_report_line', to='production.production_report')),
                ('sku', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='production_report_sku', to='masters.sku')),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.state')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_report_line_unit', to='masters.unit')),
            ],
        ),
    ]
