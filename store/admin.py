from django.contrib import admin
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.orders import Order

class AdminProduct(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']

class AdminCategory(admin.ModelAdmin):
    list_display = ['name']

class AdminCustomer(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email', 'password']

class AdminOrder(admin.ModelAdmin):
    list_display = ['id', 'customer', 'product', 'quantity', 'price', 'address', 'phone', 'status', 'payment_method','paid']
    search_fields = ['id', 'customer__first_name', 'customer__last_name', 'product__name']

admin.site.register(Product, AdminProduct)
admin.site.register(Category, AdminCategory)
admin.site.register(Customer, AdminCustomer)
admin.site.register(Order, AdminOrder)
