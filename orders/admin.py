from django.contrib import admin
from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ("id", "first_name", "last_name", "email", "status", "total_price", "created_at")
    list_filter   = ("status",)
    search_fields = ("first_name", "last_name", "email")
    list_editable = ("status",)
    inlines       = [OrderItemInline]
