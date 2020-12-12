import csv

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.generic import TemplateView,View, CreateView, FormView, DetailView, ListView
from .models import *
from .forms import *
from .filters import OrderFilter
#html2pdf
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

#install WeasyPrint
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import tempfile
from django.db.models import Sum

# Create your views here.

class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)


class HomeView(EcomMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = Product.objects.all().order_by('-id')
        return context

class AllProductsView(EcomMixin,TemplateView):
    template_name = 'allproducts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context

class ProductDetailView(EcomMixin, TemplateView):
    template_name = 'productdetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        context['product'] = product
        return context


class AddToCartView(EcomMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # prouduct id get from request url
        product_id = self.kwargs['pro_id']

        #get product
        product_obj = Product.objects.get(id=product_id)

        #check it cart exist
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id= cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product = product_obj)
            #Product already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total +=product_obj.selling_price
                cart_obj.tax = cart_obj.total * 0.05
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
            #New item added in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.tax = cart_obj.total * 0.05
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price,
                                                     quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        # check if product alredy exists
        context['product_list'] = Product.objects.all().order_by('-id')
        return context


class MyCartView(EcomMixin, TemplateView):
    template_name = 'mycart.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class ManageCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        print("This is Manage Cart Section...")
        cp_id = kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        # cart_id = request.session.get('cart_id', None)
        # if cart_id:
        #     cart2 = Cart.objects.get(id=cart_id)
        #     if cart1 != cart2:
        #         return redirect("ecoapp:mycart")
        # else:
        #     return redirect("ecoapp:mycart")
        # print(cp_id, action)
        if action == "inc":
            cp_obj.quantity +=1
            cp_obj.subtotal += cp_obj.rate

            cp_obj.save()
            cart_obj.total +=cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('ecoapp:mycart')


class EmptyCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total =0
            cart.save()
        return redirect('ecoapp:mycart')


class CheckoutView(EcomMixin,CreateView):
    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('ecoapp:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            print('login....')
        else:
            return redirect('/login/?next=/checkout/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.tax = cart_obj.tax
            form.instance.all_total = cart_obj.super_total
            # form.instance.ordered_staus = 'Cash'
            del self.request.session['cart_id']
        else:
            return redirect('ecoapp:home')
        return super().form_valid(form)



class CustomerRegistraionView(CreateView):
    template_name = 'customerregistration.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('ecoapp:home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username, password, email)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url = self.request.GET.get('next')
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('ecoapp:home')

class CustomerLoginView(FormView):
    template_name = 'customerlogin.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('ecoapp:home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form':self.form_class, 'error':'Invalid user login!'})

        return super().form_valid(form)

    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url = self.request.GET.get('next')
            return next_url
        else:
            return self.success_url






class AboutView(EcomMixin, TemplateView):
    template_name = 'about.html'


class ContactView(EcomMixin, TemplateView):
    template_name = 'contact.html'


class CustomerProfileView(TemplateView):
    template_name = 'customerprofile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            print('login....')
        else:
            return redirect('/login/?next=/profile/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer']=customer
        orders = Order.objects.filter(cart__customer=customer).order_by('-id')
        context['orders'] = orders
        return context

class CustomerOrderDetailView(DetailView):
    template_name = 'customerorderdetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs['pk']
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect('ecoapp:customerprofile')
        else:
            return redirect('/login/?next=/profile/')
        return super().dispatch(request, *args, **kwargs)

class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get('keyword')
        results = Product.objects.filter(Q(title__icontains=kw)| Q(description__icontains=kw))
        context['results']=results
        return context



# def datefilter(request):
#     form = StockHistorySearchForm(request.POST or None)
#     if request.method == 'POST':
#         queryset = Order.objects.filter(created_at__range=[form['start_date'].value(),form['end_date'].value()])
#         context = {
#         'form':form,
#         'queryset': queryset
#          }
#         return render(request, 'adminpages/datefiltersearchview.html', context)
#     context = {
#         'form': form,
#
#     }
#     return render(request, 'adminpages/datefiltersearchview.html', context)
#




#Admin Section

class AdminLoginView(FormView):
    template_name = 'adminpages/adminlogin.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('ecoapp:adminhome')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)

        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid user login!'})
        return super().form_valid(form)


class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/admin-login/')
        return super().dispatch(request, *args, **kwargs)

class CashierRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Staff.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/cashier-login/')
        return super().dispatch(request, *args, **kwargs)


class AdminHomeView(AdminRequiredMixin,TemplateView):
    template_name = 'adminpages/adminhome.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        credit_num = Order.objects.filter(ordered_staus="Credit")
        ordering = Order.objects.filter(ordered_staus="Ordering")
        customer = Customer.objects.all()
        product = Product.objects.all()

        sum = credit_num.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']
        contex['creditsum'] = sum_amt


        contex['pendingorders'] = Order.objects.filter(ordered_staus="Credit")
        contex['ordering'] = ordering.count()
        contex['creditno'] = credit_num.count()
        contex['customer'] = customer.count()
        contex['products'] = product.count()
        return contex

# sum=expenses.aggregate(Sum('amount'))
# sum['amount__sum']


class AdminCashSaleView(AdminRequiredMixin,TemplateView):
    template_name = 'adminpages/admincashlist.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['pendingorders'] = Order.objects.filter(ordered_staus="Cash")
        contex['myfilter'] = OrderFilter()

        return contex


class AdminCreditSaleView(AdminRequiredMixin,TemplateView):
    template_name = 'adminpages/admincreditlist.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        credit_num = Order.objects.filter(ordered_staus="Credit")
        contex['pendingorders'] = Order.objects.filter(ordered_staus="Credit")

        sum = credit_num.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']
        contex['creditsum'] = sum_amt
        return contex


class AdminAllSaleView(AdminRequiredMixin,TemplateView):
    template_name = 'adminpages/adminallsalelist.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['pendingorders'] = Order.objects.all()
        return contex



class AdminOrderDetailView(AdminRequiredMixin,DetailView):
    template_name = 'adminpages/adminorderdetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = STATUS
        return context



class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/adminorderlists.html'
    queryset = Order.objects.all().order_by('-id')
    context_object_name = 'allorders'


class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        order_obj.ordered_staus = new_status
        order_obj.save()
        return redirect(reverse_lazy('ecoapp:adminorderdetail', kwargs={'pk':order_id}))



class AdminProductListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/adminproductlist.html'
    queryset = Product.objects.all().order_by('-id')
    context_object_name = 'allproducts'



class AdminProductCreateView(AdminRequiredMixin, CreateView):
    template_name = 'adminpages/adminproductcreate.html'
    form_class = ProductCreateForm
    success_url = reverse_lazy('ecoapp:adminproductlist')

    def form_valid(self, form):
        p=form.save()
        images = self.request.FILES.getlist('more_images')
        for i in images:
            ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)


class AdminCategoryListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/admincategorylist.html'
    queryset = Category.objects.all()
    context_object_name = 'allcategory'

class AdminCategoryCreateView(AdminRequiredMixin, CreateView):
    template_name = 'adminpages/admincategorycreate.html'
    form_class = CategoryCreate
    success_url = reverse_lazy('ecoapp:admincategorylist')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)



class AdminSaleItemListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/adminsaleitemlist.html'
    queryset = CartProduct.objects.all().order_by('-id')
    context_object_name = 'allproducts'

#Product Edit
class AdminProductEditView(AdminRequiredMixin, View):
    def get(self,request, pk):
        pi = Product.objects.get(id=pk)
        fm = AdminProductEditForm(instance=pi)
        return render(request,'adminpages/adminproductedit.html', {'form':fm})

    def post(self, request, pk):
        pi = Product.objects.get(id=pk)
        fm = AdminProductEditForm(request.POST,instance=pi)
        if fm.is_valid():
            fm.save()
        return redirect('ecoapp:adminproductlist')



#Date Filter
class DateFilterSearchView(AdminRequiredMixin,View):
    def get(self,request):
        form = StockHistorySearchForm()
        queryset = Order.objects.all()
        context = {
            'form': form,
            'queryset': queryset
        }
        return render(request, 'adminpages/datefiltersearchview.html', context)

    def post(self, request):
        form = StockHistorySearchForm(request.POST)
        queryset = Order.objects.filter(created_at__range=[form['start_date'].value(), form['end_date'].value()])
        context = {
            'form': form,
            'queryset': queryset
        }
        return render(request, 'adminpages/datefiltersearchview.html', context)




