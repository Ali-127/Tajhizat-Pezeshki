from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

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

