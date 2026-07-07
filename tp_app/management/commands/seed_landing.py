from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from tp_app.models import Brand, Category, Product, BlogPost


class Command(BaseCommand):
    help = 'Seed data for landing page: brands, categories, products, blog posts and a demo user.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding landing page data...')

        user, _ = User.objects.get_or_create(
            phone_number='09123456789',
            defaults={'full_name': 'ادمین نمونه', 'email': 'admin@example.com'},
        )
        if not user.has_usable_password():
            user.set_password('password123')
            user.save()

        brands = {
            'MedTech': {'slug': 'medtech'},
            'DentaPlus': {'slug': 'dentaplus'},
            'LabCare': {'slug': 'labcare'},
        }
        categories = {
            'تجهیزات پزشکی': {'slug': 'medical-equipment'},
            'تجهیزات دندانپزشکی': {'slug': 'dental-equipment'},
            'تجهیزات آزمایشگاهی': {'slug': 'lab-equipment'},
        }

        for name, data in brands.items():
            Brand.objects.get_or_create(name=name, defaults={'slug': data['slug']})

        for name, data in categories.items():
            Category.objects.get_or_create(name=name, defaults={'slug': data['slug']})

        brand_medtech = Brand.objects.get(name='MedTech')
        brand_denta = Brand.objects.get(name='DentaPlus')
        brand_lab = Brand.objects.get(name='LabCare')
        cat_medical = Category.objects.get(name='تجهیزات پزشکی')
        cat_dental = Category.objects.get(name='تجهیزات دندانپزشکی')
        cat_lab = Category.objects.get(name='تجهیزات آزمایشگاهی')

        products = [
            {
                'name': 'مانیتور علائم حیاتی مدل X100',
                'description': 'مانیتور کامل علائم حیاتی برای بخش مراقبت‌های ویژه با نمایشگر لمسی.',
                'price': 12890000,
                'stock': 30,
                'brand': brand_medtech,
                'category': cat_medical,
                'is_active': True,
            },
            {
                'name': 'یونیت دندانپزشکی حرفه‌ای V20',
                'description': 'یونیت مدرن شامل نور LED، موتور توربین و صندلی راحت برای کلینیک.',
                'price': 28990000,
                'stock': 18,
                'brand': brand_denta,
                'category': cat_dental,
                'is_active': True,
            },
            {
                'name': 'سانتریفیوژ آزمایشگاهی مدل L6',
                'description': 'سانتریفیوژ مناسب آزمایشگاه‌های تشخیصی با سرعت بالا و کم صدا.',
                'price': 9800000,
                'stock': 12,
                'brand': brand_lab,
                'category': cat_lab,
                'is_active': True,
            },
            {
                'name': 'اتوکلاو دندانپزشکی کوچک',
                'description': 'اتوکلاو جمع‌وجور برای استریل ابزارهای دندانپزشکی با ایمنی بالا.',
                'price': 7450000,
                'stock': 9,
                'brand': brand_denta,
                'category': cat_dental,
                'is_active': True,
            },
            {
                'name': 'دستگاه ساکشن بیمارستانی S2',
                'description': 'ساکشن پرقدرت برای اتاق عمل و درمانگاه با صدای کم.',
                'price': 4590000,
                'stock': 24,
                'brand': brand_medtech,
                'category': cat_medical,
                'is_active': True,
            },
        ]

        for item in products:
            Product.objects.get_or_create(
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'price': item['price'],
                    'stock': item['stock'],
                    'brand': item['brand'],
                    'category': item['category'],
                    'is_active': item['is_active'],
                },
            )

        posts = [
            {
                'title': 'راهنمای انتخاب مانیتور علائم حیاتی',
                'content': 'در این مقاله به بررسی نکاتی می‌پردازیم که قبل از خرید مانیتور علائم حیاتی باید بدانید...',
            },
            {
                'title': 'چگونه یونیت دندانپزشکی مناسب کلینیک خود را انتخاب کنیم؟',
                'content': 'انتخاب یونیت مناسب نیازمند توجه به ergonomics، امکانات و خدمات پس از فروش است...',
            },
            {
                'title': 'تجهیزات آزمایشگاهی استاندارد برای آزمایشگاه‌های تشخیص',
                'content': 'در این متن، مهم‌ترین تجهیزات آزمایشگاهی و معیارهای استانداردسازی آن‌ها بررسی می‌شود...',
            },
        ]

        for item in posts:
            BlogPost.objects.get_or_create(
                title=item['title'],
                defaults={
                    'content': item['content'],
                    'author': user,
                    'created_at': timezone.now(),
                },
            )

        self.stdout.write(self.style.SUCCESS('Landing page data seeded successfully.'))
