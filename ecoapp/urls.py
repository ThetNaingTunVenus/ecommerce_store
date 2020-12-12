from django.urls import path
from .views import *



app_name = 'ecoapp'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('allproducts/', AllProductsView.as_view(), name= 'allproducts'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name = 'productdetail'),

    path('addtocart/<int:pro_id>', AddToCartView.as_view(), name = 'addtocart'),
    path('mycart/', MyCartView.as_view(), name='mycart'),
    path('emptycart/', EmptyCartView.as_view(), name='emptycart'),
    path('managecart/<int:cp_id>/', ManageCartView.as_view(), name='managecart'),

    path('checkout/', CheckoutView.as_view(), name = 'checkout'),
    path('register/', CustomerRegistraionView.as_view(), name= 'customerregistration'),
    path('logout/', CustomerLogoutView.as_view(), name = 'logout'),
    path('login/', CustomerLoginView.as_view(), name = 'login'),
    path('search/', SearchView.as_view(), name = 'search'),
    path('cashier/search/', CashierItemsSearchView.as_view(), name='cashieritemsearch'),

    path('profile/', CustomerProfileView.as_view(), name = 'customerprofile'),
    path('profile/order-<int:pk>/', CustomerOrderDetailView.as_view(), name = 'customerorderdetail'),

    path('admin-login/', AdminLoginView.as_view(), name = 'adminlogin'),
    path('admin-home/', AdminHomeView.as_view(), name = 'adminhome'),
    path('admin-order/<int:pk>/', AdminOrderDetailView.as_view(), name = 'adminorderdetail'),
    path('admin-all-order/', AdminOrderListView.as_view(), name = 'adminorderlists'),
    path('admin-order-change-<int:pk>/', AdminOrderStatusChangeView.as_view(), name = 'adminorderstatuschange'),

    path('admin-product/lists/', AdminProductListView.as_view(), name = 'adminproductlist'),
    path('admin-saleitems/lists/', AdminSaleItemListView.as_view(), name = 'adminsaleitemslist'),
    path('admin-product/create-as-view/', AdminProductCreateView.as_view(), name = 'adminproductasview'),
    path('admin-product-edit/<int:pk>', AdminProductEditView.as_view(), name='adminproductedit'),

    path('admin-cashsalelist/', AdminCashSaleView.as_view(), name = 'admincashsalelist'),
    path('admin-creditsalelist/', AdminCreditSaleView.as_view(), name='admincreditsalelist'),
    path('admin-allsalelist/', AdminAllSaleView.as_view(), name='allsalelist'),
    path('admin-datefiltersearchview/', DateFilterSearchView.as_view(), name = 'datefiltersearchview'),

    path('admin/cash/salelist/csv', cash_sale_list_csv_rep, name='cashsalelistcsv'),
    path('admin/credit/salelist/cav', credit_sale_list_csv_rep, name='creditsalelistcsv'),
    path('admin/salelist/bycustomer', sale_list_by_customer_csv_rep, name='salelistbycustomercsv'),
    path('admin/salereport/byinvoice', SaleReportbyInvoiceView.as_view(), name='salereportbyinvoiceview'),
    path('admin/tax-report/', AdminTaxReportView.as_view(), name='admintaxreport'),

    path('admin-category/lists/', AdminCategoryListView.as_view(), name = 'admincategorylist'),
    path('admin-category/create/', AdminCategoryCreateView.as_view(), name = 'admincategorycreate'),

    path('admin-customer/lists/', CustomerListView.as_view(), name='admincustomerlist'),

    path('admin/expense/category/list', AdminExpenseCategoryListView.as_view(), name='adminexpensecategorylist'),
    path('admin/expense/category/create/', AdminExpenseCategoryCreateView.as_view(), name='expensecategorycreate'),
    path('admin/admindailyexpense/', AdminDailyExpenseView.as_view(), name='admindailyexpense'),
    path('admin/admindailyexpensecreate/',AdminExpenseCreateView.as_view(), name = 'admindailyexpensecreate'),

    path('admin/adminstafflist/',AdminStaffListView.as_view(), name='adminstafflist'),
    path('admin/adminstaffcreate/',AdminStaffCreateView.as_view(), name='adminstaffcreate'),
    path('admin/userregistration/', AdminUserRegistraionView.as_view(), name='userregistration'),


    path('cashier-login/', CashierLoginView.as_view(), name = 'cashierlogin'),
    path('cashier-main-dashboard/', CashierMainDashboardView.as_view(), name='cashiermaindashboard'),
    path('cashier-home/', CashierHomeView.as_view(), name = 'cashierhome'),

    path('cashier-products-list-by-category/', CashierCreateInvoiceView.as_view(), name='cashiercreateinvoice'),
    path('cashier-addtocart/<int:pro_id>', CashierAddToCartView.as_view(), name = 'cashieraddtocart'),
    path('cashier-cart-view/', CashierMyCartView.as_view(), name='cashiercartview'),
    path('cashier-empty-cart', CashierEmptyCartView.as_view(), name='cashieremptycart'),
    path('cashier/managecart/<int:cp_id>/', CashierManageCartView.as_view(), name='cashiermanagecart'),
    path('cashier/cashiercheckout/', CashierCheckoutView.as_view(), name='cashiercheckout'),

    path('cashier-order-detail/<int:pk>/', CashierOrderDetailView.as_view(), name = 'cashierorderdetail'),
    path('cashier-order-change-<int:pk>/', CashierOrderStatusChangeView.as_view(), name = 'cashierorderstatuschange'),
    path('cashier-all-order/', CashierOrderListView.as_view(), name = 'cashierorderlists'),
    path('cashier-receive-order-list/',CashierReceiveOrderView.as_view(), name='receivedorderlist'),
    path('cashier-cash-sale-invoice/',CashierCashSaleInvoiceView.as_view(), name='cashiercashsaleinvoice'),
    path('cashier-credit-sale-invoice/',CashierCreditSaleInvoiceView.as_view(), name='cashiercreditsaleinvoice'),
    path('cashier-sale-items-list/', CashierSaleItemListView.as_view(), name='cashiersaleitemlist'),
    path('cashier-sale-invoice-report/', CashierSaleInvoiceReportView.as_view(), name='cashiersaleinvoicereport'),

    path('test_pdf/<int:pk>/', render_pdf_view, name='test_pdf'),

    # path('admin-datefiltersearchview/', datefilter, name = 'datefiltersearchview'),
    #expense
    path('export_pdf/', export_pdf, name='export_pdf'),
    path('expense_csv_rep/', expense_csv_rep, name='expense_csv_rep'),
    path('sale_item_csv_rep/',sale_item_csv_rep, name='sale_item_csv_rep'),
    path('sale_list_by_invoice_csv_rep/', sale_list_by_invoice_csv_rep, name='salelistbyinvoicecsvrep'),
    path('cashier_sale_invoice_report_csv/', cashier_sale_invoice_report_csv, name='cashier_sale_invoice_report_csv')






]
