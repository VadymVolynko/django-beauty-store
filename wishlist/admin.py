from django.contrib import admin

from wishlist.models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "added_at"]
    raw_id_fields = ["user", "product"]
