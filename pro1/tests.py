from .models import Invoice,InvoiceItem,Cashbox,Expense,AgentTransaction3,Agent,Product
from django.utils import timezone
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
import calendar



from django.db.models import Sum, Avg, Count,F


class ReportGenerator:
    @staticmethod
    def generate_profit_loss_report(start_date, end_date):
        # حساب الإيرادات (مجموع الفواتير)
        total_revenue = Invoice.objects.filter(date__range=[start_date, end_date]).aggregate(Sum('total'))[
                            'total__sum'] or 0

        # حساب تكلفة البضائع المباعة (COGS) من حقل costperone_price الموجود في InvoiceItem
        cogs = InvoiceItem.objects.filter(invoice__date__range=[start_date, end_date]).annotate(
            item_cost=F('costperone_price') * F('quantity')
        ).aggregate(total_cogs=Sum('item_cost'))['total_cogs'] or 0

        # حساب المصروفات الكلية
        total_expenses = \
        Cashbox.objects.filter(date__range=[start_date, end_date], description__icontains='مصروفات').aggregate(
            Sum('amount'))['amount__sum'] or 0

        # حساب الأرباح الصافية
        net_profit = total_revenue - cogs - total_expenses

        return {
            'total_revenue': total_revenue,
            'cogs': cogs,
            'total_expenses': total_expenses,
            'net_profit': net_profit
        }

    @staticmethod
    def generate_sales_report(start_date, end_date):
        # تفاصيل المبيعات خلال فترة محددة مع الأرباح لكل قطعة معتمدة على التكلفة المخزنة في InvoiceItem
        sales_details = InvoiceItem.objects.filter(invoice__date__range=[start_date, end_date]).annotate(
            total_quantity_sold=Sum('quantity'),
            total_sales=Sum(F('selling_price') * F('quantity')),
            cogs=Sum(F('costperone_price') * F('quantity')),
            profit_per_item=F('selling_price') - F('costperone_price'),
            total_profit=Sum((F('selling_price') - F('costperone_price')) * F('quantity'))
        ).values(
            'product__name',
            'total_quantity_sold',
            'total_sales',
            'cogs',
            'profit_per_item',
            'total_profit'
        ).order_by('-total_sales')

        return list(sales_details)

# يمكنك إضافة المزيد من الوظائف الثابتة لتقارير أخرى مثل تقارير المخزون، المصروفات، الديون، وغيرها.

# استخدام الكلاس
report_data = ReportGenerator.generate_profit_loss_report('2021-01-01', '2023-12-31')
sales_data = ReportGenerator.generate_sales_report('2021-01-01', '2023-12-31')
#print(report_data)
#print(sales_data)





def get_daily_expenses_for_current_month():
    current_year = timezone.now().year
    current_month = timezone.now().month
    expenses = Expense.objects.filter(
        date__year=current_year,
        date__month=current_month,
        spent=True
    ).annotate(day=TruncDay('date')).values('day').annotate(total=Sum('amount')).order_by('day')
    return list(expenses)

def get_monthly_expenses_for_current_year():
    current_year = timezone.now().year
    expenses = Expense.objects.filter(
        date__year=current_year,
        spent=True
    ).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    return list(expenses)

# يمكن تطبيق نفس المنطق للأرباح، المبيعات والمشتريات باستخدام الوظائف المشابهة.

def get_todays_sales():
    today = timezone.now().date()
    todays_sales = Invoice.objects.filter(date__date=today).aggregate(total_sales=Sum('total'))['total_sales']
    return todays_sales or 0

def get_current_month_sales():
    current_month = timezone.now().month
    current_year = timezone.now().year
    current_month_sales = Invoice.objects.filter(date__year=current_year, date__month=current_month).aggregate(total_sales=Sum('total'))['total_sales']
    return current_month_sales or 0

def get_current_year_sales():
    current_year = timezone.now().year
    current_year_sales = Invoice.objects.filter(date__year=current_year).aggregate(total_sales=Sum('total'))['total_sales']
    return current_year_sales or 0

#print(get_daily_expenses_for_current_month())
#print(get_monthly_expenses_for_current_year())
#print(get_current_month_sales())


###############################################

def get_daily_sales_for_current_month():
    current_year = timezone.now().year
    current_month = timezone.now().month
    num_days = calendar.monthrange(current_year, current_month)[1]
    days = [timezone.datetime(current_year, current_month, day) for day in range(1, num_days + 1)]

    sales = Invoice.objects.filter(
        date__year=current_year,
        date__month=current_month
    ).annotate(day=TruncDay('date')).values('day').annotate(total=Sum('total'))

    sales_dict = {sale['day'].date(): sale['total'] for sale in sales}

    return [{'day': day, 'total': sales_dict.get(day.date(), 0)} for day in days]