class AdminUserRegistraionView(AdminRequiredMixin,CreateView):
    template_name = 'adminpages/userregistration.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('ecoapp:admincustomerlist')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username, password, email)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url = self.request.GET.get('next')
            return next_url
        else:
            return self.success_url







class CustomerListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/admincustomerlist.html'
    queryset = Customer.objects.all()
    context_object_name = 'customerlist'


#staff section
class AdminStaffListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/adminstafflist.html'
    queryset = Staff.objects.all()
    context_object_name = 'allstaff'

#create staff
class AdminStaffCreateView(AdminRequiredMixin, CreateView):
    template_name = 'adminpages/adminstaffcreate.html'
    form_class = AdminCreateStaffForm
    success_url = reverse_lazy('ecoapp:adminstafflist')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

#expense
class AdminExpenseCategoryListView(AdminRequiredMixin, ListView):
    template_name = 'adminpages/adminexpensecategorylist.html'
    queryset = ExpenseCategory.objects.all()
    context_object_name = 'allcategory'


class AdminExpenseCategoryCreateView(AdminRequiredMixin, CreateView):
    template_name = 'adminpages/expensecategorycreate.html'
    form_class = ExpenseCategoryCreate
    success_url = reverse_lazy('ecoapp:adminexpensecategorylist')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)



class AdminDailyExpenseView(AdminRequiredMixin,ListView):
    template_name = 'adminpages/admindailyexpense.html'
    queryset = Expense.objects.all().order_by('-id')
    context_object_name = 'expenselist'


class AdminExpenseCreateView(AdminRequiredMixin, CreateView):
    template_name = 'adminpages/admindailyexpensecreate.html'
    form_class = AdminExpenseForm
    success_url = reverse_lazy('ecoapp:admindailyexpense')

    def form_valid(self, form):
        form.save()
        # images = self.request.FILES.getlist('more_images')
        # for i in images:
        #     ProductImage.objects.create(product=p, image=i)
        return super().form_valid(form)


#cash sale list by invoice

class SaleReportbyInvoiceView(AdminRequiredMixin,TemplateView):
    template_name = 'adminpages/salereportbyinvoiceview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcat'] = Cart.objects.all().order_by('-id')
        return context



#cashier sale invoice view
class AdminTaxReportView(AdminRequiredMixin,View):
    def get(self,request):
        form = StockHistorySearchForm()
        queryset = Order.objects.all()
        sum = queryset.aggregate(Sum('tax'))
        sum_tax = sum['tax__sum']
        context = {
            'form': form,
            'tax_list': queryset,
            'sum_tax': sum_tax,
        }
        return render(request, 'adminpages/admintaxreport.html', context)

    def post(self, request):
        form = StockHistorySearchForm(request.POST)
        queryset = Order.objects.filter(created_at__range=[form['start_date'].value(), form['end_date'].value()])
        sum = queryset.aggregate(Sum('tax'))
        sum_tax = sum['tax__sum']

        # tax_total = queryset.aggregate(Sum('tax'))
        # taxtxt = tax_total['tax__sum']

        context = {
            'form': form,
            'tax_list': queryset,
            'sum_tax' : sum_tax,
            # 'taxtxt':taxtxt,
        }
        # print(sum_amt)
        return render(request, 'adminpages/admintaxreport.html', context)




