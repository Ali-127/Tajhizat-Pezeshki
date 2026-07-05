from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


# 1. USER & Authentication
# custom user manager in order to replace username with phone number verification
class CustomUserManager(BaseUserManager):
  def create_user(self, phone_number, full_name, password=None, **extra_fields):
    
    if not phone_number:
      raise ValueError("The phone number field must be set")
    
    extra_fields.setdefault('is_active', True)
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)

    user = self.model(phone_number=phone_number, full_name=full_name, **extra_fields)

    if password:
      user.set_password(password)
    else:
      user.set_unusable_password()

    user.save(using=self._db)

    return user
  
  def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_active', True)

    if extra_fields.get("is_staff") is not True:
      raise ValueError("Superuser must have is_staff=True")

    if extra_fields.get("is_superuser") is not True:
      raise ValueError("Superuser must have is_superuser=True")

    

    if not password:
      raise ValueError("Superuser must have a password")
    

    user = self.create_user(
      phone_number=phone_number,
      full_name=full_name,
      password=password,
      **extra_fields)
    
    return user



# User
class User(AbstractUser):
  # Remove default username column
  username = None

  # Use full name instead of first and last name
  full_name = models.CharField(max_length=150, blank=False)

  phone_number = models.CharField(max_length=20, unique=True, blank=False)

  # email is optional. we'll use phone number as main login method
  email = models.EmailField(unique=True, blank=True, null=True)

  
  objects = CustomUserManager() # type: ignore

  # Using phone number for authentication
  USERNAME_FIELD = 'phone_number'
  REQUIRED_FIELDS = ['full_name']

  def __str__(self) -> str:
    return f'{self.full_name} ({self.phone_number})'

# Address
class Address(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
  street_address = models.CharField(max_length=255)
  city = models.CharField(max_length=100)
  is_default = models.BooleanField(default=False)

  def __str__(self) -> str:
    return f"{self.street_address}, {self.city}"
  
# OTPToken
class OTPToken(models.Model):
  phone_number = models.CharField(max_length=15)
  otp_code = models.CharField(max_length=6)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return f"{self.phone_number} - {self.otp_code}"

# ---------------------------------------------------

# 2. Core(Product, Brand, Category)
# category
class Category(models.Model):
  name = models.CharField(max_length=50, unique=True)
  slug = models.SlugField(max_length=50, unique=True)

  class Meta:
    verbose_name_plural = "Categories"

  def __str__(self) -> str:
    return self.name

# brands
class Brand(models.Model):
  name = models.CharField(max_length=50, unique=True)
  slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)

  def __str__(self) -> str:
    return self.name

  
# product
class Product(models.Model):
 name = models.CharField(max_length=50, blank=False)
 description = models.TextField(max_length=250)
 price = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False)
 image = models.ImageField(
   upload_to='product-pics/',
   blank=True,
   null=True,
 )
 stock = models.PositiveIntegerField(default=0)
 category = models.ForeignKey(
   Category,
   on_delete=models.PROTECT,
   related_name='products',
 )

 brand = models.ForeignKey(
   Brand,
   on_delete=models.PROTECT,
   related_name='products'
 )

 created_at = models.DateTimeField(auto_now_add=True)
 is_active = models.BooleanField(default=True)

 def __str__(self) -> str:
   return self.name

# -------------------------------------------------------------


# 3. Interaction(Cart, Favorites)
# Cart
class Cart(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return f"Cart for {self.user.full_name}"


# Cart item
class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

  product = models.ForeignKey('Product', on_delete=models.CASCADE)

  quantity = models.PositiveIntegerField(default=1)

  def __str__(self) -> str:
    return f"{self.quantity} x {self.product.name} in Cart"

# User Favorites
class Favorites(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  
  class Meta:
    unique_together = ('user', 'product')

# ------------------------------------------------------------------

# 4. Checkout(Orders, Payments)

# Order
class Order(models.Model):
  STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('PAID', 'Paid'),
    ('SHIPPED', 'Shipped'),
    ("DELIVERED", 'Delivered'),
    ("CANCELLED", "Cancelled"),
  )

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')

  address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

  total_price = models.DecimalField(max_digits=10, decimal_places=2)

  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return f"Order #{self.id} - {self.user.full_name if self.user else 'Deleted user'}" #type: ignore

# Order Item
class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
  quantity = models.PositiveIntegerField(default=1)
  price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)


# Payment
class Payment(models.Model):
  STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('SUCCESS', 'Success'),
    ('FAILED', 'Failed'),
  )
  order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
  transaction_id = models.CharField(max_length=100)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
  created_at = models.DateTimeField(auto_now_add=True)

# ---------------------------------------------

# Support & Content(Tickets, Blogs)
# Ticket
class Ticket(models.Model):
  STATUS_CHOICES = (
    ('OPEN', 'Open'),
    ('CLOSED', 'Closed'),
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
  subject = models.CharField(max_length=255)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
  created_at = models.DateTimeField(auto_now_add=True)

# # Ticket Message
class TicketMessage(models.Model):
  ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="message")
  sender = models.ForeignKey(User, on_delete=models.CASCADE)
  message = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

# Blog post
class BlogPost(models.Model):
  title = models.CharField(max_length=200)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')

  
