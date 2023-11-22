

# Register your models here.
from django.contrib import admin
from .models import Product, Agent, Invoice, InvoiceItem,Cashbox,InvoiceFile,Purchase,Expense,RecurringExpense,CompanyInfo,AgentTransaction3,Archive,Supplier,Category_pro,Productx,Category
from django.utils.timezone import now
admin.site.register(Product)
admin.site.register(Agent)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Purchase)
admin.site.register(Expense)
admin.site.register(RecurringExpense)
admin.site.register(AgentTransaction3)
admin.site.register(Supplier)
admin.site.register(Category_pro)
admin.site.register(Category)
admin.site.register(Productx)
class CashboxAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'balance', 'notes')  # الحقول التي تريد عرضها
    list_filter = ('date',)  # إضافة فلاتر حسب التاريخ
    search_fields = ('description', 'notes')  # إضافة خاصية البحث بالوصف والملاحظات

    def save_model(self, request, obj, form, change):
        # يمكنك تخصيص كيفية حفظ النموذج هنا
        if not obj.pk:  # إذا كان السجل جديدًا، لا يوجد له مفتاح أساسي بعد
            obj.date = now()  # تعيين التاريخ الحالي
        super().save_model(request, obj, form, change)

admin.site.register(Cashbox,CashboxAdmin)
@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'address', 'email', 'phone')


class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('agent', 'title', 'file', 'uploaded_at')



admin.site.register(Archive,ArchiveAdmin)