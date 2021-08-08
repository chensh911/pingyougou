'use strict';
update_goods_amount()

// 计算商品的总价格
function update_goods_amount() {
    // 获取商品的单价和数量
    var price = $('.price').children('em').text()
    var count = $('.qty').val()
    // 计算商品的总价
    price = parseFloat(price)
    count = parseInt(count)
    var amount = price * count
    // 设置商品的总价
    $('.total').children('em').text(amount.toFixed(2))
}

// 增加商品的数量
$('.plus').click(function () {
    // 获取商品原有的数目
    var count = $('.qty').val()
    // 加1
    count = parseInt(count) + 1
    // 重新设置商品的数目
    $(this).prev('.qty').val(count)
    // 更新商品的总价
    update_goods_amount()
})

// 减少商品的数量
$('.minus').click(function () {
    // 获取商品原有的数目
    var count = $('.qty').val()
    // 减1
    count = parseInt(count) - 1
    if (count <= 0) {
        count = 1
    }
    // 重新设置商品的数目
    $(this).next('.qty').val(count)
    // 更新商品的总价
    update_goods_amount()
})

// 手动输入商品的数量
$('.qty').blur(function () {
    // 更新商品的总价
    if ($(this).val() <= 0) {
        $(this).val(1)
    }
    update_goods_amount()
})


$(function () {
    var actionAddToCart = $('.js-action-add-cart');

    actionAddToCart.each(function () {
        $(this).on('click', function (e) {
            // 获取数据
            var sku_id = $(this).attr('sku_id')
            var count = $(this).prev().children('.qty').val()
            if (isNaN(count)) {
                count = 1
            }
            var csrf = $('input[name="csrfmiddlewaretoken"]').val()
            var params = {'sku_id': sku_id, 'count': count, 'csrfmiddlewaretoken': csrf}

            $.post('/cart/add', params, function (data) {
                if (data.res == 5) {
                    // 更新成功
                    notifyAddToCart('添加成功');
                } else {
                    notifyAddToCart('添加失败！' + data.errmsg);
                }
            })

        });
    })
    ;


    function notifyAddToCart(productName) {
        $.notify({
            title: productName,
            icon: 'lnr lnr-cart',
            message: ""
        }, {
            type: 'success',
            animate: {
                enter: 'animated fadeInUp',
                exit: 'animated fadeOut'
            },
            placement: {
                from: "bottom",
                align: "right"
            },
            offset: 20,
            spacing: 10,
            z_index: 1031,
        });
    };


})
;