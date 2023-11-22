from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

import random
class Category_pro(models.Model):
    nameC = models.CharField(max_length=100)

def generate_invoice_number():
    # الحرف الأول للسلسلة
    prefix = 'A'
    # إضافة خمسة أرقام عشوائية بعد الحرف A
    numbers = ''.join(random.choices('0123456789', k=5))
    # الرقم النهائي للفاتورة
    return prefix + numbers


# استدعاء الدالة للتحقق

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات"

class Productx(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المنتج")
    description = models.TextField(verbose_name="الوصف", null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر التكلفة للقطعة")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر البيع للقطعة")
    manufacturer = models.CharField(max_length=100, verbose_name="الشركة المصنعة")
    quantity_in_stock = models.IntegerField(verbose_name="الكمية في المخزن")
    product_image = models.ImageField(upload_to='products/', verbose_name="صورة المنتج")
    is_available = models.BooleanField(default=True, verbose_name="متوفر")
    date_added = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإضافة")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="التصنيف")
    packing_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قيمة التعبئة" ,null=True)
    measurement_unit = models.CharField(max_length=50, verbose_name="وحدة القياس" ,null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="نسبة الخصم", default=0.00)

    def save(self, *args, **kwargs):
        if self.quantity_in_stock == 0:
            self.is_available = False
        else:
            self.is_available = True
        super().save(*args, **kwargs)

    @property
    def sale_price_after_discount(self):
        return round(self.sale_price * (1 - (self.discount_percentage / 100)))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "منتجات"



class Product(models.Model):
    name = models.CharField(max_length=100)

    quantity_in_stock = models.DecimalField(max_digits=15, decimal_places=1)
    cost_price = models.DecimalField(max_digits=15, decimal_places=1)
    cost = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    pakge = models.IntegerField(null=True)

    def __str__(self):
        return self.name


from django.db.models import Sum


class Agent(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True)
    address = models.TextField(max_length=255, null=True)

    # أية تفاصيل أخرى تخص الوكيل

    def get_balance(self):
        # تجميع المبالغ لعمليات الشراء والدفع بشكل منفصل
        total_purchases = self.transactions.filter(transaction_type='purchase').aggregate(total=Sum('amount'))[
                              'total'] or 0
        total_payments = self.transactions.filter(transaction_type='payment').aggregate(total=Sum('amount'))[
                             'total'] or 0

        # الرصيد هو إجمالي الشراء ناقص إجمالي الدفع
        balance = total_payments - total_purchases
        return balance

    def __str__(self):
        return self.name


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, default=generate_invoice_number, unique=True)
    date = models.DateTimeField(default=timezone.now)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    totalAmountbeforediscount = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    total = models.DecimalField(max_digits=15, decimal_places=1, null=True)

    payment = models.CharField(max_length=100, null=True)
    balncagentlast = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    balncagentafter = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    payment_date = models.DateField(null=True, blank=True)
    admin = models.CharField(max_length=255, null=True)
    notes = models.TextField(null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=1, default=0.0)


    # يمكن تركه فارغًا إذا لم يتم تحديد تاريخ التسديد بعد
    # أية تفاصيل أخرى ترغب في تخزينها للفاتورة

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Productx, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    selling_price = models.DecimalField(max_digits=15, decimal_places=1)
    total = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    discount = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    quantity_after_discount = models.DecimalField(max_digits=15, decimal_places=1, null=True)
    pkage_total = models.IntegerField(null=True)
    pakge = models.IntegerField(null=True)
    costperone_price = models.DecimalField(max_digits=15, decimal_places=1, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Cashbox(models.Model):
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255)
    amount = models.IntegerField(null=True)
    balance = models.IntegerField(null=True)
    befor = models.IntegerField(null=True)
    notes = models.TextField(null=True)


class InvoiceFile(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='pdf_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='invoice_files/')
    receipt = models.FileField(upload_to='invoice_files/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"File for {self.invoice.invoice_number}"


class Purchase(models.Model):
    product_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=15, decimal_places=1)
    cost_price = models.DecimalField(max_digits=15, decimal_places=1)
    total_cost = models.DecimalField(max_digits=15, decimal_places=1)
    note = models.TextField(blank=True, null=True)
    invoice = models.FileField(upload_to='invoices/')
    date = models.DateTimeField(auto_now_add=True)
    supplier = models.CharField(null=True, max_length=255)

    def __str__(self):
        return self.product_name


class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=1)
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    spent_by = models.CharField(max_length=100, blank=True, null=True)
    spent = models.BooleanField(default=False)
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class RecurringExpense(models.Model):
    # وصف المصروف المتكرر
    description = models.CharField(max_length=255)
    # المبلغ المصروف
    amount = models.DecimalField(max_digits=15, decimal_places=1)
    # تاريخ بدء المصروفات المتكررة
    start_date = models.DateField(default=timezone.now)
    # تاريخ الاستحقاق الشهري للمصروف
    due_date = models.DateField()
    # ملاحظات إضافية حول المصروف المتكرر
    notes = models.TextField(blank=True, null=True)
    # حقل لتحديد ما إذا كان المصروف ما زال نشطًا
    active = models.BooleanField(default=True)
    # قد ترغب في إضافة حقل لتصنيف المصروفات المتكررة
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"


from django.db import models


class CompanyInfo(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم الشركة")
    branch = models.CharField(max_length=255, verbose_name="الفرع", blank=True, null=True)
    address = models.TextField(verbose_name="عنوان الشركة")
    email = models.EmailField(verbose_name="البريد الإلكتروني للشركة")
    phone = models.CharField(max_length=50, verbose_name="رقم الهاتف", blank=True, null=True)
    logo = models.FileField(upload_to='logo/', null=True, blank=True)
    logo_url = models.TextField(null=True)

    def __str__(self):
        return f"{self.name} - {self.branch}" if self.branch else self.name


from decimal import Decimal
from django.utils.crypto import get_random_string
import time
from datetime import datetime
import uuid

import random
import string
import random


def generate_invoice_number2():
    # الحرف الأول للسلسلة
    prefix = 'B'
    # إضافة خمسة أرقام عشوائية بعد الحرف A
    numbers = ''.join(random.choices('0123456789', k=5))
    # الرقم النهائي للفاتورة
    return prefix + numbers


class AgentTransaction3(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('payment', 'Payment'),
    )

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=100, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=1)
    balance = models.DecimalField(max_digits=15, decimal_places=1, default=0)
    balance_last = models.DecimalField(max_digits=15, decimal_places=1, default=0)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True, verbose_name="إيصال أو فاتورة")
    receipt_empty = models.FileField(upload_to='receipts/', null=True, blank=True, verbose_name=" فاتورة")
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)
    note = models.TextField(null=True)
    invice_n = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # إذا لم يتم تحديد رقم الفاتورة، قم بتوليده تلقائيًا
        if not self.invice_n:
            self.invice_n = generate_invoice_number2()
        super(AgentTransaction3, self).save(*args, **kwargs)


class Archive(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='archives')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='archives/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.agent.name}"


class Supplier(models.Model):
    company_name = models.CharField(max_length=200, verbose_name="اسم الشركة/التاجر")
    address = models.TextField(verbose_name="العنوان")
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    website = models.URLField(blank=True, null=True, verbose_name="الموقع الإلكتروني")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"


