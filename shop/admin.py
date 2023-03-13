from django.contrib import admin
from shop.models import *
from django.utils.html import format_html




class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['id',"title"]

    def delete_button(self, obj):
        return format_html("<a href='/admin/shop/category/{}/delete'>Delete</a>", obj.id)
    
    def update_button(self, obj):
        return format_html("<a href='/admin/shop/category/{}/change'>Edit</a>", obj.id)


    list_display = ["id","title","description","slug", 'delete_button','update_button']
    list_display_links = ['title','slug']

    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug":("name",)}

admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(Address)