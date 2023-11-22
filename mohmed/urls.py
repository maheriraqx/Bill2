"""
URL configuration for mohmed project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pro1 import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin2/', admin.site.urls),
                  path('login/', views.login_view, name='login'),
                  path('', views.dashb, name='dashb'),
                  path('create_invoice', views.create_invoice_view, name='create_invoice'),
                  path('getbils', views.getbils, name='getbils'),
                  path('invoice_list', views.invoice_list, name='invoice_list'),
                  path('invoiceprint/<str:number>', views.invoiceprint, name='invoiceprint'),
                  path('rpeset/<str:number>', views.rpeset, name='rpeset'),
                  path('inviocefile/<str:number>', views.inviocefile, name='inviocefile'),
                  # path('deletinvoice/<str:number>',views.deletinvoice,name='deletinvoice'),
                  path('cashbox_statement', views.cashbox_statement, name='cashbox_statement'),
                  path('cashbox_deposit', views.cashbox_deposit, name='cashbox_deposit'),
                  path('cashbox_withdraw', views.cashbox_withdraw, name='cashbox_withdraw'),
                  path('cashbox_deposit_action', views.cashbox_deposit_action, name='cashbox_deposit_action'),
                  path('cashbox_withdraw_action', views.cashbox_withdraw_action, name='cashbox_withdraw_action'),
                  path('payment', views.payment, name='payment'),
                  path('detils/<str:number>', views.detils, name='detils'),
                  path('inventory_audit', views.inventory_audit, name='inventory_audit'),
                  path('updatestock', views.updatestock, name='updatestock'),
                  path('purchase_goods', views.purchase_goods, name='purchase_goods'),
                  path('add_purchase', views.add_purchase, name='add_purchase'),
                  path('purchase_list', views.purchase_list, name='purchase_list'),
                  path('Expense', views.ExpenseViews, name='Expense'),
                  path('add_expense/', views.add_expense, name='add_expense'),
                  path('editexpense/<str:id>', views.editexpense, name='editexpense'),
                  path('delete_expense/<str:id>', views.delete_expense, name='delete_expense'),
                  path('traders_list', views.traders_list, name='traders_list'),
                  path('add-agent/', views.add_agent, name='add_agent'),
                  path('edit-agent/', views.edit_agent, name='edit_agent'),
                  path('delete-agent/', views.delete_agent, name='delete_agent'),
                  path('invoice_listFilter/<str:serch>', views.invoice_listFilter, name='invoice_listFilter'),
                  path('settings', views.settings, name='settings'),
                  path('update_company_info', views.update_company_info, name='update_company_info'),
                  path('agent_account_statement/<str:agent_id>', views.agent_account_statement,
                       name='agent_account_statement'),
                  path('status/<str:agentid>', views.creatpdffile2, name='status'),
                  path('deposetagent', views.deposetagent, name='deposetagent'),
                  path('ArchiveList/<str:id>', views.ArchiveList, name='ArchiveList'),
                  path('upload_archive/', views.upload_archive, name='upload_archive'),
                  path('deletArchive/<str:id>/<str:agent_id>', views.deletArchive, name='deletArchive'),
                  path('suppliers_list', views.suppliers_list, name='suppliers_list'),
                  path('add_supplier', views.add_supplier, name='add_supplier'),
                  path('delete_supplier/<str:supplier_id>/', views.delete_supplier, name='delete_supplier'),
                  path('sales_reports', views.sales_reports, name='sales_reports'),
                  path('profits_reports', views.profits_reports, name='profits_reports'),
                  path('sold_quantities',views.sold_quantities,name='sold_quantities'),
                  path('products_by_category', views.products_by_category, name='products_by_category'),
                  path('itemsfromuser', views.handle_cart_data, name='itemsfromuser'),
                  path('logout/', views.logout_view, name='logout'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
