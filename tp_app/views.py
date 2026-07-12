from decimal import Decimal

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import BlogPost, Brand, Category, Product


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


def _get_pagination_range(page_obj, delta=2):
  total_pages = page_obj.paginator.num_pages
  current = page_obj.number

  if total_pages <= 7:
    return list(range(1, total_pages + 1))

  pages = [1]
  left = max(2, current - delta)
  right = min(total_pages - 1, current + delta)

  if left > 2:
    pages.append('...')

  pages.extend(range(left, right + 1))

  if right < total_pages - 1:
    pages.append('...')

  pages.append(total_pages)
  return pages


def shop_view(request):
  products = Product.objects.filter(is_active=True).select_related('brand', 'category')
  categories = Category.objects.annotate(
    count=Count('products', filter=Q(products__is_active=True)),
  ).order_by('name')
  brands = Brand.objects.annotate(
    count=Count('products', filter=Q(products__is_active=True)),
  ).order_by('name')

  selected_category = request.GET.get('category', '')
  selected_brands = request.GET.getlist('brand')
  price_min = request.GET.get('price_min', '')
  price_max = request.GET.get('price_max', '')
  stock = request.GET.get('stock', '')
  warranty = request.GET.get('warranty') == '1'
  after_sales = request.GET.get('after_sales') == '1'
  fast_delivery = request.GET.get('fast_delivery') == '1'
  installation = request.GET.get('installation') == '1'
  sort = request.GET.get('sort', 'newest')
  page = request.GET.get('page', 1)

  if selected_category:
    products = products.filter(category__slug=selected_category)
  if selected_brands:
    products = products.filter(brand__slug__in=selected_brands)

  if price_min:
    try:
      products = products.filter(price__gte=Decimal(price_min.replace(',', '')))
    except Exception:
      pass
  if price_max:
    try:
      products = products.filter(price__lte=Decimal(price_max.replace(',', '')))
    except Exception:
      pass

  if stock == 'available':
    products = products.filter(stock__gt=0)
  elif stock == 'out_of_stock':
    products = products.filter(stock__lte=0)

  if warranty:
    products = products.filter(warranty=True)
  if after_sales:
    products = products.filter(after_sales=True)
  if fast_delivery:
    products = products.filter(fast_delivery=True)
  if installation:
    products = products.filter(installation_training=True)

  sort_map = {
    'newest': '-created_at',
    'best_selling': '-sold_count',
    'cheapest': 'price',
    'expensive': '-price',
  }
  products = products.order_by(sort_map.get(sort, '-created_at'))

  paginator = Paginator(products, 12)
  try:
    page_obj = paginator.page(page)
  except (PageNotAnInteger, EmptyPage):
    page_obj = paginator.page(1)

  base_query = request.GET.copy()
  base_query.pop('page', None)
  base_query_string = base_query.urlencode()

  category_query = request.GET.copy()
  category_query.pop('category', None)
  category_query.pop('page', None)
  category_query_string = category_query.urlencode()

  context = {
    'products': page_obj,
    'page_obj': page_obj,
    'page_numbers': _get_pagination_range(page_obj),
    'base_query': base_query_string,
    'category_query': category_query_string,
    'categories': categories,
    'brands': brands,
    'selected_category': selected_category,
    'selected_brands': selected_brands,
    'price_min': price_min,
    'price_max': price_max,
    'stock': stock,
    'warranty': warranty,
    'after_sales': after_sales,
    'fast_delivery': fast_delivery,
    'installation': installation,
    'sort': sort,
  }
  return render(request=request, template_name='shop.html', context=context)

def about_view(request):
  return render(request=request, template_name='darabarema.html')

def blog_view(request):
  posts = BlogPost.objects.select_related('author').order_by('-created_at')
  return render(request=request, template_name='weblog.html', context={'posts': posts})


def product_detail_view(request, product_id):
  product = get_object_or_404(
    Product.objects.select_related('brand', 'category'),
    pk=product_id,
    is_active=True,
  )
  return render(request=request, template_name='tkmhsul.html', context={'product': product})

# def t_view(request):
#   return render(request=request, template_name='shop.html')
# def shop_view(request):
#   return render(request=request, template_name='shop.html')
