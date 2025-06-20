# Generated by Django 4.2.15 on 2025-01-11 11:28

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_rename_excise_levies_mrn_items_excise_levies_export_and_more'),
        ('masters', '0005_alter_gst_on_goods_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_number', models.CharField(editable=False, max_length=100)),
                ('batch_quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('batch_date', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('status', models.CharField(default=100, max_length=20)),
                ('bom', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='stock.blend_bom')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blend_brand', to='masters.brand')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blend_creator', to=settings.AUTH_USER_MODEL)),
                ('transaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blend_unit', to='masters.unit')),
                ('uom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blend_uom', to='masters.unit_of_measurement')),
            ],
        ),
        migrations.CreateModel(
            name='Material_Requisition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requisition_number', models.CharField(max_length=20)),
                ('requisition_date', models.DateField()),
                ('production', models.DecimalField(decimal_places=2, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Production Quantity in Cases')),
                ('required_quantity', models.PositiveIntegerField(default=0)),
                ('blend', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stock.blend')),
                ('bom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.blend_bom')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.item')),
                ('transaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit')),
                ('uom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit_of_measurement')),
            ],
        ),
        migrations.CreateModel(
            name='Stock_Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_number', models.CharField(max_length=50)),
                ('transaction_date', models.DateField()),
                ('quantity', models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=20, validators=[django.core.validators.MinValueValidator(0.0, 'Reciept Quanity can not be less than 0')])),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('created', models.DateTimeField(blank=True, null=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('blend', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_blend', to='stock.blend')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_creator', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_item', to='masters.item')),
                ('mrn', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_mrn', to='inventory.mrn_items')),
                ('requisition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_requisition', to='stock.material_requisition')),
                ('stock_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_location', to='masters.unit_sub_location')),
                ('transaction_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_transaction_type', to='masters.transaction_type')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_entry_unit', to='masters.unit')),
            ],
        ),
        migrations.CreateModel(
            name='Stock_Ledger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opening_quantity', models.DecimalField(decimal_places=2, max_digits=50, validators=[django.core.validators.MinValueValidator(0.0, 'Opening Quanytity can not be less than 0')])),
                ('opening_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0.0, 'Opening value can not be less than 0')])),
                ('closing_quantity', models.DecimalField(decimal_places=2, max_digits=50, validators=[django.core.validators.MinValueValidator(0.0, 'Opening Quanytity can not be less than 0')])),
                ('closing_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0.0, 'Opening value can not be less than 0')])),
                ('average_rate', models.DecimalField(decimal_places=2, default=0, max_digits=20, validators=[django.core.validators.MinValueValidator(0.0, 'Average Rate can not be less than 0')])),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_ledger_item', to='masters.item')),
                ('stock_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_ledger_entry', to='stock.stock_entry')),
            ],
        ),
        migrations.AddConstraint(
            model_name='material_requisition',
            constraint=models.UniqueConstraint(fields=('bom', 'item', 'blend', 'requisition_date'), name='unique_bom_item_blend_requisition_date'),
        ),
    ]
