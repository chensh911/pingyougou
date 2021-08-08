function update_page_info() {
    var total_count = 0
    var total_price = 0
    $('.cart-item').each(function () {
        // 获取商品的数目和小计
        var count = $(this).find('.qty').val()
        var amount = $(this).children('.product-subtotal').find('em').text()
        // 累加计算商品的总件数和总价格
        count = parseInt(count)
        amount = parseFloat(amount)
        total_count += count
        total_price += amount
    })
    // 设置被选中的商品的总件数和总价格
    $('#total_price').find('em').text(total_price.toFixed(2))
    $('#total_count').find('em').text(total_count)
}

// 计算商品的小计
function update_goods_amount(sku_ul) {
    // 获取商品的价格和数量
    var count = sku_ul.val()
    var price = sku_ul.parents().next().find('em').text()
    // 计算商品的小计
    var amount = parseInt(count) * parseFloat(price)
    sku_ul.parents().next().next().find('em').text(amount.toFixed(2))
}


// 更新购物车中商品的数量
error_update = false
total = 0

function update_remote_cart_info(sku_id, count) {
    var csrf = $('input[name="csrfmiddlewaretoken"]').val()
    // 组织参数
    var params = {'sku_id': sku_id, 'count': count, 'csrfmiddlewaretoken': csrf}
    // 设置ajax请求为同步
    $.ajaxSettings.async = false
    // 发起ajax post请求，访问/cart/update, 传递参数:sku_id count
    // 默认发起的ajax请求都是异步的，不会等回调函数执行
    $.post('/cart/update', params, function (data) {
        if (data.res == 5) {
            // 更新成功
            error_update = false
            total = data.total_count
        } else {
            // 更新失败
            error_update = true
            alert(data.errmsg)
        }
    })
    // 设置ajax请求为异步
    $.ajaxSettings.async = true
}

// 记录用户输入之前商品的数量
pre_count = 0
$('.qty').focus(function () {
    pre_count = $(this).val()
})

// 手动输入购物车中的商品数量
$('.qty').blur(function () {
    // 获取商品的id和商品的数量
    var sku_id = $(this).attr('sku_id')
    var count = $(this).val()

    // 校验参数
    if (isNaN(count) || count.trim().length == 0 || parseInt(count) <= 0) {
        // 设置商品的数目为用户输入之前的数目
        $(this).val(pre_count)
        return
    }

    // 更新购物车中的记录
    count = parseInt(count)
    update_remote_cart_info(sku_id, count)

    // 判断更新是否成功
    if (error_update == false) {
        // 重新设置商品的数目
        $(this).val(count)
        // 计算商品的小计
        update_goods_amount($(this))
        // 获取商品对应的checkbox的选中状态，如果被选中，更新页面信息
        update_page_info()
    } else {
        // 设置商品的数目为用户输入之前的数目
        $(this).val(pre_count)
    }
})

// 删除购物车中的记录
$('.remove').click(function () {
    // 获取对应商品的id
    var sku_id = $(this).attr('sku_id')
    var csrf = $('input[name="csrfmiddlewaretoken"]').val()
    // 组织参数
    var params = {'sku_id': sku_id, 'csrfmiddlewaretoken': csrf}
    // 获取商品所在的ul元素
    var sku_td = $(this).parents('.cart-item')
    // 发起ajax post请求， 访问/cart/delete, 传递参数:sku_id
    $.post('/cart/delete', params, function (data) {
        if (data.res == 3) {
            // 删除成功，异常页面上商品所在的ul元素
            sku_td.remove()
            // 获取sku_ul中商品的选中状态
            update_page_info()
        } else {
            alert(data.errmsg)
        }
    })
})
