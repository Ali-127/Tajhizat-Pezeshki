from django.urls import path

from .views import about_view, blog_post_view, blog_view, landing_view, product_detail_view, shop_view, dashboard_view

urlpatterns = [
  path('', landing_view, name='landing'),
  path('dashboard/', dashboard_view, name='dashboard'),
  path('shop/<int:product_id>/', product_detail_view, name='product_detail'),
  path('shop/', shop_view, name='shop'),
  path('about/', about_view, name='about'),
  path('blog/<int:post_id>/', blog_post_view, name='blog_detail'),
  path('blog/', blog_view, name='blog'),
]