#print(get_daily_sales_for_current_month())



# بيانات المبيعات اليومية


##################################################################
#




def get_monthly_sales_for_current_year():
    current_year = timezone.now().year
    months = [timezone.datetime(current_year, month, 1) for month in range(1, 13)]

    sales = Invoice.objects.filter(
        date__year=current_year
    ).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('total'))

    sales_dict = {sale['month'].date(): sale['total'] for sale in sales}

    return [{'month': month, 'total': sales_dict.get(month.date(), 0)} for month in months]
def barsals():
    sales_data = get_daily_sales_for_current_month()

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(sales_data)
    df['day'] = pd.to_datetime(df['day'])
    df['total'] = df['total'].astype(float)

    # تعيين اليوم كمؤشر (index)
    df.set_index('day', inplace=True)

    # تحديد ألوان الأعمدة
    colors = ['green' if x > 250000 else 'orange' if x > 100000 else 'red' if x == 0 else 'orangered' for x in df['total']]

    # إنشاء الرسم البياني
    plt.figure(figsize=(35, 10))
    bars = plt.bar(df.index.strftime('%d'), df['total'], color=colors, width=0.3)

    # تعيين العنوان وتسميات المحاور
    plt.title(f'Daily Sales for {df.index[0].strftime("%m/%Y")}', fontsize=30)
    plt.xlabel('Day', fontsize=30, fontweight='bold')
    plt.ylabel('Sales', fontsize=30, fontweight='bold')

    # تنسيق المحاور
    plt.xticks(rotation=45, fontsize=24, weight='bold') # تكبير وتعريض الخط لمحور X
    plt.yticks(rotation=45, fontsize=24, weight='bold') # تكبير وتعريض الخط لمحور Y
    today = datetime.now().strftime('%d')

    # إضافة خط عمودي لتمييز اليوم الحالي
    plt.annotate('', xy=(today, 0), xytext=(today, 10000,),
                 arrowprops=dict(facecolor='red', shrink=0.4))

    # تعيين الحد الأقصى للمحور Y
    max_sales = df['total'].max()
    plt.ylim(0, max_sales * 2)

    # إضافة القيم فوق كل عمود بخط عريض وحجم أكبر
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max_sales * 0.05), round(yval),
                 va='bottom', ha='center', fontsize=20,rotation=2,weight='bold')

    # إضافة شبكة
    plt.grid(True)

    # حفظ الرسم البياني كصورة
    plt.tight_layout()
    plt.savefig('static/reports/sales_chart.png')





#barsals()

def bar_sales_monthly():
    sales_data = get_monthly_sales_for_current_year()

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(sales_data)
    df['month'] = pd.to_datetime(df['month'])
    df['total'] = df['total'].astype(float)

    # تعيين الشهر كمؤشر (index)
    df.set_index('month', inplace=True)

    # تحديد لون كل عمود بناءً على القيمة
    colors = ['green' if x > 1000000 else 'orange' if x > 500000 else '#FF8C00' for x in df['total']]

    # إنشاء الرسم البياني
    plt.figure(figsize=(30, 6))
    bars = plt.bar(df.index.strftime('%m'), df['total'], color=colors, width=0.5)

    # تعيين العنوان وتسميات المحاور
    plt.title(f'Monthly Sales for {df.index[0].year}', fontsize=25)
    plt.xlabel('Month', fontsize=25)
    plt.ylabel('Sales', fontsize=25)

    # تنسيق المحاور
    plt.xticks(rotation=45,fontsize=22,weight='bold')
    plt.yticks(rotation=45,fontsize=22,weight='bold')
    current_month = datetime.now().strftime('%m')
    # إضافة خط عمودي لتمييز الشهر الحالي
    plt.annotate('', xy=(current_month, 0), xytext=(current_month, 10000),
                 arrowprops=dict(facecolor='red', shrink=0.02))

    # تعيين الحد الأقصى للمحور Y
    max_sales = df['total'].max()
    plt.ylim(0, max_sales * 2)  # ضعف أعلى مبيعات كحد أقصى

    # إضافة القيم فوق كل عمود
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval), va='bottom', ha='center',fontsize=30)

    # إضافة شبكة
    plt.grid(True)

    # حفظ الرسم البياني كصورة
    plt.tight_layout()
    plt.savefig('static/reports/monthly_sales_chart.png')


#bar_sales_monthly()
from django.db.models import F, Sum

