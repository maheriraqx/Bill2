# استدعاءات Django والمكتبات المرتبطة بـ Django
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Q, Sum, DecimalField
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.core import serializers
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone

# استدعاءات المكتبات الخارجية
from weasyprint import HTML
from io import BytesIO
import qrcode
import os
from decimal import Decimal

# استدعاء النماذج من التطبيق الحالي
from .models import (
    Agent, Product, Invoice, InvoiceItem, Cashbox, InvoiceFile,
    Purchase, Expense, CompanyInfo, AgentTransaction3, Archive, Supplier,Productx
)
from pro1.tests import top_five_monthly_sold_products,top_ten_monthly_most_profitable_products

# وظيفة تعالج عملية تسجيل الدخول
def login_view(request):
    # التحقق من نوع الطلب، إذا كان POST (إرسال بيانات)
    if request.method == 'POST':
        # استرداد اسم المستخدم من الطلب
        username = request.POST.get('username')
        # استرداد كلمة المرور من الطلب
        password = request.POST.get('password')
        # محاولة مصادقة المستخدم
        user = authenticate(request, username=username, password=password)
        # التحقق إذا كان المستخدم موجودًا وصحيحًا
        if user is not None:
            # تسجيل دخول المستخدم
            login(request, user)
            # توجيه المستخدم إلى اللوحة الرئيسية بعد تسجيل الدخول
            return redirect('dashb')
        else:
            # إرجاع رسالة خطأ إذا كانت بيانات الاعتماد غير صحيحة
            return render(request, 'login.html', {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة.'})
    # إذا لم يكن الطلب من نوع POST، عرض صفحة تسجيل الدخول
    return render(request, 'login.html')


# وظيفة لتسجيل خروج المستخدم
def logout_view(request):
    # تسجيل خروج المستخدم
    logout(request)
    # توجيه المستخدم إلى صفحة تسجيل الدخول بعد الخروج
    return redirect('login')


# وظيفة لحساب مبيعات اليوم
def get_todays_sales():
    # الحصول على تاريخ اليوم
    today = timezone.now().date()
    # استرجاع إجمالي مبيعات اليوم
    todays_sales = Invoice.objects.filter(date__date=today).aggregate(total_sales=Sum('total'))['total_sales']
    # إرجاع القيمة أو 0 إذا كانت فارغة
    return todays_sales or 0


# وظيفة لحساب مبيعات الشهر الحالي
def get_this_months_sales():
    # الحصول على التاريخ الحالي
    today = timezone.now()
    # تحديد بداية الشهر
    start_of_month = today.replace(day=1)
    # استرجاع إجمالي مبيعات الشهر الحالي
    this_months_sales = Invoice.objects.filter(date__range=[start_of_month, today]).aggregate(total_sales=Sum('total'))[
        'total_sales']
    # إرجاع القيمة أو 0 إذا كانت فارغة
    return this_months_sales or 0


# وظيفة لحساب مبيعات السنة الحالية
def get_this_years_sales():
    # الحصول على التاريخ الحالي
    today = timezone.now()
    # تحديد بداية السنة
    start_of_year = today.replace(month=1, day=1)
    # استرجاع إجمالي مبيعات السنة الحالية
    this_years_sales = Invoice.objects.filter(date__range=[start_of_year, today]).aggregate(total_sales=Sum('total'))[
        'total_sales']
    # إرجاع القيمة أو 0 إذا كانت فارغة
    return this_years_sales or 0


# وظيفة لحساب إجمالي الديون
def calculate_total_debts():
    total_debt = 0
    # الحصول على جميع الوكلاء
    agents = Agent.objects.all()

    for agent in agents:
        # الحصول على رصيد كل وكيل
        balance = agent.get_balance()
        # التحقق إذا كان الرصيد سالبًا (دين)
        if balance < 0:
            total_debt += balance

    # إرجاع القيمة المطلقة لإجمالي الديون
    return abs(total_debt)


# وظيفة مشابهة لحساب الديون ولكن بشرط مختلف
def calculate_total_debts_comp():
    total_debt = 0
    agents = Agent.objects.all()

    for agent in agents:
        balance = agent.get_balance()
        # التحقق إذا كان الرصيد موجبًا
        if balance > 0:
            total_debt += balance

    # إرجاع القيمة المطلقة لإجمالي الديون
    return abs(total_debt)


# وظيفة لحساب حجم مجلد بالميغابايت
def get_folder_size_mb(folder_path):
    total_size = 0
    # تصفح جميع الملفات في المجلد ومجلداته الفرعية
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            # الحصول على المسار الكامل لكل ملف
            fp = os.path.join(dirpath, f)
            # التحقق إذا كان الملف موجودًا واحتساب حجمه
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    # تحويل الحجم من بايت إلى ميغابايت وإرجاعه
    return total_size / (1024 * 1024)


# وظيفة تعرض اللوحة الرئيسية مع المعلومات المحتسبة
@login_required  # تأكد من أن المستخدم قد سجل الدخول
def dashb(request):
    # حساب مبيعات اليوم
    todays_sales = get_todays_sales()
    # إعداد البيانات لإرسالها إلى القالب
    context = {
        'todays_sales': todays_sales,
        'current_month_sales': get_this_months_sales(),
        'current_year_sales': get_this_years_sales(),
        'total_debts': calculate_total_debts(),
        'calculate_total_debts_comp': calculate_total_debts_comp(),
        'usedMb': 0,
        'top_five_monthly_sold_products':top_five_monthly_sold_products(),
        'top_ten_monthly_most_profitable_products':top_ten_monthly_most_profitable_products()
    }

    # عرض القالب مع البيانات المحتسبة
    return render(request, 'dash.html', context)


# وظيفة لإنشاء فاتورة جديدة
@login_required  # تأكد من أن المستخدم قد سجل الدخول
def create_invoice_view(request):
    # الحصول على جميع الوكلاء والمنتجات لعرضها في القالب
    agents = Agent.objects.all()
    products = Product.objects.all()
    # عرض القالب مع البيانات المحتسبة
    return render(request, 'addbil.html', {'agents': agents, 'products': products})


def create_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io


def creatpdffile(number, Company, admin):
    from io import BytesIO
    import base64

    invoice = Invoice.objects.get(invoice_number=number)
    from datetime import datetime
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    # Get additional data if needed (e.g., agent, items).
    qr_url = f'http://185.213.22.106/media/receipts/{number}_.pdf'
    qr_code_image = create_qr_code(qr_url)
    qr_code_base64 = base64.b64encode(qr_code_image.getvalue()).decode()
    context = {
        'agent': invoice.agent,
        'invoice': invoice,
        'items': invoice.items.all(),
        'Company': Company,
        'today_date': current_date,
        'current_time': current_time,
        'admin': admin,
        'qr_code': qr_code_base64

    }

    # Render the HTML template with context data.
    html_string = render_to_string('inv.html', context)

    pdf_file_io = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file_io)
    pdf_file_io.seek(0)
    return pdf_file_io


def creatpdffileEmpty(number, Company, admin):
    invoice = Invoice.objects.get(invoice_number=number)
    from datetime import datetime
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    # Get additional data if needed (e.g., agent, items).
    context = {
        'agent': invoice.agent,
        'invoice': invoice,
        'items': invoice.items.all(),
        'Company': Company,
        'today_date': current_date,
        'current_time': current_time,
        'admin': admin

    }

    # Render the HTML template with context data.
    html_string = render_to_string('emptyinv.html', context)

    pdf_file_io = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file_io, size='A4')
    pdf_file_io.seek(0)
    return pdf_file_io


