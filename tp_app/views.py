from decimal import Decimal

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from urllib.parse import quote

from .models import BlogCategory, BlogPost, Brand, Category, Product, Cart, CartItem, Favorites
from users.models import User


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


def dashboard_view(request):
  return render(request=request, template_name='dashboard.html')


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

  favorite_product_ids = []
  if request.user.is_authenticated:
    favorite_product_ids = list(
      request.user.favorites.values_list('product_id', flat=True)
    )

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
    'favorite_product_ids': favorite_product_ids,
  }
  return render(request=request, template_name='shop.html', context=context)

def about_view(request):
  return render(request=request, template_name='darbarema.html')

def blog_view(request):
  search_query = request.GET.get('search', '').strip()
  selected_category = request.GET.get('category', '').strip()

  posts = BlogPost.objects.select_related('author', 'blog_category').order_by('-created_at')

  if search_query:
    posts = posts.filter(
      Q(title__icontains=search_query) |
      Q(content__icontains=search_query)
    )

  if selected_category:
    posts = posts.filter(blog_category__slug=selected_category)

  categories = (
    BlogCategory.objects
    .annotate(count=Count('blog_posts'))
    .order_by('-count', 'name')
  )

  return render(
    request=request,
    template_name='weblog.html',
    context={
      'posts': posts,
      'categories': categories,
      'search_query': search_query,
      'selected_category': selected_category,
    },
  )

def blog_post_view(request, post_id):
  post = get_object_or_404(
    BlogPost.objects.select_related('author', 'blog_category'),
    pk=post_id,
  )
  return render(
    request=request,
    template_name='takweblog.html',
    context={'post': post},
  )


def product_detail_view(request, product_id):
  product = get_object_or_404(
    Product.objects.select_related('brand', 'category'),
    pk=product_id,
    is_active=True,
  )
  
  is_favorite = False
  if request.user.is_authenticated:
    is_favorite = Favorites.objects.filter(user=request.user, product=product).exists()

  return render(request=request, template_name='tkmhsul.html', context={
    'product': product,
    'is_favorite': is_favorite,
  })


def cart_view(request):
  # Show user's cart; for anonymous users show demo cart if present
  demo_phone = '09123456789'
  if request.user.is_authenticated:
    user = request.user
  else:
    user = User.objects.filter(phone_number=demo_phone).first()

  cart_items = []
  total_items_price = 0
  total_discount = 0

  if user:
    cart, _ = Cart.objects.get_or_create(user=user)
    items_qs = cart.items.select_related('product')
    for ci in items_qs:
      product = ci.product
      # convert Decimal price to int for frontend calculations
      try:
        price = int(product.price)
      except Exception:
        price = int(Decimal(product.price))
      discount = 0
      qty = ci.quantity
      original_total = price * qty
      discounted_total = int(round(original_total * (1 - discount / 100)))
      total_items_price += original_total
      total_discount += (original_total - discounted_total)
      cart_items.append({
        'id': ci.id,
        'product': product,
        'quantity': qty,
        'price': price,
        'discount': discount,
        'total': discounted_total,
      })

  final_price = total_items_price - total_discount

  context = {
    'cart_items': cart_items,
    'total_items_price': total_items_price,
    'total_discount': total_discount,
    'final_price': final_price,
  }
  return render(request=request, template_name='sabadkharid.html', context=context)


def add_to_cart_view(request, product_id):
  product = get_object_or_404(Product, pk=product_id, is_active=True)
  qty = 1
  try:
    qty = int(request.GET.get('qty', 1))
  except Exception:
    qty = 1

  if not request.user.is_authenticated:
    # Redirect to auth page and preserve the add URL so after login it will add
    add_path = request.get_full_path()
    return redirect(f"{reverse('auth')}?next={quote(add_path)}")

  cart, _ = Cart.objects.get_or_create(user=request.user)
  ci, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': qty})
  if not created:
    ci.quantity = min(99, ci.quantity + qty)
    ci.save()

  return redirect('cart')


def toggle_favorite_view(request, product_id):
  product = get_object_or_404(Product, pk=product_id, is_active=True)
  if not request.user.is_authenticated:
    next_path = request.get_full_path()
    return redirect(f"{reverse('auth')}?next={quote(next_path)}")

  fav, created = Favorites.objects.get_or_create(user=request.user, product=product)
  if not created:
    fav.delete()

  # redirect back to referer or product detail
  referer = request.META.get('HTTP_REFERER')
  if referer:
    return redirect(referer)
  return redirect('product_detail', product_id=product.id)

# def t_view(request):
#   return render(request=request, template_name='shop.html')
# def shop_view(request):
#   return render(request=request, template_name='shop.html')
