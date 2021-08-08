from django.contrib import admin

# Register your models here.
from goods.models import Goods, GoodsType, GoodsSKU, IndexTypeGoodsBanner, GoodsImage


class ControlGoodsType(admin.ModelAdmin):
    list_display = ('name', "logo", "image")


class ControlGoodsSKU(admin.ModelAdmin):
    list_display = ('type', "goods", "name", "price", "image", "stock")


class ControlGoods(admin.ModelAdmin):
    list_display = ('name',)


class ControlGoodsImage(admin.ModelAdmin):
    list_display = ('sku', 'image')


class ControlIndexTypeGoodsBanner(admin.ModelAdmin):
    list_display = ('sku', 'type', 'index')


admin.site.register(GoodsType, ControlGoodsType)
admin.site.register(Goods, ControlGoods)
admin.site.register(GoodsSKU, ControlGoodsSKU)
admin.site.register(IndexTypeGoodsBanner, ControlIndexTypeGoodsBanner)
admin.site.register(GoodsImage, ControlGoodsImage)