def agent_transactions(transaction_type, name, amount, invoice_number, company, notes, admin):
    agent = Agent.objects.get(name=name)
    agent_transaction = AgentTransaction3(
        agent=agent,
        transaction_type=transaction_type,
        amount=Decimal(amount),
        balance_last=agent.get_balance(),
        balance=agent.get_balance() - Decimal(amount),
        note=notes,
        invice_n=invoice_number
    )

    # إنشاء ملف PDF
    pdf_file_io = creatpdffile(invoice_number, company, admin)
    pdf_file_empty = creatpdffileEmpty(invoice_number, company, admin)

    # حفظ ملف PDF في الحركة
    pdf_file_name = f"{invoice_number}_.pdf"
    pdf_file_name_empty = f"empty_{invoice_number}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
    agent_transaction.receipt.save(pdf_file_name, ContentFile(pdf_file_io.read()))
    agent_transaction.receipt_empty.save(pdf_file_name_empty, ContentFile(pdf_file_empty.read()))

    agent_transaction.save()

from .models import Productx
def create_invoice(agent_name, product_data, total_amount, payment, prod, useradmin, notes, admin,discount_total,totalAmountbeforediscount):
    with transaction.atomic():
        updated_products = []
        # إيجاد الوكيل أو إنشاء واحد جديد إذا لم يكن موجود
        agent, created = Agent.objects.get_or_create(name=agent_name)
        if payment == 'بيع بالأجل':
            invoice = Invoice(
                agent=agent,
                total=total_amount,
                payment=payment,
                balncagentlast=agent.get_balance(),
                balncagentafter=agent.get_balance() - Decimal(total_amount),
                admin=useradmin,
                notes=notes,
                discount=discount_total,
                totalAmountbeforediscount=totalAmountbeforediscount

            )
            invoice.save()

        for item in product_data:
            try:
                product = Productx.objects.get(name=item['product_name'])
            except ObjectDoesNotExist:
                print(f"Product {item['product_name']} does not exist.")
                continue

            if float(product.quantity_in_stock) >= item['quantity']:
                product.quantity_in_stock -= Decimal(item['quantity'])
                product.save()
                updated_products.append((product, Decimal(item['quantity'])))

                item_total = item['quantity'] * item['quantity_after']
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=item['quantity'],
                    selling_price=item['selling_price'],
                    total=item_total,  # إضافة المبلغ الإجمالي لهذا البند
                    discount=item['discount'],
                    quantity_after_discount=Decimal(item['quantity_after']),
                    pkage_total=item['pkage_total'],
                    pakge=prod.get(name=item['product_name']).packing_value,
                    costperone_price=prod.get(name=item['product_name']).cost_price
                )
            else:
                continue
        print(len(product_data))
        print(InvoiceItem.objects.filter(invoice=invoice).count())
        if len(product_data) != InvoiceItem.objects.filter(invoice=invoice).count():
            for product, quantity in updated_products:
                product.quantity_in_stock += quantity  # استخدام الكمية المخزنة
                product.save()
            invoice.delete()
            return None
        else:
            total_from_items = sum(item.total for item in InvoiceItem.objects.filter(invoice=invoice))
            invoice.total = total_amount
            invoice.save()
            Company = CompanyInfo.objects.last()
            agent_transactions('purchase', agent, total_amount, invoice.invoice_number, Company, notes, admin)
            return invoice


