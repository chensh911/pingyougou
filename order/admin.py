from django.contrib import admin

# Register your models here.
from order.models import OrderGoods, OrderInfo


class ControlOrderInfo(admin.ModelAdmin):
    list_display = ('order_id', "user", "addr", "pay_method", "total_count", "total_price", "order_status", "trade_no")


class ControlOrderGoods(admin.ModelAdmin):
    list_display = ('order', "sku", "count", "price")


admin.site.register(OrderInfo, ControlOrderInfo)
admin.site.register(OrderGoods, ControlOrderGoods)
