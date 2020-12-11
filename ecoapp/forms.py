from django import forms
from .models import *
from django.contrib.auth.models import User

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordered_by', 'mobile', 'email', 'shipping_address']


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput)
    class Meta:
        model = Customer
        fields = ['username', 'password','email' ,'full_name', 'address']

    def clean_username(self):
        uname = self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError('username is already exists!')
        return uname

class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class ProductCreateForm(forms.ModelForm):
    more_images = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'multiple':True}))
    class Meta:
        model = Product
        fields = ['title', 'slug', 'category', 'image', 'marked_price', 'selling_price', 'description', 'warranty', 'return_policy']
#         widgets = {
#             'title':forms.TextInput(attrs={'class': 'form-control'}),
#             'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'must be unique one world.....'}),
#             'category': forms.Select(attrs={'class': 'form-control'}),
#             'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#             'marked_price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control'}),
#             'warranty': forms.TextInput(attrs={'class': 'form-control'}),
#             'return_policy': forms.TextInput(attrs={'class': 'form-control'}),
#         }
# class ProductCreateForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['title', 'slug', 'category', 'image', 'marked_price', 'selling_price', 'description', 'warranty', 'return_policy']
#
# class SmallProductImage(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ['product', 'image']

class CategoryCreate(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title','slug']


class ExpenseCategoryCreate(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['category','slug']


class StockHistorySearchForm(forms.ModelForm):
    # export_to_CSV = forms.BooleanField(required=False)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    class Meta:
        model = Order
        fields = ['start_date', 'end_date']


class AdminProductEditForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'slug', 'category', 'image', 'marked_price', 'selling_price', 'description', 'warranty', 'return_policy']


class AdminExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'exp_title','amount', 'description', 'image']

class AdminCreateStaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user','full_name','image','mobile','NRCno','role']