@require_http_methods(["GET"])
def getbils(request):
    # استخراج البيانات من الطلب
    agent_name = request.GET.get('agent_name')
    total_amount = request.GET.get('total_amount')
    notes = request.GET.get('notes')
    discount_total = request.GET.get('discount_total')
    totalAmountbeforediscount = request.GET.get('totalAmountbeforediscount')
    payment = 'بيع بالأجل'

    # استخراج قوائم المنتجات
    product_names = request.GET.getlist('product_name')
    quantities = request.GET.getlist('quantity')
    selling_prices = request.GET.getlist('selling_price')
    discounts = request.GET.getlist('discounts')
    quantitys_after = request.GET.getlist('quantity_after')
    pkage_totals = request.GET.getlist('pkage_total')

    # التحقق من أن لدينا قوائم متساوية الطول
    if not (len(product_names) == len(quantities) == len(selling_prices)):
        return HttpResponse('البيانات المرسلة غير متناسقة', status=400)

    # إنشاء قائمة القواميس لكل منتج
    product_data = []
    for name, quantity, price, discount, quantity_after, pkage_total in zip(product_names, quantities, selling_prices,
                                                                            discounts, quantitys_after, pkage_totals):
        try:

            product_info = {
                'product_name': name,
                'quantity': float(quantity),
                'selling_price': float(price),
                'discount': float(str(discount).strip('%')),
                'quantity_after': float(quantity_after),
                'pkage_total': int(pkage_total),
            }
            product_data.append(product_info)
            print(product_data)
            print(agent_name)
        except ValueError as e:
            # يمكن هنا التعامل مع القيم الخاطئة أو تسجيل الخطأ
            return HttpResponse(f'قيمة غير صحيحة: {e}', status=400)

    # الآن لديك قائمة product_data التي يمكنك استخدامها لإنشاء الفاتورة

    print(
        create_invoice(agent_name, product_data, total_amount, payment, Productx.objects.all(), request.user.first_name,
                       notes, request.user.first_name,discount_total,totalAmountbeforediscount))
    return redirect(reverse('agent_account_statement', kwargs={'agent_id': Agent.objects.get(name=agent_name).id}))


@login_required
def invoice_list(request):
    # استلام معلمات البحث من الطلب
    search_query = request.GET.get('search', '')
    min_date_str = request.GET.get('min_date', '')
    max_date_str = request.GET.get('max_date', '')

    # بداية الاستعلام الأساسي
    invoices_query = Invoice.objects.all()

    # إذا كان هناك استعلام بحث، قم بتصفية النتائج
    if search_query:
        invoices_query = invoices_query.filter(
            Q(invoice_number__icontains=search_query) |
            Q(agent__name__icontains=search_query)
        )

    # إذا تم تحديد تاريخ البداية، قم بتصفية النتائج لتشمل الفواتير بعد هذا التاريخ
    if min_date_str:
        min_date = datetime.datetime.strptime(min_date_str, '%Y-%m-%d').date()
        invoices_query = invoices_query.filter(date__gte=min_date)

    # إذا تم تحديد تاريخ النهاية، قم بتصفية النتائج لتشمل الفواتير قبل هذا التاريخ
    if max_date_str:
        max_date = datetime.datetime.strptime(max_date_str, '%Y-%m-%d').date()
        invoices_query = invoices_query.filter(date__lte=max_date)

    # بناء قائمة الفواتير مع البيانات المطلوبة
    invoices_list = []
    for invoice in invoices_query.all().order_by('-date'):
        count = InvoiceItem.objects.filter(invoice=invoice).count()
        invoices_list.append({
            'invoice_number': invoice.invoice_number,
            'agent': invoice.agent.name,
            'date': invoice.date.strftime('%Y-%m-%d %H:%M'),  # تنسيق التاريخ
            'total': invoice.total,
            'balncagentafter': invoice.balncagentafter,
            'balncagentlast': invoice.balncagentlast,
            'admin': invoice.admin
        })

    return render(request, 'list_invoices.html',
                  {'invoices': invoices_list, 'search_query': search_query, 'min_date_str': min_date_str,
                   'max_date_str': max_date_str, })


"""@login_required
def deletinvoice(request,number):
    invoice = Invoice.objects.get(invoice_number=number)
    invoiceItem = invoice.items.all()
    for c in invoiceItem:
        name= c.product.name
        print(c.product.name)
        print(c.quantity_after_discount)
        pro = Product.objects.get(name=name)
        pro.quantity_in_stock += c.quantity_after_discount
        pro.save()
    invoice.delete()

    return redirect('invoice_list')"""


@login_required
def cashbox_statement(request):
    # تحديد تاريخ بداية الشهر الحالي
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # إنشاء استعلام للبحث عن العمليات في الشهر الحالي
    cashbox_query = Cashbox.objects.filter(date__gte=start_of_month)

    # تحقق إذا كانت هناك بيانات بحث مرسلة
    if 'start_date' in request.GET and 'end_date' in request.GET and 'search_term' in request.GET:
        start_date = request.GET['start_date']
        end_date = request.GET['end_date']
        search_term = request.GET['search_term']

        # إذا تم توفير تاريخ بداية وتاريخ نهاية، قم بتحديث الاستعلام
        if start_date and end_date:
            cashbox_query = cashbox_query.filter(date__range=[start_date, end_date])

        # إذا تم توفير كلمة بحث، قم بتحديث الاستعلام
        if search_term:
            cashbox_query = cashbox_query.filter(
                Q(description__icontains=search_term) |
                Q(notes__icontains=search_term)
            )

    # ترتيب النتائج بحيث تكون الأحدث في الأعلى
    cashbox_query = cashbox_query.order_by('-date')

    context = {
        'cashbox': cashbox_query,
        'current_balance': cashbox_query.first().balance if cashbox_query.exists() else 0
    }
    return render(request, 'cashbox.html', context)


@login_required
def cashbox_deposit(request):
    try:
        last = Cashbox.objects.last().balance
    except:
        last = 0
    return render(request, 'deposit.html', {'balancr': last})


@login_required
def cashbox_deposit_action(request):
    amount = request.GET.get('amount', 0)
    notes = request.GET.get('notes')
    try:
        last = Cashbox.objects.all().last().balance
    except:
        last = 0
    Cashbox.objects.create(
        amount=int(amount),
        balance=last + int(amount),
        notes=notes,
        befor=last,
        description='ايداع'
    )

    return redirect('dashb')


@login_required
def cashbox_withdraw(request):
    try:
        last = Cashbox.objects.last().balance
    except:
        last = 0

    return render(request, 'cashbox_withdraw.html', {'balancr': last})


