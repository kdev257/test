# Generated by Django 4.2.15 on 2025-05-15 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0044_alter_user_roles_department'),
        ('service', '0016_remove_service_order_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='service_order',
            name='business',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='service_order_business', to='masters.business'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='service_order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Closed', 'Closed')], default='Pending', max_length=20),
        ),
    ]