###############################################Cashier Sector

class CashierLoginView(FormView):
    template_name = 'cashier/cashierlogin.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('ecoapp:cashiermaindashboard')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None and Staff.objects.filter(user=usr).exists():
            login(self.request, usr)

        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid user login!'})
        return super().form_valid(form)


class CashierMainDashboardView(CashierRequiredMixin,TemplateView):
    template_name = 'cashier/cashiermaindashboard.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        total_ordering = Order.objects.filter(ordered_staus="Ordering")
        total_received = Order.objects.filter(ordered_staus="Accept")
        credit_num = Order.objects.filter(ordered_staus="Credit")
        contex['countorder'] = total_ordering.count()
        contex['countreceive'] = total_received.count()
        contex['creditno'] = credit_num.count()
        contex['pendingorders'] = Order.objects.filter(ordered_staus="Ordering")
        contex['receiveorders'] = Order.objects.filter(ordered_staus="Accept")
        return contex


class CashierHomeView(CashierRequiredMixin,TemplateView):
    template_name = 'cashier/cashierhome.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['pendingorders'] = Order.objects.filter(ordered_staus="Ordering")
        return contex





class CashierReceiveOrderView(CashierRequiredMixin,TemplateView):
    template_name = 'cashier/receiveorderlist.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['pendingorders'] = Order.objects.filter(ordered_staus="Accept")
        return contex



#cashier sale invoice view
class CashierCashSaleInvoiceView(CashierRequiredMixin,View):
    def get(self,request):
        form = StockHistorySearchForm()
        queryset = Order.objects.filter(ordered_staus="Cash").order_by('-id')
        sum = queryset.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']
        context = {
            'form': form,
            'pendingorders': queryset,
            'sum_amt': sum_amt,
        }
        return render(request, 'cashier/cashiercashsaleinvoice.html', context)

    def post(self, request):
        form = StockHistorySearchForm(request.POST)
        queryset = Order.objects.filter(created_at__range=[form['start_date'].value(), form['end_date'].value()])
        sum = queryset.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']

        # tax_total = queryset.aggregate(Sum('tax'))
        # taxtxt = tax_total['tax__sum']

        context = {
            'form': form,
            'pendingorders': queryset,
            'sum_amt' : sum_amt,
            # 'taxtxt':taxtxt,
        }
        # print(sum_amt)
        return render(request, 'cashier/cashiercashsaleinvoice.html', context)



#cashier sale credit view
class CashierCreditSaleInvoiceView(CashierRequiredMixin,View):
    def get(self,request):
        form = StockHistorySearchForm()
        queryset = Order.objects.filter(ordered_staus="Credit").order_by('-id')
        sum = queryset.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']
        context = {
            'form': form,
            'pendingorders': queryset,
            'sum_amt': sum_amt,
        }
        return render(request, 'cashier/cashiercreditsaleinvoice.html', context)

    def post(self, request):
        form = StockHistorySearchForm(request.POST)
        queryset = Order.objects.filter(created_at__range=[form['start_date'].value(), form['end_date'].value()])
        sum = queryset.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']

        # tax_total = queryset.aggregate(Sum('tax'))
        # taxtxt = tax_total['tax__sum']

        context = {
            'form': form,
            'pendingorders': queryset,
            'sum_amt' : sum_amt,
            # 'taxtxt':taxtxt,
        }
        # print(sum_amt)
        return render(request, 'cashier/cashiercreditsaleinvoice.html', context)





#
# class CashierCreditSaleInvoiceView(CashierRequiredMixin,TemplateView):
#     template_name = 'cashier/cashiercreditsaleinvoice.html'
#
#     def get_context_data(self, **kwargs):
#         contex = super().get_context_data(**kwargs)
#         contex['pendingorders'] = Order.objects.filter(ordered_staus="Credit").order_by('-id')
#         return contex




