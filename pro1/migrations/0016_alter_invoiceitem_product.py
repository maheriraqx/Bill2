# Generated by Django 4.2.6 on 2023-11-22 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pro1', '0015_productx_discount_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pro1.productx'),
        ),
    ]