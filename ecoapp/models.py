from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='admins')
    mobile = models.CharField(max_length=255)
    NRCno = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='admins')
    mobile = models.CharField(max_length=255)
    NRCno = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products',blank=True, null=True)
    marked_price = models.PositiveIntegerField(blank=True, null=True)
    selling_price = models.PositiveIntegerField()
    description = models.TextField()
    warranty = models.CharField(max_length=255, null=True, blank=True)
    return_policy = models.CharField(max_length=255, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')

    def __str__(self):
        return self.product.title





class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    tax = models.PositiveIntegerField(default=0)
    super_total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart : "+ str(self.id)

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart : "+ str(self.cart.id)+ "CartProduct : " + str(self.id)

class OrderStaus(models.Model):
    status = models.CharField(max_length=255)

    def __str__(self):
        return self.status

STATUS=(
    ("Ordering","Ordering"),("Accept","Accept"),("Cash","Cash"),("Credit","Credit"),("Consignment","Consignment"),("Complete","Complete")
)


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255, default='local')
    mobile = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    tax = models.PositiveIntegerField()
    all_total = models.PositiveIntegerField()
    ordered_staus = models.CharField(max_length=255, choices=STATUS, default='Ordering')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order : " + str(self.id)


class ExpenseCategory(models.Model):
    category = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.category

class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    exp_title = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    image = models.ImageField(upload_to='expensefiles', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.exp_title