def get_daily_net_profits_for_current_month():
    current_year = timezone.now().year
    current_month = timezone.now().month
    num_days = calendar.monthrange(current_year, current_month)[1]
    days = [timezone.datetime(current_year, current_month, day) for day in range(1, num_days + 1)]

    # جلب جميع عناصر الفواتير للشهر الحالي
    invoice_items = InvoiceItem.objects.filter(
        invoice__date__year=current_year,
        invoice__date__month=current_month
    ).annotate(
        day=TruncDay('invoice__date'),
        profit_per_item=F('quantity_after_discount') - F('costperone_price'),
        total_profit_per_item=F('profit_per_item') * F('quantity')
    ).values('day').annotate(total_profit=Sum('total_profit_per_item'))

    # جلب المصروفات اليومية من الصندوق
    daily_expenses = Cashbox.objects.filter(
        date__year=current_year,
        date__month=current_month,
        # هنا يمكن تطبيق فلتر لتحديد المصروفات بناءً على الوصف أو حقل آخر
        description__icontains="مصروفات"  # مثال لتصفية بناءً على الوصف
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(total_expense=Sum('amount'))

    expenses_dict = {expense['day'].date(): expense['total_expense'] for expense in daily_expenses}
    profits_dict = {item['day'].date(): item['total_profit'] for item in invoice_items}

    # حساب الأرباح الصافية
    net_profits = []
    for day in days:
        day_date = day.date()
        profit = profits_dict.get(day_date, 0)
        expense = expenses_dict.get(day_date, 0)
        net_profit = profit - expense
        net_profits.append({'day': day_date, 'net_profit': net_profit})

    return net_profits




def get_monthly_net_profits_for_current_year():
    current_year = timezone.now().year

    # جلب جميع عناصر الفواتير للسنة الحالية
    invoice_items = InvoiceItem.objects.filter(
        invoice__date__year=current_year
    ).annotate(
        month=TruncMonth('invoice__date'),
        profit_per_item=F('quantity_after_discount') - F('costperone_price'),
        total_profit_per_item=F('profit_per_item') * F('quantity')
    ).values('month').annotate(total_profit=Sum('total_profit_per_item'))

    # جلب المصروفات الشهرية من الصندوق
    monthly_expenses = Cashbox.objects.filter(
        date__year=current_year,
        description__icontains="مصروفات"
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(total_expense=Sum('amount'))

    # تحويل تواريخ الشهور إلى سلاسل نصية
    expenses_dict = {expense['month'].strftime('%Y-%m'): expense['total_expense'] for expense in monthly_expenses}
    profits_dict = {item['month'].strftime('%Y-%m'): item['total_profit'] for item in invoice_items}

    # حساب الأرباح الصافية لكل شهر
    net_profits = []
    for month in range(1, 13):  # لكل شهر في السنة
        month_str = f'{current_year}-{month:02d}'
        profit = profits_dict.get(month_str, 0)
        expense = expenses_dict.get(month_str, 0)
        net_profit = profit - expense
        net_profits.append({'month': month_str, 'net_profit': net_profit})

    return net_profits



#print(get_daily_net_profits_for_current_month())
#print(get_monthly_net_profits_for_current_year())

def bar_net_profits():
    import datetime
    # البيانات المتوفرة لديك
    net_profit_data = get_daily_net_profits_for_current_month()

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(net_profit_data)
    df['day'] = pd.to_datetime(df['day'])
    df['net_profit'] = df['net_profit'].astype(float)

    # تعيين اليوم كمؤشر (index)
    df.set_index('day', inplace=True)

    # تحديد ألوان الأعمدة بناءً على قيمة الأرباح
    colors = ['green' if x > 200000 else 'orange' if x > 50000 else 'red' if x == 0 else 'orangered' for x in df['net_profit']]

    # إنشاء الرسم البياني
    plt.figure(figsize=(35, 10))
    bars = plt.bar(df.index.strftime('%d'), df['net_profit'], color=colors, width=0.3)

    # تعيين العنوان وتسميات المحاور
    plt.title(f'Daily Net Profits for {df.index[0].strftime("%m/%Y")}', fontsize=30)
    plt.xlabel('Day', fontsize=30, fontweight='bold')
    plt.ylabel('Net Profit', fontsize=30, fontweight='bold')

    # تنسيق المحاور
    plt.xticks(rotation=45, fontsize=24, weight='bold')
    plt.yticks(rotation=45, fontsize=24, weight='bold')
    today = datetime.datetime.now().strftime('%d')

    # إضافة خط عمودي لتمييز اليوم الحالي
    plt.axvline(today, color='blue', linestyle='--', linewidth=2)

    # تعيين الحد الأقصى للمحور Y
    max_profit = df['net_profit'].max()
    plt.ylim(0, max_profit * 1.2)

    # إضافة القيم فوق كل عمود بخط عريض وحجم أكبر
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + (max_profit * 0.05), round(yval),
                 va='bottom', ha='center', fontsize=20, rotation=2, weight='bold')

    # إضافة شبكة
    plt.grid(True)

    # حفظ الرسم البياني كصورة
    plt.tight_layout()
    plt.savefig('static/reports/net_profits_chart.png')

# يمكنك الآن استدعاء الوظيفة لإنشاء الرسم البياني
#bar_net_profits()

def bar_net_profits_monthly():
    import datetime
    # البيانات المتوفرة لديك
    net_profit_data = get_monthly_net_profits_for_current_year()

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(net_profit_data)
    df['month'] = pd.to_datetime(df['month'])
    df['net_profit'] = df['net_profit'].astype(float)

    # تعيين الشهر كمؤشر (index)
    df.set_index('month', inplace=True)

    # تحديد ألوان الأعمدة
    colors = ['green' if x > 1000000 else 'orange' if x > 500000 else '#FF8C00' for x in df['net_profit']]

    # إنشاء الرسم البياني
    plt.figure(figsize=(30, 6))
    bars = plt.bar(df.index.strftime('%m'), df['net_profit'], color=colors, width=0.5)

    # تعيين العنوان وتسميات المحاور
    plt.title(f'Monthly Net Profits for {df.index[0].year}', fontsize=25)
    plt.xlabel('Month', fontsize=25)
    plt.ylabel('Net Profit', fontsize=25)

    # تنسيق المحاور
    plt.xticks(rotation=45, fontsize=22, weight='bold')
    plt.yticks(rotation=45, fontsize=22, weight='bold')
    current_month = datetime.datetime.now().strftime('%m')
    # إضافة خط عمودي لتمييز الشهر الحالي
    plt.annotate('', xy=(current_month, 0), xytext=(current_month, 10000),
                 arrowprops=dict(facecolor='red', shrink=0.02))

    # تعيين الحد الأقصى للمحور Y
    max_net_profit = df['net_profit'].max()
    plt.ylim(0, max_net_profit * 2)

    # إضافة القيم فوق كل عمود
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval), va='bottom', ha='center', fontsize=20)

    # إضافة شبكة
    plt.grid(True)

    # حفظ الرسم البياني كصورة
    plt.tight_layout()
    plt.savefig('static/reports/monthly_net_profits_chart.png')

