from django.contrib import admin

from .models import (
    BlogPost,
    Brand,
    Cart,
    CartItem,
    Category,
    Favorites,
    Order,
    OrderItem,
    Payment,
    Product,
    Ticket,
    TicketMessage,
)


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


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
  list_display = ('user', 'created_at', 'updated_at')
  search_fields = ('user__phone_number', 'user__full_name')
  readonly_fields = ('created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
  list_display = ('cart', 'product', 'quantity')
  search_fields = ('cart__user__phone_number', 'cart__user__full_name', 'product__name')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
  list_display = ('user', 'product')
  search_fields = ('user__phone_number', 'user__full_name', 'product__name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'updated_at')
  list_filter = ('status', 'created_at', 'updated_at')
  search_fields = ('=id', 'user__phone_number', 'user__full_name')
  readonly_fields = ('created_at', 'updated_at')
  ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
  list_display = ('order', 'product', 'quantity', 'price_at_purchase')
  search_fields = ('=order__id', 'product__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
  list_display = ('order', 'transaction_id', 'status', 'created_at')
  list_filter = ('status', 'created_at')
  search_fields = ('=order__id', 'transaction_id')
  readonly_fields = ('created_at',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
  list_display = ('subject', 'user', 'status', 'created_at')
  list_filter = ('status', 'created_at')
  search_fields = ('subject', 'user__phone_number', 'user__full_name')
  readonly_fields = ('created_at',)
  ordering = ('-created_at',)


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
  list_display = ('ticket', 'sender', 'created_at')
  search_fields = ('ticket__subject', 'sender__phone_number', 'sender__full_name', 'message')
  readonly_fields = ('created_at',)
  ordering = ('-created_at',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
  list_display = ('title', 'author', 'created_at')
  search_fields = ('title', 'content', 'author__phone_number', 'author__full_name')
  readonly_fields = ('created_at',)
  ordering = ('-created_at',)