class CashierOrderDetailView(CashierRequiredMixin,DetailView):
    template_name = 'cashier/cashierorderdetail.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allstatus'] = STATUS
        return context








class CashierOrderStatusChangeView(CashierRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        order_obj.ordered_staus = new_status
        order_obj.save()
        return redirect(reverse_lazy('ecoapp:cashierorderdetail', kwargs={'pk':order_id}))


class CashierOrderListView(CashierRequiredMixin, ListView):
    template_name = 'cashier/cashierorderlists.html'
    queryset = Order.objects.all().order_by('-id')
    context_object_name = 'allorders'


class CashierSaleItemListView(CashierRequiredMixin, ListView):
    template_name = 'cashier/cashiersaleitemlist.html'
    queryset = CartProduct.objects.all().order_by('-id')
    context_object_name = 'allproducts'



#cashier sale invoice report
class CashierSaleInvoiceReportView(CashierRequiredMixin,View):
    def get(self,request):
        form = StockHistorySearchForm()
        queryset = Order.objects.all()
        context = {
            'form': form,
            'allinvoice': queryset
        }
        return render(request, 'cashier/cashiersaleinvoicereport.html', context)

    def post(self, request):
        form = StockHistorySearchForm(request.POST)
        queryset = Order.objects.filter(created_at__range=[form['start_date'].value(), form['end_date'].value()])
        sum = queryset.aggregate(Sum('all_total'))
        sum_amt = sum['all_total__sum']

        tax_total = queryset.aggregate(Sum('tax'))
        taxtxt = tax_total['tax__sum']

        context = {
            'form': form,
            'allinvoice': queryset,
            'sum_amt' : sum_amt,
            'taxtxt':taxtxt,
        }
        # print(sum_amt)
        return render(request, 'cashier/cashiersaleinvoicereport.html', context)


        # sum = credit_num.aggregate(Sum('all_total'))
        # sum_amt = sum['all_total__sum']
        # contex['creditsum'] = sum_amt


class CashierCreateInvoiceView(CashierRequiredMixin,TemplateView):
    template_name = 'cashier/cashiercreateinvoice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Category.objects.all()
        return context




class CashierAddToCartView(CashierRequiredMixin, TemplateView):
    template_name = 'cashier/cashieraddtocart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # prouduct id get from request url
        product_id = self.kwargs['pro_id']

        #get product
        product_obj = Product.objects.get(id=product_id)

        #check it cart exist
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id= cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product = product_obj)
            #Product already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total +=product_obj.selling_price
                cart_obj.tax = cart_obj.total * 0.05
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
            #New item added in cart
            else:
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.tax = cart_obj.total * 0.05
                cart_obj.super_total = cart_obj.tax + cart_obj.total
                cart_obj.save()
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price,
                                                     quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        # check if product alredy exists
        context['allcategories'] = Category.objects.all()
        return context



class CashierMyCartView(CashierRequiredMixin, TemplateView):
    template_name = 'cashier/cashiercartview.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context



class CashierEmptyCartView(CashierRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total =0
            cart.tax = 0
            cart.super_total=0
            cart.save()
        return redirect('ecoapp:cashiercartview')



class CashierManageCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):

        cp_id = kwargs['cp_id']
        action = request.GET.get('action')
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        if action == "inc":
            cp_obj.quantity +=1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total +=cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
        elif action == 'dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == 'rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.tax = cart_obj.total * 0.05
            cart_obj.super_total = cart_obj.tax + cart_obj.total
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('ecoapp:cashiercartview')