# يمكنك الآن استدعاء الوظيفة لإنشاء الرسم البياني
#bar_net_profits_monthly()

from django.db.models import Sum
from django.utils import timezone

def get_monthly_sold_quantities():
    current_month = timezone.now().month
    current_year = timezone.now().year
    products = Product.objects.all()
    monthly_sales = {}

    for product in products:
        sold_quantity = InvoiceItem.objects.filter(
            product=product,
            invoice__date__year=current_year,
            invoice__date__month=current_month
        ).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

        monthly_sales[product.name] = round(sold_quantity)

    return monthly_sales

print(get_monthly_sold_quantities())

def get_annual_sold_quantities():
    current_year = timezone.now().year
    products = Product.objects.all()
    annual_sales = {}

    for product in products:
        sold_quantity = InvoiceItem.objects.filter(
            product=product,
            invoice__date__year=current_year
        ).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

        annual_sales[product.name] = round(sold_quantity)

    return annual_sales
print(get_annual_sold_quantities())

def top_five_monthly_sold_products():
    current_month = timezone.now().month
    current_year = timezone.now().year

    # تجميع الكميات المباعة لكل منتج
    product_sales = InvoiceItem.objects.filter(
        invoice__date__year=current_year,
        invoice__date__month=current_month
    ).values('product__name').annotate(total_sold=Sum('quantity'))

    # فرز البيانات حسب الكمية المباعة واختيار أعلى خمسة
    top_five_products = product_sales.order_by('-total_sold')[:5]

    # تحويل النتيجة إلى قاموس
    monthly_sales = {item['product__name']: round(item['total_sold']) for item in top_five_products}

    return monthly_sales

def top_ten_monthly_most_profitable_products():
    current_month = timezone.now().month
    current_year = timezone.now().year

    # تجميع الأرباح لكل منتج
    product_profits = InvoiceItem.objects.filter(
        invoice__date__year=current_year,
        invoice__date__month=current_month
    ).values('product__name').annotate(
        total_profit=Sum(F('quantity_after_discount') * F('quantity') - F('costperone_price') * F('quantity'))
    )

    # فرز البيانات حسب الأرباح واختيار أعلى عشرة
    top_ten_products = product_profits.order_by('-total_profit')[:10]

    # تحويل النتيجة إلى قاموس
    monthly_profits = {item['product__name']: round(item['total_profit'], 2) for item in top_ten_products}
    monthly_profits = {item['product__name']: float(item['total_profit']) for item in top_ten_products}
    return monthly_profits

print(top_ten_monthly_most_profitable_products())