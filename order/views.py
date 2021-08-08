from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.views.generic import View

from user.models import Address
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods

from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from datetime import datetime
# from alipay import AliPay
import os


# Create your views here.
# /order/place
class OrderPlaceView(LoginRequiredMixin, View):
    """提交订单页面显示"""

    def post(self, request):
        """提交订单页面显示"""
        # 获取我们的登录用户
        user = request.user
        # 获取参数sku_ids
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        sku_ids = conn.hgetall(cart_key)
        skus = []
        # 保存商品的总家属和总价
        total_count = 0
        total_price = 0
        sku_id_lst = []
        # 便利sku_ids获取用户要购买的商品的信息
        for sku_id in sku_ids:
            # 根据商品的id获取商品的信息
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户要购买的商品的数量
            count = conn.hget(cart_key, sku_id)
            # 计算商品的小计
            amount = sku.price * int(count)
            # 动态给sku增加属性count,保存购买商品的数量
            sku.count = int(count)
            # 动态给sku添加属性amount,保存购买商品的小计
            sku.amount = amount
            # 追加
            skus.append(sku)
            sku_id_lst.append(str(int(sku_id)))
            # 累加计算商品的总价和总术
            total_count += int(count)
            total_price += amount

        # 获取用户默认的地址
        default_addr = Address.objects.get(user=user, is_default=True)

        # 获取用户非默认的地址
        not_default_addrs = Address.objects.filter(user=user, is_default=False)

        # 组织上下文
        sku_ids = ','.join(sku_id_lst)  # [1, 25]->1, 25
        context = {'skus': skus,
                   'total_count': total_count,
                   'total_price': total_price,
                   'default_addr': default_addr,
                   'not_default_addrs': not_default_addrs,
                   'sku_ids': sku_ids,
                   }

        # 使用模板
        return render(request, 'place_order.html', context)


# 前端传递的参数: 地址的id 支付方法(pay_method), 用户要购买的商品id
# 悲观锁：执行的时候加琐 用户抢锁
class OrderCommitView(View):
    """订单创建"""

    # 事务装饰器
    @transaction.atomic
    def post(self, request):
        """订单创建"""
        # 判断用户是否登录,非后台无法使用LoginRequiredMixin验证
        user = request.user
        if not user.is_authenticated:
            # 用户美登录
            return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

        # 接受参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')
        print("=========================")

        # 校验参数
        if not all([addr_id, pay_method, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

        # 校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法的支付方式'})

        # 校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            # 地址不存在
            return JsonResponse({'res': 3, 'errmsg': '地址不存在'})

        # todo: 创建订单核心业务

        # 组织参数
        # 订单id： 年月日时间+用户id
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)


        # 总数木和总金额
        total_count = 0
        total_price = 0

        # 设置事务保存点
        save_id = transaction.savepoint()
        try:
            # todo： 向df_order_info表中添加一条记录
            order = OrderInfo.objects.create(order_id=order_id,
                                             user=user,
                                             addr=addr,
                                             pay_method=pay_method,
                                             total_count=total_count,
                                             total_price=total_price,
                                             )

            # todo： 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id

            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                # 获取商品的信息
                try:
                    # 悲观锁：select * from df_goods_sku where id=sku_id for update; for update 为加琐操作
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                except:
                    # 商品不存在
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 4, 'errmsg': '商品不存在'})

                # 从redis中获取用户所要购买的商品的数量
                count = conn.hget(cart_key, sku_id)
                # todo：判断商品的库存
                if int(count) > sku.stock:
                    transaction.savepoint_rollback(save_id)
                    return JsonResponse({'res': 6, 'errmsg': ' 商品库存不足'})
                # todo：向df_order_goods表中添加一条记录
                OrderGoods.objects.create(order=order,
                                          sku=sku,
                                          count=count,
                                          price=sku.price)
                # todo: 更新商品的库存和销量
                sku.stock -= int(count)
                sku.save()
                # todo: 累加计算订单商品的总数量和总价格
                amount = sku.price * int(count)
                total_count += int(count)
                total_price += amount
            # todo: 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # todo： 清楚用户购物车中对应的记录 [1, 3]
        conn.hdel(cart_key, *sku_ids)  # 拆包

        # 返回应答
        return JsonResponse({'res': 5, 'message': '创建成功'})


class CommentView(LoginRequiredMixin, View):
    """订单评论"""

    def get(self, request, order_id, sku_id):
        """提供评论页面"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        try:
            order_good = OrderGoods.objects.get(order=order, sku_id=sku_id)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        comment = order_good.comment
        # 使用模板
        return render(request, "order_comment.html", {"comment": comment})

    def post(self, request, order_id, sku_id):
        """处理评论内容"""
        user = request.user
        # 校验数据
        if not order_id:
            return redirect(reverse('user:order'))

        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        try:
            order_good = OrderGoods.objects.get(order=order, sku_id=sku_id)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))

        comment = request.POST.get('comment')
        order_good.comment = comment
        order_good.save()

        order.order_status = 5  # 已完成
        order.save()

        return redirect(reverse("user:order", kwargs={"page": 1}))
