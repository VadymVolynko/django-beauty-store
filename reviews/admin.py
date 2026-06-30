from django.contrib import admin

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "rating", "created_at"]
    list_filter = ["rating"]
    raw_id_fields = ["user", "product"]