class CashierCheckoutView(EcomMixin,CreateView):
    template_name = 'cashier/cashiercheckout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('ecoapp:cashiercreateinvoice')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            print('login....')
        else:
            return redirect('/login/?next=/checkout/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.ordered_staus = 'Accept'
            form.instance.tax = cart_obj.tax
            form.instance.all_total = cart_obj.super_total

            del self.request.session['cart_id']
        else:
            return redirect('ecoapp:cashiercreateinvoice')
        return super().form_valid(form)


class CashierItemsSearchView(CashierRequiredMixin,TemplateView):
    template_name = 'cashier/cashieritemsearch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get('keyword')
        results = Product.objects.filter(Q(title__icontains=kw)| Q(description__icontains=kw))
        context['results']=results
        return context





# html2pdf

#ResponsePDF
def render_pdf_view(request,pk):
    ord_obj = Order.objects.get(id=pk)

    template_path = 'invoicepage/invoicesample.html'
    context = {'ord_obj': ord_obj}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #if download::
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #if display::
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors')
    return response


# pip install WeasyPrint
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='inline; attachment; filename="expense.pdf"'
    response['Content-Transfer-Encoding']= 'binary'

    expenses = Expense.objects.all()

    sum=expenses.aggregate(Sum('amount'))

    html_string = render_to_string('adminpages/expensepdf.html', {'expense':expenses,'total':sum['amount__sum']})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True)as output:
        output.write(result)
        output.flush()
        output = open(output.name,'rb')
        response.write(output.read())
    return response

################################### CSV Download
def expense_csv_rep(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="expense.csv"'

    writer = csv.writer(response)
    writer.writerow(['category','exp_title','amount','description','created_at'])

    expenses = Expense.objects.all()

    for expense in expenses:
        writer.writerow([expense.category,expense.exp_title,expense.amount,expense.description,expense.created_at])

    return response



def sale_item_csv_rep(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="saleitemreports.csv"'

    writer = csv.writer(response)
    writer.writerow(['invoice_id','product','rate','quantity','subtotal'])

    repos = CartProduct.objects.all()

    for expense in repos:
        writer.writerow([expense.cart.id,expense.product.title,expense.rate,expense.quantity,expense.subtotal])

    return response


#cash sale csv list
def cash_sale_list_csv_rep(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="cashsalelist.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice_id','CustomerName','Date','Total',])

    repos = Order.objects.filter(ordered_staus="Cash")

    for cashlist in repos:
        writer.writerow([cashlist.cart.id,cashlist.ordered_by,cashlist.created_at,cashlist.all_total])

    return response



#credit sale list csv
def credit_sale_list_csv_rep(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="creditsalelist.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice_id','CustomerName','Date','Total',])

    repos = Order.objects.filter(ordered_staus="Credit")

    for cashlist in repos:
        writer.writerow([cashlist.cart.id,cashlist.ordered_by,cashlist.created_at,cashlist.all_total])

    return response


#sale list csv by customer
def sale_list_by_customer_csv_rep(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="creditsalelist.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice_id','CustomerName','Date','Tax','Total','Status'])

    repos = Order.objects.all()

    for cashlist in repos:
        writer.writerow([cashlist.cart.id,cashlist.ordered_by,cashlist.created_at,cashlist.tax,cashlist.all_total,cashlist.ordered_staus])

    return response


#sale list csv by customer
def sale_list_by_invoice_csv_rep(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="salereportbyinvoice.csv"'

    writer = csv.writer(response)
    # writer.writerow(['Invoice_id','CustomerName','Date','Total','Status'])

    repos = CartProduct.objects.all()
    writer.writerow(['InvoiceNo','Item Name', 'Rate', 'Quantity', 'Sub Total','Date'])

    for p in repos:
        writer.writerow([p.cart.id,p.product.title,p.rate, p.quantity, p.subtotal,p.cart.created_at])

    return response

#sale invoice csv by cashier
def cashier_sale_invoice_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']='inline; attachment; filename="salereportbyinvoice.csv"'

    writer = csv.writer(response)
    # writer.writerow(['Invoice_id','CustomerName','Date','Total','Status'])

    repos = Order.objects.all()
    writer.writerow(['InvoiceNo','Customer Name', 'Tax', 'Total', 'Status','Date'])

    for i in repos:
        writer.writerow([i.cart.id, i.ordered_by, i.tax, i.all_total, i.ordered_staus, i.created_at])

    return response


