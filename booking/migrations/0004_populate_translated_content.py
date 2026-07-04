from django.db import migrations

SERVICE_NAME_EN = {
    "Консультація лікаря-косметолога онлайн": "Online cosmetologist consultation",
}

SERVICE_DESCRIPTION_EN = {
    "Консультація лікаря-косметолога онлайн": (
        "A personal online consultation with a cosmetologist: skin condition "
        "analysis, home care selection, and treatment recommendations."
    ),
}

SPECIALIST_BIO_EN = {
    "Михайлець Катерина Русланівна": (
        "Cosmetologist with 2 years of experience. Specializes in online "
        "consultations: skin condition analysis, selection of individual home care "
        "and cosmetology treatments, and support in addressing problem skin, acne "
        "and signs of ageing. Continuously develops professional skills and follows "
        "the latest techniques in aesthetic cosmetology."
    ),
}


def populate_translations(apps, schema_editor):
    Service = apps.get_model("booking", "Service")
    Specialist = apps.get_model("booking", "Specialist")

    for service in Service.objects.all():
        original_name = service.name
        original_description = service.description
        service.name_uk = original_name
        service.name_en = SERVICE_NAME_EN.get(original_name, original_name)
        service.description_uk = original_description
        service.description_en = SERVICE_DESCRIPTION_EN.get(original_name, original_description)
        service.save(update_fields=["name_uk", "name_en", "description_uk", "description_en"])

    for specialist in Specialist.objects.all():
        original_bio = specialist.bio
        specialist.bio_uk = original_bio
        specialist.bio_en = SPECIALIST_BIO_EN.get(specialist.name, original_bio)
        specialist.save(update_fields=["bio_uk", "bio_en"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0003_service_description_en_service_description_uk_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_translations, noop_reverse),
    ]