@login_required
def cashbox_withdraw_action(request):
    amount = request.GET.get('amount', 0)
    notes = request.GET.get('notes')
    try:
        last = Cashbox.objects.all().last().balance
    except:
        last = 0
    Cashbox.objects.create(
        amount=int(amount),
        balance=last - int(amount),
        notes=notes,
        befor=last,
        description='سحب'
    )
    return redirect('dashb')


@login_required
def invoiceprint(request, number, comp):
    # Get the Invoice object using the provided number.
    invoice = Invoice.objects.get(invoice_number=number)
    from datetime import datetime
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    # Get additional data if needed (e.g., agent, items).
    context = {
        'agent': invoice.agent,
        'invoice': invoice,
        'items': invoice.items.all(),
        'Company': comp,
        'today_date': current_date,
        'current_time': current_time,
    }

    # Render the HTML template with context data.
    html_string = render_to_string('inv.html', context)

    pdf_file_io = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file_io, size='A4')
    pdf_file_io.seek(0)

    # إنشاء اسم ملف PDF بناءً على الفاتورة والوقت الحالي
    pdf_file_name = f"{invoice.invoice_number}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # إنشاء كائن InvoiceFile جديد وحفظه
    invoice_file = InvoiceFile(invoice=invoice)
    invoice_file.file.save(pdf_file_name, ContentFile(pdf_file_io.read()), save=True)
    invoice_file.save()

    return redirect('invoice_list')


################################################################################
###############################################################################


def rpeset(request, number):
    # Get the Invoice object using the provided number.
    invoice = Invoice.objects.get(invoice_number=number)
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    # Get additional data if needed (e.g., agent, items).
    context = {
        'agent': invoice.agent,
        'invoice': invoice,
        'items': invoice.items.all(),
        'comp': CompanyInfo.objects.last(),
        'admin': request.user.first_name,
        'today_date': current_date,
        'current_time': current_time,
    }
    # Render the HTML template with context data.
    html_string = render_to_string('mt.html', context)

    pdf_file_io = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file_io)
    pdf_file_io.seek(0)

    # إنشاء اسم ملف PDF بناءً على الفاتورة والوقت الحالي
    pdf_file_name = f"receipt_{invoice.invoice_number}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # إنشاء كائن InvoiceFile جديد وحفظه
    invoice_file = InvoiceFile(invoice=invoice)
    invoice_file.receipt.save(pdf_file_name, ContentFile(pdf_file_io.read()), save=True)
    invoice_file.save()


@login_required
def payment(request):
    amount = request.GET['payment_amount']
    invoice_number = request.GET['invoice_number']
    invoicr = Invoice.objects.get(invoice_number=invoice_number)
    invoicr.payment = 'مدفوع'
    invoicr.payment_date = timezone.now()
    invoicr.save()
    comp = CompanyInfo.objects.last()
    invoiceprint(request, invoice_number, comp)
    rpeset(request, invoice_number)
    iss = Invoice.objects.get(invoice_number=invoice_number)
    last = Cashbox.objects.all().last().balance
    print(last)
    Cashbox.objects.create(
        amount=int(amount),
        description='تسديد',
        befor=last,
        balance=int(last) + int(amount),
        notes=f"""
    <div style="text-align: center; border: 1px solid #47933a; padding: 5px; margin: 10px;">
    <h5 style="border-bottom: 1px solid #ccc;">وصل قبض مبلغ</h5>
    <div style="margin: 10px 0;margin-top: 10px">
        <strong> </strong> <span style="color: orangered">{iss.invoice_number}</span> :رقم الفاتورة
    </div>
    <div style="margin: 10px 0;">
        <strong>اسم الوكيل/التاجر:</strong> <span>{iss.agent.name}</span>
    </div>
    <div style="margin: 10px 0;">
        <strong>المبلغ المسدد:</strong> <span>{iss.amount_paid} د.ع </span>
    </div>
    <div style="margin: 10px 0;">
        <strong>المبلغ المتبقي:</strong> <span>{iss.remaining_amount} د.ع </span>
    </div>
    <div style="margin: 10px 0;direction: rtl">
        <strong>الموضف:</strong> <span>{request.user.first_name}  </span>
    </div>
</div>
        """

    )
    return redirect('invoice_list')


def detils(request, number):
    invoice = Invoice.objects.get(invoice_number=number)
    context = {
        'invoice': invoice
    }
    return render(request, 'bill.html', context)


@login_required
def inviocefile(request, number):
    # Get the Invoice object using the provided number.
    invoice = Invoice.objects.get(invoice_number=number)
    from datetime import datetime
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    # Get additional data if needed (e.g., agent, items).
    context = {
        'agent': invoice.agent,
        'invoice': invoice,
        'items': invoice.items.all(),
        'Company': CompanyInfo.objects.last(),
        'today_date': current_date,
        'current_time': current_time,
    }

    # Get additional data if needed (e.g., agent, items).

    return render(request, 'inv.html', context)


@login_required
def inventory_audit(request):
    from django.db.models import Sum, F
    search_name = request.GET.get('searchName', '')
    search_category = request.GET.get('searchCategory', '')

    products_query = Productx.objects.all()

    if search_name:
        products_query = products_query.filter(name__icontains=search_name)

    if search_category:
        products_query = products_query.filter(category=Category.objects.get(name=search_category))
    total_cost = products_query.aggregate(
        total=Sum(F('quantity_in_stock') * F('sale_price'))
    )['total'] or 0
    count = products_query.all().count()
    products_data = []
    for product in products_query :
        # تعديل الحقول النصية لإزالة الاقتباسات المزدوجة
        product_data = {
            "name": product.name.replace('"', ''),
            "description": product.description.replace('"', '').replace("'","") if product.description else '',
            "cost_price": float(product.cost_price),
            "sale_price": float(product.sale_price),
            "manufacturer": product.manufacturer.replace('"', ''),
            "quantity_in_stock": product.quantity_in_stock,
            "product_image": product.product_image.url,  # تحويل مسار الصورة إلى نص
            "is_available": product.is_available,
            "date_added": product.date_added.strftime("%Y-%m-%dT%H:%M:%SZ"),  # تحويل التاريخ إلى نص
            "category": product.category.id if product.category else None,  # تحويل الفئة إلى معرف رقمي
            "packing_value": float(product.packing_value),
            "measurement_unit": product.measurement_unit.replace('"', ''),
            "discount_percentage": float(product.discount_percentage),
            "id":product.id
        }
        products_data.append(product_data)

    products_json = json.dumps(products_data)

    context = {
        'products_json': products_json,
        'total_cost':total_cost,
        'count':count,
        'category':Category.objects.all()
    }
    return render(request, 'stock.html', context)



