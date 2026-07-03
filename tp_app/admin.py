from django.contrib import admin
from .models import Category, Brand, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug')
  
  prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
  list_display = ('name', 'slug')

  prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ('name', 'brand', 'category', 'price', 'stock', 'is_active', 'created_at')

  list_filter = ('is_active', 'category', 'brand', 'created_at')

  search_fields = ('name', 'description', 'brand__name', 'category__name')

  list_editable = ('price', 'stock', 'is_active')

  ordering = ('-created_at',)

