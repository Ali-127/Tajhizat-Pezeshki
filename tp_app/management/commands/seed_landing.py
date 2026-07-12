import os
import shutil

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from users.models import User
from tp_app.models import BlogCategory, Brand, Category, Product, BlogPost



class Command(BaseCommand):
    help = 'Seed data for landing page and shop page: brands, categories, products, blog posts and a demo user.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding landing page and shop data...')

        user, _ = User.objects.get_or_create(
            phone_number='09123456789',
            defaults={'full_name': 'ادمین نمونه', 'email': 'admin@example.com'},
        )
        if not user.has_usable_password():
            user.set_password('password123')
            user.save()

        brands = {
            'WBH': {'slug': 'wbh'},
            'Castellini': {'slug': 'castellini'},
            'Mindray': {'slug': 'mindray'},
            'Acteon': {'slug': 'acteon'},
            'Yuwell': {'slug': 'yuwell'},
            'Woodpecker': {'slug': 'woodpecker'},
            'Labomed': {'slug': 'labomed'},
            'Contec': {'slug': 'contec'},
            'NSK': {'slug': 'nsk'},
            'Labogene': {'slug': 'labogene'},
        }
        categories = {
            'تجهیزات دندانپزشکی': {'slug': 'dental-equipment'},
            'تجهیزات پزشکی': {'slug': 'medical-equipment'},
            'تجهیزات آزمایشگاهی': {'slug': 'lab-equipment'},
            'تصویربرداری': {'slug': 'imaging-equipment'},
            'تجهیزات مصرفی': {'slug': 'consumable-equipment'},
        }

        for name, data in brands.items():
            Brand.objects.get_or_create(name=name, defaults={'slug': data['slug']})

        for name, data in categories.items():
            Category.objects.get_or_create(name=name, defaults={'slug': data['slug']})

        brand_wbh = Brand.objects.get(name='WBH')
        brand_castellini = Brand.objects.get(name='Castellini')
        brand_mindray = Brand.objects.get(name='Mindray')
        brand_acteon = Brand.objects.get(name='Acteon')
        brand_yuwell = Brand.objects.get(name='Yuwell')
        brand_woodpecker = Brand.objects.get(name='Woodpecker')
        brand_labomed = Brand.objects.get(name='Labomed')
        brand_contec = Brand.objects.get(name='Contec')
        brand_nsk = Brand.objects.get(name='NSK')
        brand_labogene = Brand.objects.get(name='Labogene')

        cat_dental = Category.objects.get(name='تجهیزات دندانپزشکی')
        cat_medical = Category.objects.get(name='تجهیزات پزشکی')
        cat_lab = Category.objects.get(name='تجهیزات آزمایشگاهی')
        cat_imaging = Category.objects.get(name='تصویربرداری')
        cat_consumable = Category.objects.get(name='تجهیزات مصرفی')

        products = [
            {'name': 'یونیت دندانپزشکی S300', 'description': 'یونیت کامل همراه با صندلی، چراغ و اجزا برای کلینیک های تخصصی.', 'price': 275000000, 'stock': 8, 'sold_count': 33, 'brand': brand_castellini, 'category': cat_dental, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': True, 'image': 'unitdandan.jpeg'},
            {'name': 'اتوکلاو کلاس B3 لتری', 'description': 'اتوکلاو استاندارد با چرخه های استریل سریع و کنترل آسان.', 'price': 125000000, 'stock': 22, 'sold_count': 12, 'brand': brand_wbh, 'category': cat_dental, 'warranty': True, 'after_sales': True, 'fast_delivery': False, 'installation_training': False, 'image': 'otocluve.jpeg'},
            {'name': 'مانیتور علائم حیاتی D12', 'description': 'مانیتور علائم حیاتی با صفحه نمایش رنگی و اتصال شبکه برای بخش های بیمارستانی.', 'price': 85000000, 'stock': 15, 'sold_count': 30, 'brand': brand_mindray, 'category': cat_medical, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'manitor.jpeg'},
            {'name': 'رادیوگرافی دیواری AC70', 'description': 'سیستم رادیوگرافی با کیفیت بالا برای کلینیک های دندانپزشکی و تخصصی.', 'price': 195000000, 'stock': 4, 'sold_count': 12, 'brand': brand_acteon, 'category': cat_imaging, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': True, 'image': 'radiography.jpeg'},
            {'name': 'ساکشن جراحی لتری', 'description': 'ساکشن قدرتمند مناسب اتاق عمل با صدای کم و پمپ باکیفیت.', 'price': 25500000, 'stock': 16, 'sold_count': 27, 'brand': brand_yuwell, 'category': cat_medical, 'warranty': False, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'suctiondastgah.jpeg'},
            {'name': 'سانتریفیوژ آزمایشگاهی', 'description': 'سانتریفیوژ آزمایشگاهی با سرعت بالا و عملکرد پایدار برای نمونه های تشخیصی.', 'price': 45000000, 'stock': 11, 'sold_count': 14, 'brand': brand_labogene, 'category': cat_lab, 'warranty': True, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'azmayeshgah.jpeg'},
            {'name': 'دستگاه ECG سه کاناله', 'description': 'ای سی جی دقیق با نمایشگر پیشرفته برای تشخیص سریع و ثبت اطلاعات.', 'price': 59000000, 'stock': 20, 'sold_count': 23, 'brand': brand_contec, 'category': cat_medical, 'warranty': True, 'after_sales': True, 'fast_delivery': False, 'installation_training': False, 'image': 'dastgahECG.jpeg'},
            {'name': 'دوربین داخل دهانی', 'description': 'دوربین ثبت تصاویر داخل دهان با کیفیت بالا و نور LED قدرتمند.', 'price': 32800000, 'stock': 12, 'sold_count': 13, 'brand': brand_woodpecker, 'category': cat_dental, 'warranty': False, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'durbin dandan.jpeg'},
            {'name': 'میکروسکوپ دندانپزشکی', 'description': 'میکروسکوپ با بزرگنمایی قوی برای عمل های دندانپزشکی دقیق.', 'price': 385000000, 'stock': 5, 'sold_count': 11, 'brand': brand_labomed, 'category': cat_dental, 'warranty': True, 'after_sales': True, 'fast_delivery': False, 'installation_training': True, 'image': 'mikroskop dandani.jpeg'},
            {'name': 'ساکشن پرتابل', 'description': 'ساکشن کوچک و قابل حمل برای استفاده در مراکز درمانی و کلینیک ها.', 'price': 18500000, 'stock': 14, 'sold_count': 10, 'brand': brand_yuwell, 'category': cat_medical, 'warranty': False, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'portabl.jpeg'},
            {'name': 'الایت کیور LED', 'description': 'چراغ کیور LED با نور یکنواخت مناسب برای مواد کامپوزیت دندانپزشکی.', 'price': 9900000, 'stock': 25, 'sold_count': 9, 'brand': brand_woodpecker, 'category': cat_dental, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'cheraghled.jpeg'},
            {'name': 'محدوده دمای انکوباتور', 'description': 'انکوباتور آزمایشگاهی با کنترل دقیق دما برای نمونه های حساس.', 'price': 118000000, 'stock': 6, 'sold_count': 6, 'brand': brand_labogene, 'category': cat_lab, 'warranty': True, 'after_sales': False, 'fast_delivery': False, 'installation_training': True, 'image': 'azmayeshgah.jpeg'},
            {'name': 'یونیت دندانپزشکی کامل', 'description': 'یونیت همراه با سیستم آبی و رسانا برای چندین درمان دندانپزشکی.', 'price': 315000000, 'stock': 7, 'sold_count': 18, 'brand': brand_castellini, 'category': cat_dental, 'warranty': True, 'after_sales': True, 'fast_delivery': False, 'installation_training': True, 'image': 'unitdandan.jpeg'},
            {'name': 'شبیه‌ساز ECG قابل حمل', 'description': 'دستگاه اندازه گیری ECG همراه برای استفاده آموزشی و پرتابل.', 'price': 14500000, 'stock': 27, 'sold_count': 5, 'brand': brand_mindray, 'category': cat_medical, 'warranty': False, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'dastgahECG.jpeg'},
            {'name': 'موج نگار رادیولوژی', 'description': 'سیستم تصویربرداری محافظت شده با دقت بالا و وضوح عالی.', 'price': 422000000, 'stock': 3, 'sold_count': 8, 'brand': brand_acteon, 'category': cat_imaging, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': True, 'image': 'mri jadid.jpeg'},
            {'name': 'میکروسکوپ سلولی حرفه‌ای', 'description': 'میکروسکوپ آزمایشگاهی برای تشخیص نمونه های بافتی و سلولی.', 'price': 62000000, 'stock': 9, 'sold_count': 20, 'brand': brand_labomed, 'category': cat_lab, 'warranty': True, 'after_sales': True, 'fast_delivery': False, 'installation_training': True, 'image': 'mri.jpeg'},
            {'name': 'کیت تست مصرفی سریع', 'description': 'کیت مصرفی یکبار مصرف برای تشخیص های آزمایشگاهی سریع.', 'price': 7500000, 'stock': 58, 'sold_count': 45, 'brand': brand_wbh, 'category': cat_consumable, 'warranty': False, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'paks ekstir.jpeg'},
            {'name': 'دستگاه خنک کننده ترمومتر', 'description': 'سیستم خنک کننده برای تجهیزات آزمایشگاهی با کنترل خودکار.', 'price': 21500000, 'stock': 11, 'sold_count': 8, 'brand': brand_labogene, 'category': cat_lab, 'warranty': True, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'tabasnj.jpeg'},
            {'name': 'پک آموزش نصب تجهیزات', 'description': 'پکیج نصب و راه اندازی به همراه آموزش و خدمات پس از فروش.', 'price': 12800000, 'stock': 18, 'sold_count': 6, 'brand': brand_wbh, 'category': cat_consumable, 'warranty': True, 'after_sales': True, 'fast_delivery': False, 'installation_training': True, 'image': 'main-img.jpeg'},
            {'name': 'دستگاه ساکشن رومیزی', 'description': 'ساکشن رومیزی با صدای کم و کارکرد یکپارچه برای اتاق عمل.', 'price': 22500000, 'stock': 21, 'sold_count': 16, 'brand': brand_yuwell, 'category': cat_medical, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'suction.jpeg'},
            {'name': 'روکش محافظ یکبار مصرف', 'description': 'روکش محافظ مناسب برای تجهیزات دندانپزشکی و پزشکی.', 'price': 5800000, 'stock': 34, 'sold_count': 22, 'brand': brand_wbh, 'category': cat_consumable, 'warranty': False, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'tak3.jpeg'},
            {'name': 'مجموعه ابزار ایمپلنت', 'description': 'مجموعه ابزار کامل برای انجام ایمپلنت دندانپزشکی با کیفیت بالا.', 'price': 31000000, 'stock': 12, 'sold_count': 19, 'brand': brand_nsk, 'category': cat_dental, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': False, 'image': 'motor implant.jpeg'},
            {'name': 'سنسور RVG دیجیتال', 'description': 'سنسور تصویربرداری دیجیتال RVG با کیفیت بالا و نویز کم.', 'price': 98000000, 'stock': 10, 'sold_count': 11, 'brand': brand_acteon, 'category': cat_imaging, 'warranty': True, 'after_sales': True, 'fast_delivery': True, 'installation_training': True, 'image': 'radiography.jpeg'},
            {'name': 'پک لوازم مصرفی دندانپزشکی', 'description': 'پکیج لوازم مصرفی برای یونیت و استریل دندانپزشکی.', 'price': 16400000, 'stock': 29, 'sold_count': 17, 'brand': brand_wbh, 'category': cat_consumable, 'warranty': False, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'tak4.jpeg'},
            {'name': 'نوار تست خون سریع', 'description': 'نوار تست تشخیص سریع مناسب آزمایشگاه های ابتدایی.', 'price': 9100000, 'stock': 41, 'sold_count': 28, 'brand': brand_labogene, 'category': cat_lab, 'warranty': False, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'paks ekstir.jpeg'},
            {'name': 'امولوسیون ضدعفونی کننده', 'description': 'محصول مصرفی برای استریل و ضدعفونی محیط آزمایشگاه و کلینیک.', 'price': 6200000, 'stock': 49, 'sold_count': 14, 'brand': brand_wbh, 'category': cat_consumable, 'warranty': False, 'after_sales': False, 'fast_delivery': True, 'installation_training': False, 'image': 'paks ekstir.jpeg'},
        ]

        static_media_dir = os.path.join(settings.BASE_DIR, 'static', 'media')
        product_pics_dir = os.path.join(settings.MEDIA_ROOT, 'product-pics')
        os.makedirs(product_pics_dir, exist_ok=True)

        for item in products:
            image_name = item.get('image')
            image_value = None
            if image_name:
                source_image_path = os.path.join(static_media_dir, image_name)
                target_image_path = os.path.join(product_pics_dir, image_name)
                if os.path.exists(source_image_path) and not os.path.exists(target_image_path):
                    shutil.copyfile(source_image_path, target_image_path)
                image_value = os.path.join('product-pics', image_name)

            Product.objects.update_or_create(
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'price': item['price'],
                    'stock': item['stock'],
                    'sold_count': item['sold_count'],
                    'warranty': item['warranty'],
                    'after_sales': item['after_sales'],
                    'fast_delivery': item['fast_delivery'],
                    'installation_training': item['installation_training'],
                    'brand': item['brand'],
                    'category': item['category'],
                    'image': image_value,
                    'is_active': True,
                },
            )

        blog_categories = {
            'مانیتورینگ': BlogCategory.objects.get_or_create(name='مانیتورینگ', defaults={'slug': 'monitoring'})[0],
            'دندانپزشکی': BlogCategory.objects.get_or_create(name='دندانپزشکی', defaults={'slug': 'dentistry'})[0],
            'آزمایشگاهی': BlogCategory.objects.get_or_create(name='آزمایشگاهی', defaults={'slug': 'laboratory'})[0],
        }

        posts = [
            {
                'title': 'راهنمای انتخاب مانیتور علائم حیاتی',
                'content': 'در این مقاله به بررسی نکاتی می‌پردازیم که قبل از خرید مانیتور علائم حیاتی باید بدانید...',
                'category': blog_categories['مانیتورینگ'],
            },
            {
                'title': 'چگونه یونیت دندانپزشکی مناسب کلینیک خود را انتخاب کنیم؟',
                'content': 'انتخاب یونیت مناسب نیازمند توجه به ergonomics، امکانات و خدمات پس از فروش است...',
                'category': blog_categories['دندانپزشکی'],
            },
            {
                'title': 'تجهیزات آزمایشگاهی استاندارد برای آزمایشگاه‌های تشخیص',
                'content': 'در این متن، مهم‌ترین تجهیزات آزمایشگاهی و معیارهای استانداردسازی آن‌ها بررسی می‌شود...',
                'category': blog_categories['آزمایشگاهی'],
            },
        ]

        for item in posts:
            BlogPost.objects.get_or_create(
                title=item['title'],
                defaults={
                    'content': item['content'],
                    'author': user,
                    'blog_category': item['category'],
                    'created_at': timezone.now(),
                },
            )

        self.stdout.write(self.style.SUCCESS('Landing page and shop data seeded successfully.'))
