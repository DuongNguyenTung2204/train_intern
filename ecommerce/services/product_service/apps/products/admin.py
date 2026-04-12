from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "stock", "is_active", "created_at")
    list_filter  = ("is_active", "categories")
    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("categories",)
