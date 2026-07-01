from decimal import Decimal
from pathlib import Path
import shutil

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from catalog.models import Brand, Category, Product
from orders.models import Order, OrderItem


SOURCE_DIR = Path(r"C:\Users\user\Downloads\Telegram Desktop")


PRODUCTS = [
    {
        "brand": "Dr. Spiller",
        "name": "Retinol+ Serum",
        "subtitle": "Відновлювальна сироватка з ретинолом. 30 мл. Ціна 4635 грн / 90 євро.",
        "description": (
            "Інноваційна сироватка поєднує інкапсульований ретинол з активними компонентами, "
            "які працюють зі шкірою, що вже має ознаки вікових змін. Синергія інгредієнтів "
            "зменшує вираженість зморщок, покращує текстуру, вирівнює рельєф і тон шкіри. "
            "Регулює діяльність сальних залоз, нормалізує склад себуму, має протизапальну дію. "
            "Інкапсульована форма ретинолу нормалізує процеси кератинізації, усуває гіперкератоз, "
            "покращує структуру шкіри та бореться з фотостарінням. Сприяє синтезу якісного колагену "
            "й еластину. Поєднання ретинолу із заспокійливими інгредієнтами мінімізує ризик подразнення, "
            "що робить її придатною навіть для чутливої шкіри. Тон, рельєф і пружність шкіри покращуються, "
            "обличчя набуває гладкого й рівного вигляду.\n\n"
            "Склад: ретинол, пальмітоїл трипептид-5, гіалуронова кислота, комплекс PoreRefine "
            "(агарицинова кислота), екстракт лілії, ніацинамід, пантенол, комплекс MatriFirm, "
            "гідролат лаванди. Не містить ліпідів."
        ),
        "price": "4635.00",
        "image": "photo_2026-07-01_15-03-22.jpg",
        "quantity": 2,
    },
    {
        "brand": "Bioline Jatò",
        "name": "Daily Ritual Pure Gel Cleansing",
        "subtitle": "Гель для вмивання для жирної та комбінованої шкіри. Ціна 1728 грн / 34 євро.",
        "description": (
            "Гель очищає шкіру від надлишків шкірного сала та зберігає водно-жирову мантію шкіри, "
            "не руйнуючи цілісності рогового шару. Рекомендується для жирної, комбінованої та "
            "проблемної шкіри, при вугровій хворобі.\n\n"
            "Склад: коко-глікозид, лаурил глікозид, ксантан, фруктові олігосахариди, екстракт білої "
            "верби, фруктові кислоти, ніацинамід."
        ),
        "price": "1728.00",
        "image": "photo_2026-07-01_15-03-07.jpg",
        "quantity": 3,
    },
    {
        "brand": "GlyMed+",
        "name": "Blemish Control No. 5 with Benzoyl Peroxide",
        "subtitle": "Лосьйон з 5% бензоїл пероксидом. 30 мл. Ціна 1088 грн / 21 євро.",
        "description": (
            "Лосьйон з 5% бензоїлпероксидом - це ефективний засіб проти елементів акне, особливо "
            "запальних. Може використовуватися при захворюванні будь-якого ступеня тяжкості. Має "
            "потужну антибактеріальну та протизапальну дію, пришвидшує загоєння.\n\n"
            "Склад: бензоїлпероксид 5%, алое вера, лаванда, чайне дерево."
        ),
        "price": "1088.00",
        "image": "photo_2026-07-01_15-03-16.jpg",
        "quantity": 4,
    },
    {
        "brand": "GlyMed+",
        "name": "Skin Clarifying Masque",
        "subtitle": "Себорегулювальна очищувальна маска з ензимами. 30 мл. Ціна 1671 грн / 32 євро.",
        "description": (
            "Ефективний засіб для очищення та детоксу шкіри. Завдяки комплексному складу відбувається "
            "себорегуляція, м'яка ексфоліація з наступним зволоженням та відновленням шкіри.\n\n"
            "Склад: папаїн, бромелаїн, лемонграс, бентоніт, лаванда, календула, гіалуронова кислота."
        ),
        "price": "1671.00",
        "image": "photo_2026-07-01_15-03-12.jpg",
        "quantity": 2,
    },
    {
        "brand": "Alissa Beauté",
        "name": "ESSENTIAL Tonic Gel",
        "subtitle": "Тонер-гель для зневодненої шкіри. 200 мл. Ціна 1302 грн / 26 євро.",
        "description": (
            "Зволожує, заспокоює та освіжає шкіру.\n\n"
            "Склад: сечовина, гіалуронова кислота, комплекс вітамінів (B3/PP, B5, B6), стабільна "
            "форма вітаміну C, вітамін E, гідролат гамамелісу, сахариди."
        ),
        "price": "1302.00",
        "image": "photo_2026-07-01_15-03-19.jpg",
        "quantity": 5,
    },
    {
        "brand": "Dr. Spiller",
        "name": "Fresh & Fruit® Moisturizing Mask",
        "subtitle": "Зволожувальна гель-маска з екстрактами фруктів. 50 мл. Ціна 2363 грн / 45,60 євро.",
        "description": (
            "Охолоджувальна гелева маска з фруктовими екстрактами - фаворит літнього догляду для всіх "
            "типів шкіри. Освіжає, бадьорить, глибоко зволожує та повертає сяйво навіть тьмяній і "
            "втомленій шкірі. Має легку гелеву текстуру без ліпідів і тропічний аромат, що піднімає "
            "настрій і дарує відчуття відпустки незалежно від погоди. Фруктовий комплекс (ананас, "
            "манго, папая) стимулює оновлення, делікатно відлущує, вирівнює тон і текстуру, активізує "
            "клітинну активність. Пантенол знімає подразнення, заспокоює, зменшує чутливість і сприяє "
            "відновленню шкіри після стресу.\n\n"
            "Склад: екстракти ананасу, манго, папаї, пантенол. Не містить ліпідів."
        ),
        "price": "2363.00",
        "image": "photo_2026-07-01_15-10-44.jpg",
        "quantity": 2,
    },
]


