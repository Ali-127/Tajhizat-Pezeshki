from django.shortcuts import render

from .models import BlogPost, Product


def landing_view(request):
  active_products = Product.objects.filter(is_active=True).select_related(
    'brand',
    'category',
  )
  context = {
    'special_products': active_products.order_by('-stock', '-created_at')[:5],
    'latest_products': active_products.order_by('-created_at')[:5],
    'latest_posts': BlogPost.objects.select_related('author').order_by('-created_at')[:3],
  }
  return render(request=request, template_name='landing.html', context=context)

def shop_view(request):
  products = Product.objects.filter(is_active=True).select_related('brand', 'category')
  return render(request=request, template_name='shop.html', context={'products': products})

def about_view(request):
  return render(request=request, template_name='darabarema.html')

def blog_view(request):
  posts = BlogPost.objects.select_related('author').order_by('-created_at')
  return render(request=request, template_name='weblog.html', context={'posts': posts})

# def t_view(request):
#   return render(request=request, template_name='shop.html')
# def shop_view(request):
#   return render(request=request, template_name='shop.html')
