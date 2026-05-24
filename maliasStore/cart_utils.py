from .models import Cart, CartItems, Product, Customer, OrderProducts, Order

# Тест купонов
VALID_VOUCHERS = {'200SPECIAL': 200,
                  '300PROMO': 300,
                  '100OPENING': 100}

VALID_COUPONS = {'10OFF': 10,
                 '20OFF': 20,
                 '30OFF': 30}

def coupon_voucher_validator(action, value):
    if action == 'voucher':
        value = VALID_VOUCHERS.get(value)
    elif action == 'coupon_discount':
        value = VALID_COUPONS.get(value)
    return value

class CartTool:
    def __init__(self, request, pk=None, action=None, quantity=None, gift=None, value=None):
        self.user = request.user
        if pk and action:
            self.add_or_delete_product(pk, action, quantity)
            print(action, pk)
        if not pk and action and value:
            self.cart_params(action, value)


    def get_cart_info(self):
        customer = self.user.customer
        cart = customer.cart

        return {
            'customer': customer,
            'cart': cart,
            'items': cart.products.all(),
            'cart_price': cart.cart_price,
            'quantity_cart_items': cart.product_cart_quantity,
        }

    def add_or_delete_product(self, pk, action, quantity=None, gift=None):
        cart = self.get_cart_info()['cart']
        product = Product.objects.get(pk=pk)
        cart_item, created = CartItems.objects.get_or_create(cart=cart, product=product)

        if quantity:
            try:
                value_quantity = int(quantity)
            except:
                value_quantity = 1

        if gift:
            gift = True
            cart_item.gift = gift

        if action == 'add' and product.quantity > 0 and (product.quantity > cart_item.quantity) and \
                (cart_item.quantity + value_quantity):

            cart_item.quantity += value_quantity


        elif action == 'alter':
            if (cart_item.quantity + value_quantity) < product.quantity:
                cart_item.quantity = value_quantity

        elif action == 'gift':
            cart_item.gift = not cart_item.gift

        elif action == 'delete':
            cart_item.quantity -= 1

        elif action == 'clear':
            cart_item.quantity = 0

        cart_item.save()

        if cart_item.quantity == 0 or cart_item.quantity < 0:
            cart_item.delete()

    def cart_params(self, action, value):
        cart = self.get_cart_info()['cart']
        print(action)
        if not action == 'delivery_est':
            new_value = coupon_voucher_validator(action, value)
            if new_value is not None:
                print(new_value)
                if action == 'coupon_discount' and cart.coupon_discount == 0:
                    cart.coupon_discount = new_value
                elif action == 'voucher' and cart.voucher == 0:
                    cart.voucher = new_value
        elif action == 'delivery_est':
            cart.delivery_est = value
        cart.save()

    def save_order(self, request, delivery):
        data = self.get_cart_info()
        cart = data['cart']

        order = Order.objects.create(customer=data['customer'], delivery=delivery,
                                     voucher=cart.voucher, coupon_discount=cart.coupon_discount)
        order.delivery_cost = delivery.get_delivery_cost
        order.subtotal = cart.subtotal_cart_price
        order.price = order.get_total_price
        order.save()

        for item in data['items']:
            product_ordered = OrderProducts.objects.create(order=order, title=item.product.title,
                                                           slug=item.product.slug, quantity=item.quantity,
                                                           price=item.product.get_price(),
                                                           total_price =item.get_total_price,
                                                           image=item.product.get_first_image(),
                                                           model=item.product.model.title,
                                                           )
            if item.product.version:
                product_ordered.version = item.product.version.title
            product_ordered.save()
        cart = data['cart']
        cart.delivery_est = 0
        cart.voucher = 0
        cart.coupon_discount = 0
        cart.save()
        self.clear_cart()


    def clear_cart(self):
        cart_products = self.get_cart_info()['items']
        for item in cart_products:
            product = item.product
            product.quantity -= item.quantity
            product.save()
            item.delete()