class Command(BaseCommand):
    help = "Seed portfolio catalog products and owner demo orders."

    def handle(self, *args, **options):
        category, _ = Category.objects.get_or_create(
            slug="professional-skincare",
            defaults={"name": "Professional Skincare"},
        )
        media_dir = Path("media/products/portfolio")
        media_dir.mkdir(parents=True, exist_ok=True)

        products = []
        Product.objects.all().delete()

        for item in PRODUCTS:
            brand_slug = slugify(item["brand"], allow_unicode=True)
            brand, _ = Brand.objects.get_or_create(
                slug=brand_slug,
                defaults={"name": item["brand"]},
            )
            source = SOURCE_DIR / item["image"]
            target_name = f"{slugify(item['name'], allow_unicode=True)}.jpg"
            target = media_dir / target_name
            if source.exists():
                shutil.copyfile(source, target)

            description = f"{item['subtitle']}\n\n{item['description']}"
            product = Product.objects.create(
                category=category,
                brand=brand,
                name=item["name"],
                slug=slugify(item["name"], allow_unicode=True),
                description=description,
                price=Decimal(item["price"]),
                image=f"products/portfolio/{target_name}" if target.exists() else "",
                stock=24,
                is_available=True,
            )
            products.append((product, item["quantity"]))

        Order.objects.all().delete()
        user, _ = User.objects.get_or_create(
            username="portfolio_customer",
            defaults={
                "email": "client@example.com",
                "first_name": "Client",
                "last_name": "Demo",
                "is_active": True,
            },
        )

        first_order = Order.objects.create(
            user=user,
            first_name="Client",
            last_name="Demo",
            email="client@example.com",
            phone="+380501112233",
            address="Beauty Street 12",
            city="Kyiv",
            postal_code="01001",
            total_price=Decimal("0.00"),
        )
        second_order = Order.objects.create(
            user=user,
            first_name="Anna",
            last_name="Care",
            email="anna@example.com",
            phone="+380671234567",
            address="Skin Avenue 5",
            city="Lviv",
            postal_code="79000",
            total_price=Decimal("0.00"),
        )

        for index, (product, quantity) in enumerate(products):
            order = first_order if index < 3 else second_order
            OrderItem.objects.create(
                order=order,
                product=product,
                name=product.name,
                price=product.price,
                quantity=quantity,
            )

        for order in (first_order, second_order):
            order.total_price = sum(
                (item.total for item in order.items.all()),
                Decimal("0.00"),
            )
            order.save(update_fields=["total_price"])

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(products)} portfolio products."))
