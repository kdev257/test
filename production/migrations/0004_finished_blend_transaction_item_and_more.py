# Generated by Django 4.2.15 on 2025-01-28 11:12

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0010_brand_finished_blend_item_brand_finished_goods_item_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stock', '0009_stock_entry_return_quantity_stock_entry_return_value'),
        ('production', '0003_finished_blend_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='finished_blend_transaction',
            name='item',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Finished_blend_item', to='masters.item'),
        ),
        migrations.CreateModel(
            name='Finished_blend_Stock_Ledger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_number', models.CharField(max_length=30)),
                ('transaction_date', models.DateField()),
                ('opening_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('opening_value', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('opening_rate', models.DecimalField(decimal_places=4, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('receipt_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('receipt_value', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('receipt_rate', models.DecimalField(decimal_places=4, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('issue_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('issue_value', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('issue_rate', models.DecimalField(decimal_places=4, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('closing_quantity', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('closing_value', models.DecimalField(decimal_places=2, default=0, max_digits=30, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('closing_rate', models.DecimalField(decimal_places=4, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('blend', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='finished_blend_stock', to='stock.blend')),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='finished_blend_brand', to='masters.brand')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_ledger_created_by', to=settings.AUTH_USER_MODEL)),
                ('transaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit')),
            ],
        ),
    ]
