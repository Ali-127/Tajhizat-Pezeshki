from django.urls import path

from .views import about_view, blog_post_view, blog_view, landing_view, product_detail_view, shop_view, dashboard_view, cart_view, add_to_cart_view, toggle_favorite_view, favorites_view
from .views import dashboard_profile_update_view, dashboard_address_add_view, dashboard_address_delete_view, dashboard_create_ticket_view, dashboard_add_to_cart_view, dashboard_remove_favorite_view

urlpatterns = [
  path('', landing_view, name='landing'),
  path('dashboard/', dashboard_view, name='dashboard'),
  path('dashboard/profile/update/', dashboard_profile_update_view, name='dashboard_profile_update'),
  path('dashboard/address/add/', dashboard_address_add_view, name='dashboard_address_add'),
  path('dashboard/address/<int:address_id>/delete/', dashboard_address_delete_view, name='dashboard_address_delete'),
  path('dashboard/ticket/create/', dashboard_create_ticket_view, name='dashboard_create_ticket'),
  path('dashboard/cart/<int:product_id>/', dashboard_add_to_cart_view, name='dashboard_add_to_cart'),
  path('dashboard/favorites/<int:product_id>/remove/', dashboard_remove_favorite_view, name='dashboard_remove_favorite'),
  path('shop/<int:product_id>/', product_detail_view, name='product_detail'),
  path('shop/', shop_view, name='shop'),
  path('cart/', cart_view, name='cart'),
  path('cart/add/<int:product_id>/', add_to_cart_view, name='add_to_cart'),
  path('favorites/toggle/<int:product_id>/', toggle_favorite_view, name='toggle_favorite'),
  path('about/', about_view, name='about'),
  path('blog/<int:post_id>/', blog_post_view, name='blog_detail'),
  path('blog/', blog_view, name='blog'),
  path('favorites/', favorites_view, name='favorites'),
]
