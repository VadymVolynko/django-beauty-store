"""
Management command: python manage.py populate_db
Seeds the real portfolio catalog (brands, products, service, specialist)
shown in the project's README/screenshots, using the real images committed
under media/brands/, media/products/portfolio/ and
media/specialists/gallery/, so every deploy's storefront matches the
documented design instead of generic placeholder data.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from booking.models import Service, Specialist, SpecialistPhoto
from catalog.models import Brand, Category, Product

CATEGORIES = ["Skincare", "Makeup", "Haircare", "Perfumery"]

# (slug, name, description_uk, description_en, image)
BRANDS = [
    (
        "dr-spiller", "Dr. Spiller",
        "Професійна косметика німецького бренду Dr. Spiller з доказаною "
        "клінічною ефективністю, заснована на натуральних органічних "
        "інгредієнтах і екстрактах рослин.",
        "Professional cosmetics from the German brand Dr. Spiller with "
        "proven clinical efficacy, based on natural organic ingredients "
        "and plant extracts.",
        "brands/Dr._Spiller.jpg",
    ),
    (
        "alissa-beaute", "Alissa Beauté",
        "Італійський бренд дерматокосметики з до 98% натуральних "
        "інгредієнтів. Легкі текстури, органічні масла й екстракти дарують "
        "шкірі комфорт у ритмі міста. Ключова перевага — інноваційні "
        "пептиди з вираженим anti-age ефектом. Alissa Beauté поєднує "
        "природу та науку, створюючи професійний догляд, який робить красу "
        "помітною щодня.",
        "An Italian dermocosmetics brand with up to 98% natural "
        "ingredients. Light textures, organic oils and extracts give skin "
        "comfort in the rhythm of city life. The key advantage is "
        "innovative peptides with a pronounced anti-age effect. Alissa "
        "Beauté combines nature and science to create professional care "
        "that makes beauty visible every day.",
        "brands/Alissa_Beauté.jpg",
    ),
    (
        "glymed-plus", "GlyMed Plus",
        "Бренд професійної космецевтики із США, один із лідерів по "
        "лікуванню акне і розацеа.",
        "A professional cosmeceutical brand from the USA, one of the "
        "leaders in acne and rosacea treatment.",
        "brands/GlyMed_Plus.jpg",
    ),
    (
        "me-line", "ME Line",
        "Лінійка Me Line – унікальна розробка іспанської компанії "
        "Innoaesthetics, препарати призначені для лікування пігментних "
        "плям будь-якого генезу, для всіх типів шкіри, для обличчя та "
        "тіла.",
        "The Me Line range is a unique development by the Spanish company "
        "Innoaesthetics, with formulas designed to treat pigment spots of "
        "any origin, for all skin types, face and body.",
        "brands/ME_Line.jpg",
    ),
    (
        "bioline-jato", "Bioline Jato",
        "Італійський преміум-бренд професійної косметики, що поєднує "
        "науку та природу для створення ефективних засобів догляду за "
        "шкірою обличчя та тіла.",
        "An Italian premium professional cosmetics brand that combines "
        "science and nature to create effective face and body skincare "
        "products.",
        "brands/Bioline_Jato.jpg",
    ),
    (
        "dermaquest", "DermaQuest",
        "Преміальний американський бренд професійної космецевтики, "
        "заснований у 1999 році біохіміком Семом Дхаттом, який створював "
        "формули для понад 700 світових брендів. Косметика спеціалізується "
        "на вирішенні складних проблем: акне, гіперпігментація, вікові "
        "зміни та розацеа.",
        "A premium American professional cosmeceutical brand founded in "
        "1999 by biochemist Sam Dhatt, who developed formulas for over "
        "700 global brands. The line specializes in addressing complex "
        "skin concerns: acne, hyperpigmentation, ageing and rosacea.",
        "brands/DermaQuest.png",
    ),
    (
        "maria-galland-paris", "Maria Galland Paris",
        "Французький преміум-бренд професійного догляду за шкірою із "
        "захоплюючою подих історією.",
        "A French premium professional skincare brand with a "
        "breathtaking history.",
        "brands/Maria_Galland_Paris.png",
    ),
    (
        "simildiet", "Simildiet",
        "Фармацевтична лабораторія, заснована у 1993 році в Сарагосі "
        "(Іспанія) лікарем-мезотерапевтом Карлосом Азнаром Санчесом. "
        "Бренд дотримується комплексного підходу до краси, створюючи "
        "власні інноваційні формули. Назва означає «дієта для шкіри» — "
        "живлення клітин цінними інгредієнтами.",
        "A pharmaceutical laboratory founded in 1993 in Zaragoza, Spain, "
        "by mesotherapy physician Carlos Aznar Sánchez. The brand takes a "
        "comprehensive approach to beauty, creating its own innovative "
        "formulas. The name means “diet for the skin” — "
        "nourishing cells with valuable ingredients.",
        "brands/Simildiet.jpg",
    ),
    (
        "trawenmoor", "TRAWENMOOR",
        "Під час розробки TRAWENMOOR, наша мета полягала в тому, щоб "
        "повністю задовольнити сучасні високі вимоги до органічної "
        "косметики та показати, що «органічний» не означає поступки у "
        "якості та ефективності, а якраз навпаки.",
        "When developing TRAWENMOOR, our goal was to fully meet today's "
        "high standards for organic cosmetics and to show that "
        "“organic” doesn't mean compromising on quality and "
        "efficacy — quite the opposite.",
        "brands/TRAWENMOOR.jpg",
    ),
]

# (slug, name, brand_slug, price, description_uk, description_en)
# image is always media/products/portfolio/<slug>.jpg
PRODUCTS = [
    (
        "daily-ritual-pure-gel-cleansing", "Daily Ritual Pure Gel Cleansing",
        "bioline-jato", "1728.00",
        "Гель для вмивання для жирної та комбінованої шкіри.\n\n"
        "Гель очищає шкіру від надлишків шкірного сала та зберігає "
        "водно-жирову мантію шкіри, не руйнуючи цілісності рогового шару. "
        "Рекомендується для жирної, комбінованої та проблемної шкіри, при "
        "вугровій хворобі.\n\n"
        "Склад: Коко-глікозид, лаурил глікозид, ксантан, фруктові "
        "олігосахариди, екстракт білої верби, фруктові кислоти, "
        "ніацинамід.",
        "Cleansing gel for oily and combination skin.\n\n"
        "The gel removes excess sebum while preserving the skin's "
        "hydrolipidic barrier without disrupting the integrity of the "
        "stratum corneum. Recommended for oily, combination and problem "
        "skin, and for acne-prone skin.\n\n"
        "Ingredients: Coco-glucoside, lauryl glucoside, xanthan gum, "
        "fruit oligosaccharides, white willow extract, fruit acids, "
        "niacinamide.",
    ),
    (
        "skin-clarifying-masque", "Skin Clarifying Masque",
        "glymed-plus", "1671.00",
        "Себорегулювальна очищувальна маска з ензимами.\n\n"
        "Об'єм: 30 мл.\n\n"
        "Ефективний засіб для очищення та детоксу шкіри, завдяки його "
        "комплексному складу відбувається себорегуляція, м'яка "
        "ексфоліація з наступним зволоженням та відновленням шкіри.\n\n"
        "Склад: Папаїн, бромелаїн, лемонграс, бентоніт, лаванда, "
        "календула, гіалуронова кислота.",
        "Sebum-regulating cleansing mask with enzymes.\n\n"
        "Volume: 30 ml.\n\n"
        "An effective cleansing and detox treatment — its complex formula "
        "regulates sebum production and provides gentle exfoliation "
        "followed by hydration and skin recovery.\n\n"
        "Ingredients: Papain, bromelain, lemongrass, bentonite, lavender, "
        "calendula, hyaluronic acid.",
    ),
    (
        "blemish-control-no-5-with-benzoyl-peroxide",
        "Blemish Control No. 5 with Benzoyl Peroxide",
        "glymed-plus", "1088.00",
        "Лосьйон з 5% бензоїл пероксидом.\n\n"
        "Об'єм: 30 мл.\n\n"
        "Лосьйон з 5% бензоїлпероксидом – це ефективний засіб проти "
        "елементів акне, особливо запальних. Може використовуватися при "
        "захворюванні будь-якого ступеня тяжкості. Має потужну "
        "антибактеріальну та протизапальну дію, пришвидшує загоєння.\n\n"
        "Склад: Бензоїлпероксид 5%, алое вера, лаванда, чайне дерево.",
        "Lotion with 5% benzoyl peroxide.\n\n"
        "Volume: 30 ml.\n\n"
        "A lotion with 5% benzoyl peroxide is an effective treatment "
        "against acne lesions, especially inflammatory ones. Suitable for "
        "any severity of the condition. Has a strong antibacterial and "
        "anti-inflammatory action and speeds up healing.\n\n"
        "Ingredients: Benzoyl peroxide 5%, aloe vera, lavender, tea tree.",
    ),
    (
        "essential-tonic-gel", "ESSENTIAL Tonic Gel",
        "dr-spiller", "1302.00",
        "Тонер-гель для зневодненої шкіри.\n\n"
        "Об'єм: 200 мл.\n\n"
        "Зволожує, заспокоює та освіжає шкіру.\n\n"
        "Склад: Сечовина, гіалуронова кислота, комплекс вітамінів (B3/PP, "
        "В5, B6), стабільна форма вітаміну C, вітамін E, гідролат "
        "гамамелісу, сахариди.",
        "Toner-gel for dehydrated skin.\n\n"
        "Volume: 200 ml.\n\n"
        "Hydrates, soothes and refreshes the skin.\n\n"
        "Ingredients: Urea, hyaluronic acid, vitamin complex (B3/PP, B5, "
        "B6), stable vitamin C, vitamin E, witch hazel hydrolate, "
        "saccharides.",
    ),
    (
        "retinol-serum", "Retinol+ Serum",
        "alissa-beaute", "4635.00",
        "Відновлювальна сироватка з ретинолом.\n\n"
        "Об'єм: 30 мл.\n\n"
        "Інноваційна сироватка поєднує інкапсульований ретинол з "
        "активними компонентами, які працюють зі шкірою, що вже має "
        "ознаки вікових змін. Синергія інгредієнтів зменшує вираженість "
        "зморшок, покращує текстуру, вирівнює рельєф і тон шкіри. "
        "Регулює діяльність сальних залоз, нормалізує склад себуму, має "
        "протизапальну дію. Інкапсульована форма ретинолу нормалізує "
        "процеси кератинізації, усуває гіперкератоз, покращує структуру "
        "шкіри та бореться з фотостарінням. Сприяє синтезу якісного "
        "колагену й еластину. Поєднання ретинолу із заспокійливими "
        "інгредієнтами мінімізує ризик подразнення, що робить її "
        "придатною навіть для чутливої шкіри.\n\n"
        "Склад: Ретинол, пальмітоїл трипептид-5, гіалуронова кислота, "
        "комплекс PoreRefine (агарицинова кислота), екстракт лілії, "
        "ніацинамід, пантенол, комплекс MatriFirm, гідролат лаванди. Не "
        "містить ліпідів.",
        "Restorative serum with retinol.\n\n"
        "Volume: 30 ml.\n\n"
        "This innovative serum combines encapsulated retinol with active "
        "ingredients that work with skin already showing signs of "
        "ageing. The synergy of ingredients reduces the appearance of "
        "wrinkles, improves texture, and evens out skin relief and tone. "
        "It regulates sebaceous gland activity, normalizes sebum "
        "composition, and has an anti-inflammatory effect. The "
        "encapsulated form of retinol normalizes keratinization, "
        "eliminates hyperkeratosis, improves skin structure and fights "
        "photoageing. It promotes the synthesis of quality collagen and "
        "elastin. Combining retinol with soothing ingredients minimizes "
        "the risk of irritation, making it suitable even for sensitive "
        "skin.\n\n"
        "Ingredients: Retinol, palmitoyl tripeptide-5, hyaluronic acid, "
        "PoreRefine complex (agaricic acid), lily extract, niacinamide, "
        "panthenol, MatriFirm complex, lavender hydrolate. Lipid-free.",
    ),
    (
        "fresh-fruit-moisturizing-mask", "Fresh & Fruit Moisturizing Mask",
        "dr-spiller", "2363.00",
        "Зволожувальна гель-маска з екстрактами фруктів.\n\n"
        "Об'єм: 50 мл.\n\n"
        "Охолоджувальна гелева маска з фруктовими екстрактами — фаворит "
        "літнього догляду для всіх типів шкіри. Освіжає, бадьорить, "
        "глибоко зволожує та повертає сяйво навіть тьмяній і втомленій "
        "шкірі. Має легку гелеву текстуру без ліпідів і тропічний "
        "аромат. Фруктовий комплекс (ананас, манго, папая) стимулює "
        "оновлення, делікатно відлущує, вирівнює тон і текстуру, "
        "активізує клітинну активність. Пантенол знімає подразнення, "
        "заспокоює, зменшує чутливість і сприяє відновленню шкіри після "
        "стресу.\n\n"
        "Склад: Екстракти ананасу, манго, папаї, пантенол. Не містить "
        "ліпідів.",
        "Moisturizing gel mask with fruit extracts.\n\n"
        "Volume: 50 ml.\n\n"
        "A cooling gel mask with fruit extracts — a summer skincare "
        "favourite for all skin types. Refreshes, revitalizes, deeply "
        "hydrates and restores radiance even to dull, tired skin. Has a "
        "light, lipid-free gel texture and a tropical scent. The fruit "
        "complex (pineapple, mango, papaya) stimulates renewal, gently "
        "exfoliates, evens out tone and texture, and boosts cellular "
        "activity. Panthenol relieves irritation, soothes, reduces "
        "sensitivity and supports skin recovery after stress.\n\n"
        "Ingredients: Pineapple, mango and papaya extracts, panthenol. "
        "Lipid-free.",
    ),
]

SERVICE = {
    "name_uk": "Консультація лікаря-косметолога онлайн",
    "name_en": "Online cosmetologist consultation",
    "description_uk": "Персональна онлайн-консультація з лікарем-косметологом: аналіз "
    "стану шкіри, підбір домашнього догляду та рекомендації процедур.",
    "description_en": "A personal online consultation with a cosmetologist: skin "
    "condition analysis, home care selection, and treatment recommendations.",
    "price": "1000.00",
    "duration": 60,
}

SPECIALIST = {
    "name": "Михайлець Катерина Русланівна",
    "bio_uk": "Лікар-косметолог зі стажем роботи 2 роки. Спеціалізується на "
    "онлайн-консультаціях: аналіз стану шкіри, підбір індивідуального "
    "домашнього догляду та косметологічних процедур, супровід у "
    "вирішенні проблемної шкіри, акне, вікових змін. Постійно підвищує "
    "кваліфікацію та слідкує за новітніми методиками в естетичній "
    "косметології.",
    "bio_en": "Cosmetologist with 2 years of experience. Specializes in online "
    "consultations: skin condition analysis, selection of individual home "
    "care and cosmetology treatments, and support in addressing problem "
    "skin, acne and signs of ageing. Continuously develops professional "
    "skills and follows the latest techniques in aesthetic cosmetology.",
    "experience": 2,
    "gallery": [
        "specialists/gallery/IMG_2800.jpg",
        "specialists/gallery/IMG_2856.jpg",
        "specialists/gallery/IMG_2880.jpg",
        "specialists/gallery/IMG_2887.jpg",
    ],
}


# Slugs/names from the old generic placeholder demo data this command used
# to seed. Deployed environments already have these rows persisted in
# Postgres from earlier builds; remove them so the storefront converges on
# the real catalog instead of showing a mix of both.
LEGACY_PRODUCT_SLUGS = [
    "soft-moisturising-cream",
    "revitalift-anti-wrinkle-serum",
    "micellar-cleansing-water",
    "fit-me-foundation",
    "lash-sensational-mascara",
    "infallible-24h-lipstick",
    "pro-v-repair-protect-shampoo",
    "fructis-sleek-shine-conditioner",
    "black-white-invisible-deodorant",
    "men-expert-cool-power-shower-gel",
]
LEGACY_BRAND_NAMES = ["Nivea", "L'Oréal", "Garnier", "Maybelline", "Pantene"]
LEGACY_SERVICE_NAMES = [
    "Deep Cleansing Facial",
    "Anti-Age Treatment",
    "Hydration Boost",
    "Brow & Lash Styling",
    "Chemical Peeling",
]
LEGACY_SPECIALIST_NAMES = ["Sophia Williams", "Olivia Martinez", "Emma Johnson"]


class Command(BaseCommand):
    help = "Populate the database with the real portfolio catalog and booking data"

    def handle(self, *args, **options):
        self._cleanup_legacy_demo_data()
        self._create_categories()
        self._create_brands()
        self._create_products()
        self._create_booking_data()
        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))

    def _cleanup_legacy_demo_data(self):
        deleted, _ = Product.objects.filter(slug__in=LEGACY_PRODUCT_SLUGS).delete()
        if deleted:
            self.stdout.write(f"  removed {deleted} legacy demo product row(s)")

        deleted, _ = Brand.objects.filter(name__in=LEGACY_BRAND_NAMES).delete()
        if deleted:
            self.stdout.write(f"  removed {deleted} legacy demo brand row(s)")

        deleted, _ = Specialist.objects.filter(name__in=LEGACY_SPECIALIST_NAMES).delete()
        if deleted:
            self.stdout.write(f"  removed {deleted} legacy demo specialist row(s)")

        deleted, _ = Service.objects.filter(name_en__in=LEGACY_SERVICE_NAMES).delete()
        if deleted:
            self.stdout.write(f"  removed {deleted} legacy demo service row(s)")

    def _create_categories(self):
        for name in CATEGORIES:
            Category.objects.get_or_create(name=name, defaults={"slug": slugify(name)})

    def _create_brands(self):
        for slug, name, desc_uk, desc_en, image in BRANDS:
            brand, created = Brand.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            brand.name = name
            brand.description_uk = desc_uk
            brand.description_en = desc_en
            brand.image = image
            brand.save()
            self.stdout.write(f"  {'created' if created else 'updated'}  brand  {name}")

    def _create_products(self):
        for slug, name, brand_slug, price, desc_uk, desc_en in PRODUCTS:
            category = Category.objects.get(slug="skincare")
            brand = Brand.objects.get(slug=brand_slug)

            product = Product.objects.filter(slug=slug).first()
            created = product is None
            if product is None:
                product = Product(slug=slug)

            product.category = category
            product.brand = brand
            product.name = name
            product.description_uk = desc_uk
            product.description_en = desc_en
            product.price = price
            product.stock = 20
            product.is_available = True
            product.is_featured = True
            product.image = f"products/portfolio/{slug}.jpg"
            product.save()
            self.stdout.write(f"  {'created' if created else 'updated'}  product  {name}")

    def _create_booking_data(self):
        service, created = Service.objects.get_or_create(
            name_en=SERVICE["name_en"],
            defaults={
                "name_uk": SERVICE["name_uk"],
                "description_uk": SERVICE["description_uk"],
                "description_en": SERVICE["description_en"],
                "price": SERVICE["price"],
                "duration": SERVICE["duration"],
            },
        )
        if not created:
            service.name_uk = SERVICE["name_uk"]
            service.description_uk = SERVICE["description_uk"]
            service.description_en = SERVICE["description_en"]
            service.price = SERVICE["price"]
            service.duration = SERVICE["duration"]
            service.save()
        self.stdout.write(f"  {'created' if created else 'updated'}  service  {SERVICE['name_en']}")

        specialist, created = Specialist.objects.get_or_create(
            name=SPECIALIST["name"],
            defaults={
                "bio_uk": SPECIALIST["bio_uk"],
                "bio_en": SPECIALIST["bio_en"],
                "experience": SPECIALIST["experience"],
            },
        )
        specialist.bio_uk = SPECIALIST["bio_uk"]
        specialist.bio_en = SPECIALIST["bio_en"]
        specialist.experience = SPECIALIST["experience"]
        specialist.save()
        specialist.services.set([service])

        for order, path in enumerate(SPECIALIST["gallery"]):
            SpecialistPhoto.objects.get_or_create(
                specialist=specialist, image=path, defaults={"order": order}
            )
        self.stdout.write(
            f"  {'created' if created else 'updated'}  specialist  {SPECIALIST['name']}"
        )
