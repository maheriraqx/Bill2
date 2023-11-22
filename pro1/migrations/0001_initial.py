# Generated by Django 4.2.6 on 2023-11-12 05:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pro1.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15, null=True)),
                ('address', models.TextField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cashbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.IntegerField(null=True)),
                ('balance', models.IntegerField(null=True)),
                ('befor', models.IntegerField(null=True)),
                ('notes', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم الشركة')),
                ('branch', models.CharField(blank=True, max_length=255, null=True, verbose_name='الفرع')),
                ('address', models.TextField(verbose_name='عنوان الشركة')),
                ('email', models.EmailField(max_length=254, verbose_name='البريد الإلكتروني للشركة')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, verbose_name='رقم الهاتف')),
                ('logo', models.FileField(blank=True, null=True, upload_to='logo/')),
                ('logo_url', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
                ('spent_by', models.CharField(blank=True, max_length=100, null=True)),
                ('spent', models.BooleanField(default=False)),
                ('invoice_file', models.FileField(blank=True, null=True, upload_to='invoices/')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(default=pro1.models.generate_invoice_number, max_length=100, unique=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('payment', models.CharField(max_length=100, null=True)),
                ('balncagentlast', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('balncagentafter', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('admin', models.CharField(max_length=200, null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pro1.agent')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity_in_stock', models.DecimalField(decimal_places=1, max_digits=10)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('pakge', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('note', models.TextField(blank=True, null=True)),
                ('invoice', models.FileField(upload_to='invoices/')),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecurringExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('due_date', models.DateField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=1, max_digits=10, null=True)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('discount', models.DecimalField(decimal_places=1, max_digits=10, null=True)),
                ('quantity_after_discount', models.DecimalField(decimal_places=1, max_digits=10, null=True)),
                ('pkage_total', models.IntegerField(null=True)),
                ('pakge', models.IntegerField(null=True)),
                ('costperone_price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='pro1.invoice')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pro1.product')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='invoice_files/')),
                ('receipt', models.FileField(blank=True, null=True, upload_to='invoice_files/')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_files', to='pro1.invoice')),
            ],
        ),
        migrations.CreateModel(
            name='AgentTransaction3',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('purchase', 'Purchase'), ('payment', 'Payment')], max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('balance_last', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('receipt', models.FileField(blank=True, null=True, upload_to='receipts/', verbose_name='إيصال أو فاتورة')),
                ('date', models.DateField(auto_now=True)),
                ('time', models.TimeField(auto_now=True)),
                ('note', models.TextField(null=True)),
                ('invice_n', models.CharField(max_length=100, null=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='pro1.agent')),
            ],
        ),
    ]