from django.core.files.storage import FileSystemStorage
@login_required
def updatestock(request):
    if request.method == 'POST':
        productId = request.POST.get('productId')
        productName = request.POST.get('productName')
        productDescription = request.POST.get('productDescription')
        costPrice = request.POST.get('costPrice')
        sellPrice = request.POST.get('salePrice')
        manufacturer = request.POST.get('manufacturer')
        quantityInStock = request.POST.get('quantityInStock')
        packingValue = request.POST.get('packingValue')
        measurementUnit = request.POST.get('measurementUnit')
        discountPercentage = request.POST.get('discountPercentage')
        productImage = request.FILES.get('productImage')

        pro = Productx.objects.get(id=productId)
        pro.name = productName
        pro.description = productDescription
        pro.cost_price = costPrice
        pro.sale_price = sellPrice
        pro.manufacturer = manufacturer
        pro.quantity_in_stock = quantityInStock
        pro.packing_value = packingValue
        pro.measurement_unit = measurementUnit
        pro.discount_percentage = discountPercentage

        if productImage:
            pro.product_image =productImage

        pro.save()
        return redirect('inventory_audit')

    return redirect('inventory_audit')


@login_required  # تأكد من أن المستخدم قد سجل الدخول
def purchase_goods(request):
    # الحصول على جميع المنتجات من قاعدة البيانات
    products = Product.objects.all()
    # تحويل البيانات إلى صيغة JSON لاستخدامها في الواجهة الأمامية
    products_json = serializers.serialize('json', products)
    try:
        # محاولة الحصول على رصيد آخر صندوق النقدية
        balancr = Cashbox.objects.all().last().balance
    except:
        # إذا لم يكن هناك رصيد، استخدم القيمة 0
        balancr = 0
    # عرض القالب مع البيانات المحتسبة
    return render(request, 'peypro.html',
                  {'products_json': products_json, 'balancr': balancr, 'suppliers': Supplier.objects.all()})


@login_required
def add_purchase(request):
    if request.method == 'POST':  # التحقق من أن الطلب هو POST
        # استلام البيانات من الطلب
        supplierName = request.POST.get('supplierName')
        product_name = request.POST.get('productName')
        quantity = request.POST.get('quantity')
        cost_price = request.POST.get('costPrice')
        total_cost = request.POST.get('totalCost')
        pakage = request.POST.get('pakage')
        note = request.POST.get('note')
        invoice_file = request.FILES.get('invoiceFile')

        # محاولة العثور على المنتج في قاعدة البيانات وتحديث الكمية المخزنة
        try:
            product = Product.objects.get(name=product_name.strip())
            quantity_to_add = Decimal(quantity)
            product.quantity_in_stock += quantity_to_add
            product.save()
        # إذا لم يتم العثور على المنتج، قم بإنشاء واحد جديد
        except:
            Product.objects.create(
                name=product_name,
                pakge=pakage,
                quantity_in_stock=quantity,
                cost=cost_price,
                cost_price=0,
            )

        # إنشاء تنسيق HTML للملاحظة
        from django.utils.html import format_html
        purchase_date = timezone.now()
        note_html = format_html(
            "<p>تم شراء بضاعة بمبلغ: <strong>{}<strong><br>"
            "اسم البضاعة: <strong>{}<strong><br>"
            "اسم المورد: <strong>{}<strong><br>"
            "الكمية: <strong>{}<strong><br>"
            "التكلفة للقطعه: <strong>{}<strong><br>"
            "التاريخ: <strong>{}<strong></p>",
            total_cost,
            product_name,
            supplierName,
            quantity,
            cost_price,
            purchase_date,
        )

        # الحصول على آخر رصيد في صندوق النقدية
        try:
            last = Cashbox.objects.all().last().balance
        except:
            last = 0

        # إنشاء سجل في صندوق النقدية لهذه العملية
        Cashbox.objects.create(
            description='شراء بضاعه',
            notes=note_html,
            amount=Decimal(total_cost),
            befor=last,
            balance=last - Decimal(total_cost)
        )

        # إنشاء وحفظ سجل شراء جديد
        purchase = Purchase(
            supplier=supplierName,
            product_name=product_name,
            quantity=quantity,
            cost_price=cost_price,
            total_cost=total_cost,
            note=note,
            invoice=invoice_file,
            date=timezone.now()  # أو يمكنك استخدام auto_now_add=True في نموذجك
        )
        purchase.save()

        # إعادة توجيه المستخدم إلى صفحة المراجعة الجردية
        return redirect('inventory_audit')


@login_required
def purchase_list(request):
    # الحصول على جميع سجلات الشراء وترتيبها حسب التاريخ
    purchase = Purchase.objects.all().order_by('date')
    context = {
        'purchase': purchase
    }
    # عرض صفحة قائمة المشتريات
    return render(request, 'purchase_list.html', context)


