"""
Management command: python manage.py populate_db
Creates sample categories, brands, products and booking data.
"""
import io

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from booking.models import Service, Specialist
from catalog.models import Brand, Category, Product


def _make_image(color: str, label: str) -> ContentFile:
    """Generate a simple colored PNG placeholder with text."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (600, 600), color=color)
    draw = ImageDraw.Draw(img)

    # Draw brand/name text centered
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except OSError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((600 - w) // 2, (600 - h) // 2), label, fill="white", font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue())


PRODUCTS = [
    # (category, brand, name, description, price, stock, bg_color)
    ("Skincare",  "Nivea",     "Soft Moisturising Cream",
     "Intensive moisturising cream for face, hands and body. Suitable for all skin types.",
     8.99, 50, "#3a6ea8"),

    ("Skincare",  "L'Oréal",   "Revitalift Anti-Wrinkle Serum",
     "Pro-Retinol serum that reduces wrinkles and firms skin overnight.",
     24.99, 35, "#c0392b"),

    ("Skincare",  "Garnier",   "Micellar Cleansing Water",
     "Gently removes makeup and impurities without rinsing. For all skin types.",
     7.49, 60, "#27ae60"),

    ("Makeup",    "Maybelline", "Fit Me Foundation",
     "Natural finish foundation with SPF 18 and a wide range of shades.",
     12.99, 40, "#8e44ad"),

    ("Makeup",    "Maybelline", "Lash Sensational Mascara",
     "Multiplying brush opens up your lashes for a sensational fan effect.",
     11.49, 45, "#2c3e50"),

    ("Makeup",    "L'Oréal",   "Infallible 24H Lipstick",
     "Long-lasting lipstick with an intense color payoff, lasts up to 24 hours.",
     9.99, 30, "#e74c3c"),

    ("Haircare",  "Pantene",   "Pro-V Repair & Protect Shampoo",
     "Strengthening shampoo that repairs damaged hair from root to tip.",
     6.99, 55, "#f39c12"),

    ("Haircare",  "Garnier",   "Fructis Sleek & Shine Conditioner",
     "Anti-frizz conditioner with Argan oil for smooth, glossy hair all day.",
     6.49, 50, "#16a085"),

    ("Perfumery", "Nivea",     "Black & White Invisible Deodorant",
     "48h protection against sweat and odor. No white marks, no yellow stains.",
     5.99, 80, "#2d3436"),

    ("Perfumery", "L'Oréal",   "Men Expert Cool Power Shower Gel",
     "Energising shower gel with menthol that leaves skin feeling refreshed.",
     7.99, 45, "#0984e3"),
]

SERVICES = [
    ("Deep Cleansing Facial",
     "A thorough cleanse that removes impurities, unclogs pores and brightens complexion.",
     45.00, 60),
    ("Anti-Age Treatment",
     "Targeted treatment using hyaluronic acid and retinol to reduce visible signs of ageing.",
     75.00, 90),
    ("Hydration Boost",
     "Intensive moisturising mask and massage that restores skin's natural glow.",
     55.00, 60),
    ("Brow & Lash Styling",
     "Professional shaping, tinting and styling for brows and lashes.",
     35.00, 45),
    ("Chemical Peeling",
     "Light AHA/BHA peel that smooths texture, fades spots and refreshes skin tone.",
     90.00, 75),
]

SPECIALISTS = [
    ("Sophia Williams",
     "Certified cosmetologist with 8 years of experience specialising in anti-age treatments and facial care.",
     8, ["Deep Cleansing Facial", "Anti-Age Treatment", "Chemical Peeling"]),
    ("Olivia Martinez",
     "Skincare specialist focused on hydration therapies and sensitive skin. Passionate about clean beauty.",
     5, ["Hydration Boost", "Deep Cleansing Facial", "Brow & Lash Styling"]),
    ("Emma Johnson",
     "Expert in aesthetic procedures with 12 years in top beauty salons across Europe.",
     12, ["Anti-Age Treatment", "Chemical Peeling", "Hydration Boost"]),
]


class Command(BaseCommand):
    help = "Populate the database with sample beauty store data"

    def handle(self, *args, **options):
        self._create_products()
        self._create_booking_data()
        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))

    def _create_products(self):
        for cat_name, brand_name, name, desc, price, stock, color in PRODUCTS:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={"slug": slugify(cat_name)},
            )
            brand, _ = Brand.objects.get_or_create(
                name=brand_name,
                defaults={"slug": slugify(brand_name)},
            )

            slug = slugify(name)
            if Product.objects.filter(slug=slug).exists():
                self.stdout.write(f"  skip  {name}")
                continue

            product = Product(
                category=cat,
                brand=brand,
                name=name,
                slug=slug,
                description=desc,
                price=price,
                stock=stock,
                is_available=True,
            )

            img_data = _make_image(color, brand_name)
            product.image.save(f"{slug}.png", img_data, save=False)
            product.save()
            self.stdout.write(f"  created  {name}")

    def _create_booking_data(self):
        service_objs = {}
        for s_name, s_desc, s_price, s_dur in SERVICES:
            svc, created = Service.objects.get_or_create(
                name=s_name,
                defaults={"description": s_desc, "price": s_price, "duration": s_dur},
            )
            service_objs[s_name] = svc
            if created:
                self.stdout.write(f"  service  {s_name}")

        for sp_name, sp_bio, sp_exp, sp_services in SPECIALISTS:
            if Specialist.objects.filter(name=sp_name).exists():
                continue
            sp = Specialist.objects.create(name=sp_name, bio=sp_bio, experience=sp_exp)

            img_data = _make_image("#b45309", sp_name.split()[0])
            sp.photo.save(f"{sp_name.lower().replace(' ', '-')}.png", img_data, save=False)
            sp.save()

            for svc_name in sp_services:
                if svc_name in service_objs:
                    sp.services.add(service_objs[svc_name])

            self.stdout.write(f"  specialist  {sp_name}")
