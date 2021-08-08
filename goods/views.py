from django.core.paginator import Paginator
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from goods.models import GoodsType, IndexTypeGoodsBanner, GoodsSKU, GoodsImage
from order.models import OrderGoods


class IndexView(View):
    def get(self, request):
        # 商品种类
        types = GoodsType.objects.all()


        # 首页展示商品信息
        type_goods_banners = IndexTypeGoodsBanner.objects.all()

        context = {
            'types': types,
            'type_goods_banners': type_goods_banners
        }
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context.update(cart_count=cart_count)

        return render(request, 'index.html', context)


class DetailView(View):
    """商品详情界面"""

    def get(self, request, goods_id):

        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist as e:
            return redirect(reverse('goods:index'))
        try:
            goods_img = GoodsImage.objects.filter(sku=sku)
        except GoodsImage.DoesNotExist as e:
            goods_img = None

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        sku_orders.len = sku_orders.count()
        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:4]
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)

        context = {
            'sku': sku,
            'sku_orders': sku_orders,
            'new_skus': new_skus,
            'goods_img': goods_img,
        }
        context.update(cart_count=cart_count)

        return render(request, 'detail.html', context)


class ListView(View):
    """列表页"""

    def get(self, request, type_id, page):
        # 先验证种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist as e:
            return redirect(reverse('goods:index'))

        # 获取下拉的全部种类信息
        types = GoodsType.objects.all()

        # 获取排序的方式
        sort = request.GET.get('sort')
        if sort == '价格':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == '成熟度':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = '默认'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对skus数据进行分页
        paginator = Paginator(skus, 12)
        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的page对象，废弃因为会加载所有的页码
        skus_page = paginator.page(page)
        # 控制限制的页码，只显示最多5个按钮
        # 如果总页数小于5，显示[1-页码]
        # 如果当前页是前三页，显示[1,2,3,4,5]
        # 如果当前页是后三页，显示[4,5,6,7,8] num_pages-4 到num_oages+1

        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)
        # 通过page对象获取数据
        # 获取首页购物车的数目
        cart_count = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cart_key = 'cart_%s' % request.user.id
            cart_count = conn.hlen(cart_key)
        context = {
            "sort": sort,
            "type": type,
            "types": types,
            "skus_page": skus_page,
            "cart_count": cart_count,
            "pages": pages,
            "count": paginator.count,
        }

        return render(request, 'list.html', context)
