from django.db import models

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




