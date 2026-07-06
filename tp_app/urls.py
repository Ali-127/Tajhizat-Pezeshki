from django.urls import path

from .views import about_view, blog_view, landing_view, shop_view

urlpatterns = [
  path('', landing_view, name='landing'),
  path('shop/', shop_view, name='shop'),
  path('about/', about_view, name='about'),
  path('blog/', blog_view, name='blog'),
]
