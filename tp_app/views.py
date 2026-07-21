from decimal import Decimal

from django.contrib.auth import logout
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_POST
from urllib.parse import quote

from .models import BlogCategory, BlogPost, Brand, Category, Product, Cart, CartItem, Favorites
from .models import Order, OrderItem, Ticket, TicketMessage
from users.models import User, Address


def landing_view(request):
  active_products = Product.objects.filter(is_active=True).select_related('brand', 'category')
  context = {
    'special_products': active_products.order_by('-stock', '-created_at')[:5],
    'latest_products': active_products.order_by('-created_at')[:5],
    'latest_posts': BlogPost.objects.select_related('author').order_by('-created_at')[:3],
  }
  return render(request, 'landing.html', context)


def dashboard_view(request):
  if not request.user.is_authenticated:
    return redirect('auth')

  user = request.user
  now = timezone.now()

  # Stats
  total_orders = user.orders.count()
  active_orders_count = user.orders.filter(status__in=['PENDING', 'PAID', 'SHIPPED']).count()
  open_tickets_count = user.tickets.filter(status='OPEN').count()
  favorites_count = user.favorites.count()

  # Recent orders
  recent_orders = user.orders.select_related('payment').prefetch_related('items__product').order_by('-created_at')[:4]

  # Recent tickets
  recent_tickets = user.tickets.order_by('-created_at')[:3]

  # Recent favorites
  recent_favorites = user.favorites.select_related('product__brand', 'product__category').order_by('-id')[:4]
  recent_fav_products = [f.product for f in recent_favorites]

  # Orders page
  all_orders = user.orders.select_related('payment').prefetch_related('items__product').order_by('-created_at')

  # Tickets page
  all_tickets = user.tickets.order_by('-created_at')

  # Favorites page
  favorite_product_ids = list(user.favorites.values_list('product_id', flat=True))
  fav_products = Product.objects.filter(pk__in=favorite_product_ids).select_related('brand', 'category')

  # Addresses
  addresses = user.addresses.all()

  # New orders since last visit
  last_login = user.last_login or now
  new_orders_count = user.orders.filter(created_at__gte=last_login).count()

  context = {
    'user': user,
    'total_orders': total_orders,
    'active_orders': active_orders_count,
    'open_tickets': open_tickets_count,
    'favorites_count': favorites_count,
    'recent_orders': recent_orders,
    'recent_tickets': recent_tickets,
    'recent_fav_products': recent_fav_products,
    'all_orders': all_orders,
    'all_tickets': all_tickets,
    'fav_products': fav_products,
    'favorite_product_ids': favorite_product_ids,
    'addresses': addresses,
    'new_orders_count': new_orders_count,
  }
  return render(request, 'dashboard.html', context)


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

  filters = {
    'stock__gt': 0 if stock == 'available' else None,
    'stock__lte': 0 if stock == 'out_of_stock' else None,
    'warranty': True if warranty else None,
    'after_sales': True if after_sales else None,
    'fast_delivery': True if fast_delivery else None,
    'installation_training': True if installation else None,
  }
  products = products.filter(**{k: v for k, v in filters.items() if v is not None})

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
  return render(request, 'shop.html', context)

def about_view(request):
  return render(request, 'darbarema.html')

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

  return render(request, 'weblog.html', {
    'posts': posts,
    'categories': categories,
    'search_query': search_query,
    'selected_category': selected_category,
  })

def blog_post_view(request, post_id):
  post = get_object_or_404(
    BlogPost.objects.select_related('author', 'blog_category'),
    pk=post_id,
  )
  return render(request, 'takweblog.html', {'post': post})


def product_detail_view(request, product_id):
  product = get_object_or_404(
    Product.objects.select_related('brand', 'category'),
    pk=product_id,
    is_active=True,
  )
  
  is_favorite = request.user.is_authenticated and request.user.favorites.filter(product=product).exists()

  return render(request, 'tkmhsul.html', {'product': product, 'is_favorite': is_favorite})


def cart_view(request):
  # Show user's cart; for anonymous users show demo cart if present
  demo_phone = '09123456789'
  if request.user.is_authenticated:
    user = request.user
  else:
    user = User.objects.filter(phone_number=demo_phone).first()

  cart_items = []
  total_price = 0

  if user:
    cart, _ = Cart.objects.get_or_create(user=user)
    for ci in cart.items.select_related('product'):
      price = int(ci.product.price)
      qty = ci.quantity
      item_total = price * qty
      total_price += item_total
      cart_items.append({
        'id': ci.id,
        'product': ci.product,
        'quantity': qty,
        'price': price,
        'total': item_total,
      })

  context = {
    'cart_items': cart_items,
    'total_items_price': total_price,
    'total_discount': 0,
    'final_price': total_price,
  }
  return render(request, 'sabadkharid.html', context)


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

def favorites_view(request):
  if not request.user.is_authenticated:
    next_path = request.get_full_path()
    return redirect(f"{reverse('auth')}?next={quote(next_path)}")

  favorite_product_ids = list(request.user.favorites.values_list('product_id', flat=True))
  products = Product.objects.filter(pk__in=favorite_product_ids).select_related('brand', 'category')

  page = request.GET.get('page', 1)
  paginator = Paginator(products, 12)
  try:
    page_obj = paginator.page(page)
  except (PageNotAnInteger, EmptyPage):
    page_obj = paginator.page(1)

  context = {
    'page_obj': page_obj,
    'page_numbers': _get_pagination_range(page_obj),
    'favorite_product_ids': favorite_product_ids,
  }
  return render(request, 'favorites.html', context)


# ── Dashboard action views ──

def _dashboard_redirect(section=None):
    url = reverse('dashboard')
    if section:
        url += f'#{section}'
    return redirect(url)


@require_POST
def dashboard_profile_update_view(request):
    if not request.user.is_authenticated:
        return redirect('auth')

    user = request.user
    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()

    if full_name:
        user.full_name = full_name
    if email:
        user.email = email
    user.save(update_fields=['full_name', 'email'])

    return _dashboard_redirect('profile')


@require_POST
def dashboard_address_add_view(request):
    if not request.user.is_authenticated:
        return redirect('auth')

    street = request.POST.get('street_address', '').strip()
    city = request.POST.get('city', '').strip()

    if street and city:
        Address.objects.create(
            user=request.user,
            street_address=street,
            city=city,
        )

    return _dashboard_redirect('addresses')


@require_POST
def dashboard_address_delete_view(request, address_id):
    if not request.user.is_authenticated:
        return redirect('auth')

    addr = get_object_or_404(Address, pk=address_id, user=request.user)
    addr.delete()

    return _dashboard_redirect('addresses')


@require_POST
def dashboard_create_ticket_view(request):
    if not request.user.is_authenticated:
        return redirect('auth')

    subject = request.POST.get('subject', '').strip()
    message_text = request.POST.get('message', '').strip()

    if subject and message_text:
        ticket = Ticket.objects.create(user=request.user, subject=subject)
        TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message_text,
        )

    return _dashboard_redirect('tickets')


@require_POST
def dashboard_add_to_cart_view(request, product_id):
    if not request.user.is_authenticated:
        return redirect('auth')

    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    ci, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})
    if not created:
        ci.quantity = min(99, ci.quantity + 1)
        ci.save()

    return redirect('cart')


@require_POST
def dashboard_remove_favorite_view(request, product_id):
    if not request.user.is_authenticated:
        return redirect('auth')

    product = get_object_or_404(Product, pk=product_id)
    Favorites.objects.filter(user=request.user, product=product).delete()

    return _dashboard_redirect('favorites')