@login_required
def ExpenseViews(request):
    import datetime
    # جلب معلمات البحث من الطلب
    search_query = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # تحديد الشهر الحالي كنطاق تاريخ افتراضي
    if not date_from and not date_to:
        today = datetime.date.today()
        date_from = today.replace(day=1)
        next_month = today.replace(day=28) + datetime.timedelta(days=4)
        date_to = next_month - datetime.timedelta(days=next_month.day)

    # الحصول على سجلات النفقات في النطاق الزمني المحدد
    Expenseop = Expense.objects.filter(date__range=[date_from, date_to])

    # الفلترة بناءً على النص المدخل
    if search_query:
        Expenseop = Expenseop.filter(
            Q(spent_by__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    # حساب مجموع النفقات
    total_expenses = Expenseop.filter(spent=True).aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'Expense': Expenseop.order_by('-date'),
        'total_expenses': total_expenses
    }

    # عرض صفحة قائمة النفقات
    return render(request, 'Expense.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':  # التحقق من أن الطلب هو POST
        # استلام البيانات من الطلب
        category = request.POST.get('category')  # الفئة
        amount = request.POST.get('amount')  # المبلغ
        notes = request.POST.get('notes')  # الملاحظات
        # الحصول على ملف الفاتورة إذا كان موجودًا
        invoice_file = request.FILES.get('invoice_file') if 'invoice_file' in request.FILES else None

        # إنشاء كائن جديد من نموذج Expense
        new_expense = Expense(
            category=category,
            amount=amount,
            notes=notes,
            invoice_file=invoice_file,
            spent_by=request.user.username,  # اسم المستخدم الذي أضاف النفقة
            spent=False,  # حالة النفقة (غير مدفوعة بعد)
            description='مصروفات'
        )

        # حفظ الكائن الجديد في قاعدة البيانات
        new_expense.save()
        # إعادة توجيه المستخدم إلى صفحة النفقات
        return redirect('Expense')


@login_required
def editexpense(request, id):
    # الحصول على النفقة من قاعدة البيانات باستخدام الهوية
    Expenseed = Expense.objects.get(id=id)
    # تحديث حالة النفقة إلى "مدفوعة"
    Expenseed.spent = True
    Expenseed.save()

    # الحصول على آخر رصيد في صندوق النقدية
    try:
        last = Cashbox.objects.last().balance
    except:
        last = 0
    # إنشاء سجل في صندوق النقدية لهذه النفقة
    Cashbox.objects.create(
        description='مصروفات',
        amount=Expenseed.amount,
        befor=last,
        balance=last - Expenseed.amount,
        notes=Expenseed.notes
    )
    # إعادة توجيه المستخدم إلى صفحة النفقات
    return redirect('Expense')


@login_required
def delete_expense(request, id):
    # حذف النفقة من قاعدة البيانات
    Expense.objects.get(id=id).delete()
    # إعادة توجيه المستخدم إلى صفحة النفقات
    return redirect('Expense')


@login_required
def traders_list(request):
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    agents = Agent.objects.all()

    if search_query:
        agents = agents.filter(name__icontains=search_query)

    # إضافة مجموع المشتريات والمدفوعات لكل وكيل
    for agent in agents:
        agent.total_purchases = AgentTransaction3.objects.filter(
            agent=agent, transaction_type='purchase'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        agent.total_payments = AgentTransaction3.objects.filter(
            agent=agent, transaction_type='payment'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    context = {
        'agents': agents,
        'search_query': search_query,
    }

    return render(request, 'traders_list.html', context)


@login_required
def add_agent(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        adress = request.POST.get('adress')
        new_agent = Agent.objects.create(name=name, phone=phone, address=adress)
        new_agent.save()

    return redirect('traders_list')


@login_required
def edit_agent(request):
    if request.method == 'POST':
        # الحصول على ID الوكيل من النموذج
        agent_id = request.POST.get('id')
        agent = get_object_or_404(Agent, id=agent_id)

        # الحصول على البيانات الجديدة من النموذج
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        adress = request.POST.get('adress')

        # تحديث بيانات الوكيل
        agent.name = name
        agent.phone = phone
        agent.address = adress
        agent.save()

        return redirect('traders_list')


@login_required
def delete_agent(request):
    agent_id = request.GET.get('id')
    agent = get_object_or_404(Agent, id=agent_id)
    agent.delete()

    return redirect('traders_list')


@login_required
def invoice_listFilter(request, serch):
    # استلام معلمات البحث من الطلب
    search_query = serch
    min_date_str = request.GET.get('min_date', '')
    max_date_str = request.GET.get('max_date', '')

    # بداية الاستعلام الأساسي
    invoices_query = Invoice.objects.all()

    # إذا كان هناك استعلام بحث، قم بتصفية النتائج
    if search_query:
        invoices_query = invoices_query.filter(
            Q(invoice_number__icontains=search_query) |
            Q(agent__name__icontains=search_query)
        )

    # إذا تم تحديد تاريخ البداية، قم بتصفية النتائج لتشمل الفواتير بعد هذا التاريخ
    if min_date_str:
        min_date = datetime.datetime.strptime(min_date_str, '%Y-%m-%d').date()
        invoices_query = invoices_query.filter(date__gte=min_date)

    # إذا تم تحديد تاريخ النهاية، قم بتصفية النتائج لتشمل الفواتير قبل هذا التاريخ
    if max_date_str:
        max_date = datetime.datetime.strptime(max_date_str, '%Y-%m-%d').date()
        invoices_query = invoices_query.filter(date__lte=max_date)

    # بناء قائمة الفواتير مع البيانات المطلوبة
    invoices_list = []
    for invoice in invoices_query.all().order_by('-date'):
        count = InvoiceItem.objects.filter(invoice=invoice).count()
        invoices_list.append({
            'invoice_number': invoice.invoice_number,
            'agent': invoice.agent.name,
            'date': invoice.date.strftime('%Y-%m-%d %H:%M'),  # تنسيق التاريخ
            'total': invoice.total,
            'balncagentafter': invoice.balncagentafter,
            'balncagentlast': invoice.balncagentlast,
            'admin': invoice.admin

        })
    total_sales = invoices_query.aggregate(Sum('total'))['total__sum'] or 0
    return render(request, 'list_invoices.html',
                  {'invoices': invoices_list, 'search_query': search_query, 'min_date_str': min_date_str,
                   'max_date_str': max_date_str, 'total_sales': total_sales, })


def settings(rquest):
    return render(rquest, 'settings.html', {'company_info': CompanyInfo.objects.last()})


@login_required
def update_company_info(request):
    company_info = CompanyInfo.objects.last()
    if request.method == 'POST':
        company_name = request.POST.get('name')
        company_branch = request.POST.get('branch')
        company_address = request.POST.get('address')
        company_email = request.POST.get('email')
        company_phone = request.POST.get('ph')
        logo_file = request.POST.get('logo')
        print(logo_file)

        company_info.logo_url = logo_file
        company_info.name = company_name
        company_info.branch = company_branch
        company_info.address = company_address
        company_info.email = company_email
        company_info.phone = company_phone

        company_info.save()

    return redirect('settings')


def agent_account_statement(request, agent_id):
    # الحصول على تواريخ البداية والنهاية ورقم الفاتورة من معاملات GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    invoice_number = request.GET.get('invoice_number')  # الحصول على رقم الفاتورة

    # استرجاع معاملات الوكيل المحدد مع تطبيق الفلتر إذا توفرت التواريخ أو رقم الفاتورة
    agent_transactions = AgentTransaction3.objects.filter(agent_id=agent_id)

    if start_date:
        agent_transactions = agent_transactions.filter(date__gte=start_date)
    if end_date:
        agent_transactions = agent_transactions.filter(date__lte=end_date)
    if invoice_number:
        agent_transactions = agent_transactions.filter(invice_n=invoice_number)  # تطبيق الفلتر حسب رقم الفاتورة

    agent_transactions = agent_transactions.order_by('date', 'time')

    # إعداد السياق للقالب
    context = {
        'agent_transactions': agent_transactions,
        'agentid': agent_id,
        'agent': Agent.objects.get(id=agent_id)
    }
    # تقديم القالب مع السياق
    return render(request, 'agent_statment.html', context)


def status(request, agentid):
    # الحصول على تواريخ البداية والنهاية من معاملات GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # استرجاع معاملات الوكيل المحدد مع تطبيق الفلتر إذا توفرت التواريخ
    agent_transactions = AgentTransaction3.objects.filter(agent_id=agentid)

    if start_date:
        agent_transactions = agent_transactions.filter(date__gte=start_date)
    if end_date:
        agent_transactions = agent_transactions.filter(date__lte=end_date)

    agent_transactions = agent_transactions.order_by('-date', '-time')

    # إعداد السياق للقالب
    context = {
        'agent_transactions': agent_transactions,
        'agentid': agentid,
        'Company': CompanyInfo.objects.last(),
        'agent': Agent.objects.get(id=agentid),
        'start': start_date,
        'end': end_date
    }
    return render(request, 'status.html', context)


def creatpdffile2(request, agentid):
    # الحصول على تواريخ البداية والنهاية من معاملات GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # استرجاع معاملات الوكيل المحدد مع تطبيق الفلتر إذا توفرت التواريخ
    agent_transactions = AgentTransaction3.objects.filter(agent_id=agentid)
    if start_date:
        agent_transactions = agent_transactions.filter(date__gte=start_date)
    if end_date:
        agent_transactions = agent_transactions.filter(date__lte=end_date)

    agent_transactions = agent_transactions.order_by('date', 'time')

    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    last_transaction = agent_transactions.last()
    last_balance = last_transaction.balance if last_transaction else 0
    # إعداد السياق للقالب مع التاريخ والوقت
    context = {
        'agent_transactions': agent_transactions,
        'agentid': agentid,
        'Company': CompanyInfo.objects.last(),
        'agent': Agent.objects.get(id=agentid),
        'start': start_date,
        'end': end_date,
        'today_date': current_date,
        'current_time': current_time,
        'admin': request.user.first_name,
        'last': last_balance
    }
    # تحويل القالب إلى سلسلة HTML
    html_string = render_to_string('status.html', context)

    # إنشاء ملف PDF في الذاكرة
    pdf_file_io = BytesIO()
    # HTML(string=html_string).write_pdf(target=pdf_file_io)
    HTML(string=html_string).write_pdf(target=pdf_file_io, size='A4')
    pdf_file_io.seek(0)

    # إنشاء استجابة HTTP تحمل محتوى PDF
    response = HttpResponse(pdf_file_io.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agent_statement.pdf"'

    return response


def creatpdffile3(context):
    html_string = render_to_string('mt.html', context)

    pdf_file_io = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file_io)
    pdf_file_io.seek(0)
    return pdf_file_io


def deposetagent(request):
    id = request.GET.get('id')
    amount = request.GET.get('amount')
    note = request.GET.get('note')
    agent = Agent.objects.get(id=id)
    payment_transaction = AgentTransaction3(
        agent=agent,
        amount=Decimal(amount),
        balance_last=agent.get_balance(),
        balance=agent.get_balance() + Decimal(amount),
        transaction_type='payment',
        note=note

    )
    payment_transaction.save()
    from datetime import datetime
    # إعداد السياق للقالب
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')  # التنسيق: سنة-شهر-يوم
    current_time = now.strftime('%H:%M:%S')  # التنسيق: ساعة:دقيقة:ثانية
    context = {
        'payment_transaction': payment_transaction,
        'Company': CompanyInfo.objects.last(),
        'today_date': current_date,
        'current_time': current_time,
        'admin': request.user.first_name
    }

    pdf_file_io = creatpdffile3(context)

    # حفظ ملف PDF في الحركة
    pdf_file_name = f"{payment_transaction.invice_n}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
    payment_transaction.receipt.save(pdf_file_name, ContentFile(pdf_file_io.read()))
    payment_transaction.save()
    try:
        last = Cashbox.objects.last().balance
    except:
        last = 0
    Cashbox.objects.create(
        amount=int(amount),
        description='تسديد',
        befor=last,
        balance=int(last) + int(amount),
        notes=f"""
        <div style="text-align: center; border: 1px solid #47933a; padding: 5px; margin: 10px;">
            <h5 style="border-bottom: 1px solid #ccc;">وصل إيداع</h5>
            <div style="margin: 10px 0; margin-top: 10px">
                <strong>اسم الوكيل/التاجر:</strong> <span>{agent.name}</span>
            </div>
            <div style="margin: 10px 0;">
                <strong>المبلغ المودع:</strong> <span>{amount} د.ع </span>
            </div>
            <div style="margin: 10px 0;">
                <strong>الرصيد السابق للشركه:</strong> <span>{last} د.ع </span>
            </div>
            <div style="margin: 10px 0;">
                <strong>الرصيد الحالي للشركه:</strong> <span>{int(last) + int(amount)} د.ع </span>
            </div>
             <div style="margin: 10px 0;">
                <strong>رقم الأيصال:</strong> <span>{payment_transaction.invice_n}  </span>
            </div>
               <div style="margin: 10px 0;">
                <strong>اصبح رصيد التاجر بعد هذا الأيداع :</strong> <span>{agent.get_balance()}  </span> د.ع
            </div>
            <div style="margin: 10px 0; direction: rtl">
                <strong>الموظف:</strong> <span>{request.user.username}  </span>
            </div>
        </div>
        """

    )

    return redirect('traders_list')


def ArchiveList(request, id):
    agent = Agent.objects.get(id=id)
    archives = agent.archives.all()

    for archive in archives:
        archive.size_kb = round(archive.file.size / 1024)  # تحويل الحجم من بايت إلى كيلوبايت

    return render(request, 'Archive.html', {'agent': agent, 'archives': archives})


def upload_archive(request):
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        title = request.POST.get('title')
        file = request.FILES.get('file')
        agent = Agent.objects.get(id=agent_id)
        Archive.objects.create(agent=agent, title=title, file=file)
        return redirect(reverse('ArchiveList', kwargs={'id': agent_id}))


def deletArchive(request, id, agent_id):
    Archive.objects.get(id=id).delete()
    return redirect(reverse('ArchiveList', kwargs={'id': agent_id}))


def suppliers_list(request):
    suppliers = Supplier.objects.all()

    for supplier in suppliers:
        total_cost = Purchase.objects.filter(supplier=supplier.company_name).aggregate(Sum('total_cost'))[
            'total_cost__sum']
        supplier.total_cost = total_cost if total_cost is not None else 0

    context = {
        'suppliers': suppliers
    }

    return render(request, 'suppliers_list.html', context)


@require_http_methods(['POST', 'GET'])
def add_supplier(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email', '')  # يتم استخدام قيمة افتراضية إذا لم يتم تقديم البريد الإلكتروني
        website = request.POST.get('website', '')
        notes = request.POST.get('notes', '')

        # إنشاء وحفظ مثيل جديد من النموذج
        Supplier.objects.create(
            company_name=company_name,
            address=address,
            phone_number=phone_number,
            email=email,
            website=website,
            notes=notes
        )

        return redirect('suppliers_list')


# في views.py
def delete_supplier(request, supplier_id):
    # تنفيذ عملية الحذف
    supplier = Supplier.objects.get(id=supplier_id)
    supplier.delete()
    return redirect('suppliers_list')  # إعادة توجيه بعد الحذف


#######################################################

from datetime import datetime
from pro1.tests import bar_sales_monthly, barsals, bar_net_profits, bar_net_profits_monthly,get_annual_sold_quantities,get_monthly_sold_quantities


def sales_reports(request):
    barsals()
    bar_sales_monthly()

    return render(request, 'sales_reports.html', )


def profits_reports(request):
    bar_net_profits()
    bar_net_profits_monthly()

    return render(request, 'profitrepot.html', )


def sold_quantities(requst):

    return render(requst,'sold_quantities.html',{
        'get_annual_sold_quantities':get_annual_sold_quantities(),
        'get_monthly_sold_quantities':get_monthly_sold_quantities()
    })
from django.http import JsonResponse
from .models import Productx,Category
def products_by_category(request):
    products = Productx.objects.all()
    categories = Category.objects.all()

    return render(request, 'cart.html', {'products': products,'categories':categories})


######################################################
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # إزالة هذا السطر إذا كان لديك CSRF token
@require_GET
def handle_cart_data(request):
    try:
        products_param = request.GET.get('products')
        products_data = json.loads(products_param)

        invoice_items = []  # قائمة لتخزين بيانات بنود الفاتورة
        total_invoice_amount = 0  # متغير لتخزين القيمة الكلية للفاتورة
        for product_id, details in products_data.items():
            quantity = details.get('quantity')
            product = Productx.objects.get(id=product_id)

            sale_total = int(quantity) * float(product.sale_price_after_discount)  # تحويل إلى float
            sale_price_per_item = float(product.sale_price)  # تحويل إلى float
            sale_price_per_item_after = float(product.sale_price_after_discount)
            cost_price = float(product.cost_price)  # تحويل إلى float
            quantity_in_stock = product.quantity_in_stock

            total_invoice_amount += sale_total

            invoice_items.append({
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'sale_total': sale_total,
                'sale_price_per_item': sale_price_per_item,
                'cost_price': cost_price,
                'quantity_in_stock': quantity_in_stock,
                'img_product':product.product_image.url,
                'discount':float(product.discount_percentage),
                'packing_value':float(product.packing_value) * quantity,
                'measurement_unit':product.measurement_unit,
                'sale_price_per_item_after':sale_price_per_item_after
            })
        print(invoice_items)
        return render(request, 'list_add_products.html', {
            'invoice_items': invoice_items,
            'total_invoice_amount': total_invoice_amount
        })
    except Exception as e:
        print('Error:', e)




