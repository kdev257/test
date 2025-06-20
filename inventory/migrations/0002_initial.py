# Generated by Django 4.2.15 on 2025-01-02 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0001_initial'),
        ('masters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle_unloading_report',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='vehicle_unloading_report',
            name='gate_entry',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='inventory.gate_entry'),
        ),
        migrations.AddField(
            model_name='vehicle_unloading_report',
            name='transaction_type',
            field=models.ForeignKey(default=22, on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='vehicle_unloading_report',
            name='unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.unit'),
        ),
        migrations.AddField(
            model_name='vehicle_unload_items',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unloaded_item', to='masters.item'),
        ),
        migrations.AddField(
            model_name='vehicle_unload_items',
            name='vur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unloaded_item', to='inventory.vehicle_unloading_report', verbose_name='Vehicle_Unload_Report'),
        ),
        migrations.AddField(
            model_name='tax_table',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.supplier'),
        ),
        migrations.AddField(
            model_name='tax_table',
            name='transaction_type',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='tax_table',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit'),
        ),
        migrations.AddField(
            model_name='quotation_items',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.item'),
        ),
        migrations.AddField(
            model_name='quotation_items',
            name='quotation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotation_item', to='inventory.quotation'),
        ),
        migrations.AddField(
            model_name='quotation',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='q_approver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quotation',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='q_creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quotation',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.currency'),
        ),
        migrations.AddField(
            model_name='quotation',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quo_supplier', to='masters.supplier'),
        ),
        migrations.AddField(
            model_name='quotation',
            name='transaction_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='quotation',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quo_unit', to='masters.unit'),
        ),
        migrations.AddField(
            model_name='quality_check',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quality_check',
            name='gate_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.gate_entry'),
        ),
        migrations.AddField(
            model_name='quality_check',
            name='specification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.standard_quality_specifications'),
        ),
        migrations.AddField(
            model_name='quality_check',
            name='transaction_type',
            field=models.ForeignKey(default=21, on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='quality_check',
            name='unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.unit'),
        ),
        migrations.AddField(
            model_name='purchase_order_items',
            name='purchase_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='inventory.purchase_order'),
        ),
        migrations.AddField(
            model_name='purchase_order_items',
            name='quotation_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.item'),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='purchase_order_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='business',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='masters.business'),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='freight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.freight', verbose_name='Freight_Rule'),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='quotation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quote', to='inventory.quotation'),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='transaction_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='purchase_order',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='po_unit', to='masters.unit'),
        ),
        migrations.AddField(
            model_name='po_lcr_join',
            name='clearance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.supplier_service'),
        ),
        migrations.AddField(
            model_name='po_lcr_join',
            name='freight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='join_freight', to='masters.freight'),
        ),
        migrations.AddField(
            model_name='po_lcr_join',
            name='lcr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_lcr', to='masters.landed_cost_rule'),
        ),
        migrations.AddField(
            model_name='po_lcr_join',
            name='po',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='join_po', to='inventory.purchase_order'),
        ),
        migrations.AddField(
            model_name='mrn_items',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mrn_item', to='masters.item'),
        ),
        migrations.AddField(
            model_name='mrn_items',
            name='mrn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mrn_instance', to='inventory.material_receipt_note'),
        ),
        migrations.AddField(
            model_name='mrn_items',
            name='stock_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit_sub_location'),
        ),
        migrations.AddField(
            model_name='mrn_items',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit'),
        ),
        migrations.AddField(
            model_name='material_receipt_note',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='approver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='material_receipt_note',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='material_receipt_note',
            name='gate_entry',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='related_ge', to='inventory.gate_entry'),
        ),
        migrations.AddField(
            model_name='material_receipt_note',
            name='transaction_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='material_receipt_note',
            name='unit',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.unit'),
        ),
        migrations.AddField(
            model_name='material_receipt_note',
            name='unload_report',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='unloaded_items', to='inventory.vehicle_unloading_report'),
        ),
        migrations.AddField(
            model_name='gate_entry',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gate_entry',
            name='item_cat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.item_category'),
        ),
        migrations.AddField(
            model_name='gate_entry',
            name='po',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.purchase_order', verbose_name='Enter Purchase Order Number'),
        ),
        migrations.AddField(
            model_name='gate_entry',
            name='transaction_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='gate_entry',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='masters.unit'),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='frt_approved_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='business',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='service_business', to='masters.business'),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='po',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.purchase_order'),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='service',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='masters.service'),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transporter', to='masters.supplier'),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='transaction_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='masters.transaction_type'),
        ),
        migrations.AddField(
            model_name='freight_purchase_order',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frt_unit', to='masters.unit'),
        ),
        migrations.AlterUniqueTogether(
            name='quality_check',
            unique_together={('gate_entry', 'specification')},
        ),
        migrations.AddIndex(
            model_name='material_receipt_note',
            index=models.Index(fields=['mrn_number', 'mrn_date'], name='inventory_m_mrn_num_c8ce92_idx'),
        ),
    ]
