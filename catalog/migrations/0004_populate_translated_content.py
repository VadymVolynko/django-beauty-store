from django.db import migrations

BRAND_DESCRIPTIONS_EN = {
    "dr-spiller": (
        "Professional cosmetics from the German brand Dr. Spiller with proven clinical "
        "efficacy, based on natural organic ingredients and plant extracts."
    ),
    "alissa-beaute": (
        "An Italian dermocosmetics brand with up to 98% natural ingredients. Light "
        "textures, organic oils and extracts give skin comfort in the rhythm of city "
        "life. The key advantage is innovative peptides with a pronounced anti-age "
        "effect. Alissa Beauté combines nature and science to create professional care "
        "that makes beauty visible every day."
    ),
    "glymed-plus": (
        "A professional cosmeceutical brand from the USA, one of the leaders in acne "
        "and rosacea treatment."
    ),
    "me-line": (
        "The Me Line range is a unique development by the Spanish company "
        "Innoaesthetics, with formulas designed to treat pigment spots of any origin, "
        "for all skin types, face and body."
    ),
    "bioline-jato": (
        "An Italian premium professional cosmetics brand that combines science and "
        "nature to create effective face and body skincare products."
    ),
    "dermaquest": (
        "A premium American professional cosmeceutical brand founded in 1999 by "
        "biochemist Sam Dhatt, who developed formulas for over 700 global brands. The "
        "line specializes in addressing complex skin concerns: acne, hyperpigmentation, "
        "ageing and rosacea."
    ),
    "maria-galland-paris": (
        "A French premium professional skincare brand with a breathtaking history."
    ),
    "simildiet": (
        "A pharmaceutical laboratory founded in 1993 in Zaragoza, Spain, by "
        "mesotherapy physician Carlos Aznar Sánchez. The brand takes a comprehensive "
        "approach to beauty, creating its own innovative formulas. The name means "
        "“diet for the skin” — nourishing cells with valuable ingredients."
    ),
    "trawenmoor": (
        "When developing TRAWENMOOR, our goal was to fully meet today's high standards "
        "for organic cosmetics and to show that “organic” doesn't mean "
        "compromising on quality and efficacy — quite the opposite."
    ),
}

PRODUCT_DESCRIPTIONS_EN = {
    "daily-ritual-pure-gel-cleansing": (
        "Cleansing gel for oily and combination skin.\n\n"
        "The gel removes excess sebum while preserving the skin's hydrolipidic barrier "
        "without disrupting the integrity of the stratum corneum. Recommended for oily, "
        "combination and problem skin, and for acne-prone skin.\n\n"
        "Ingredients: Coco-glucoside, lauryl glucoside, xanthan gum, fruit "
        "oligosaccharides, white willow extract, fruit acids, niacinamide."
    ),
    "skin-clarifying-masque": (
        "Sebum-regulating cleansing mask with enzymes.\n\n"
        "Volume: 30 ml.\n\n"
        "An effective cleansing and detox treatment — its complex formula regulates "
        "sebum production and provides gentle exfoliation followed by hydration and "
        "skin recovery.\n\n"
        "Ingredients: Papain, bromelain, lemongrass, bentonite, lavender, calendula, "
        "hyaluronic acid."
    ),
    "blemish-control-no-5-with-benzoyl-peroxide": (
        "Lotion with 5% benzoyl peroxide.\n\n"
        "Volume: 30 ml.\n\n"
        "A lotion with 5% benzoyl peroxide is an effective treatment against acne "
        "lesions, especially inflammatory ones. Suitable for any severity of the "
        "condition. Has a strong antibacterial and anti-inflammatory action and speeds "
        "up healing.\n\n"
        "Ingredients: Benzoyl peroxide 5%, aloe vera, lavender, tea tree."
    ),
    "essential-tonic-gel": (
        "Toner-gel for dehydrated skin.\n\n"
        "Volume: 200 ml.\n\n"
        "Hydrates, soothes and refreshes the skin.\n\n"
        "Ingredients: Urea, hyaluronic acid, vitamin complex (B3/PP, B5, B6), stable "
        "vitamin C, vitamin E, witch hazel hydrolate, saccharides."
    ),
    "retinol-serum": (
        "Restorative serum with retinol.\n\n"
        "Volume: 30 ml.\n\n"
        "This innovative serum combines encapsulated retinol with active ingredients "
        "that work with skin already showing signs of ageing. The synergy of "
        "ingredients reduces the appearance of wrinkles, improves texture, and evens "
        "out skin relief and tone. It regulates sebaceous gland activity, normalizes "
        "sebum composition, and has an anti-inflammatory effect. The encapsulated form "
        "of retinol normalizes keratinization, eliminates hyperkeratosis, improves "
        "skin structure and fights photoageing. It promotes the synthesis of quality "
        "collagen and elastin. Combining retinol with soothing ingredients minimizes "
        "the risk of irritation, making it suitable even for sensitive skin.\n\n"
        "Ingredients: Retinol, palmitoyl tripeptide-5, hyaluronic acid, PoreRefine "
        "complex (agaricic acid), lily extract, niacinamide, panthenol, MatriFirm "
        "complex, lavender hydrolate. Lipid-free."
    ),
    "fresh-fruit-moisturizing-mask": (
        "Moisturizing gel mask with fruit extracts.\n\n"
        "Volume: 50 ml.\n\n"
        "A cooling gel mask with fruit extracts — a summer skincare favourite for all "
        "skin types. Refreshes, revitalizes, deeply hydrates and restores radiance "
        "even to dull, tired skin. Has a light, lipid-free gel texture and a tropical "
        "scent. The fruit complex (pineapple, mango, papaya) stimulates renewal, "
        "gently exfoliates, evens out tone and texture, and boosts cellular activity. "
        "Panthenol relieves irritation, soothes, reduces sensitivity and supports skin "
        "recovery after stress.\n\n"
        "Ingredients: Pineapple, mango and papaya extracts, panthenol. Lipid-free."
    ),
}


def populate_translations(apps, schema_editor):
    Brand = apps.get_model("catalog", "Brand")
    Product = apps.get_model("catalog", "Product")

    for brand in Brand.objects.all():
        original = brand.description
        brand.description_uk = original
        brand.description_en = BRAND_DESCRIPTIONS_EN.get(brand.slug, original)
        brand.save(update_fields=["description_uk", "description_en"])

    for product in Product.objects.all():
        original = product.description
        product.description_uk = original
        product.description_en = PRODUCT_DESCRIPTIONS_EN.get(product.slug, original)
        product.save(update_fields=["description_uk", "description_en"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_brand_description_en_brand_description_uk_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_translations, noop_reverse),
    ]
