from django import template
import re

from maliasStore.cart_utils import CartTool
from maliasStore.models import *

register = template.Library()

@register.simple_tag()
def main_categories():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def bestsellers():
    return Product.objects.filter(bestseller_status=True).order_by('-created_at')


@register.simple_tag()
def last_posts():
    return Post.objects.order_by('-created_at')[:5]


@register.simple_tag()
def filter_by(category):
    res = False
    title = category.title.split(' ')
    if 'Brand' in title or 'Company' in title:
        res = 'Brand'
    elif 'Type' in title:
        res = 'Type'
    return res


@register.simple_tag()
def all_brands():
    return BrandsAndCompanies.objects.all()


@register.simple_tag()
def all_colors():
    return Color.objects.all()


@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        if value is not None and (key != 'page' or value != 1):
            query[key] = value
        elif key in query:
            del query[key]
    return query.urlencode()


@register.simple_tag()
def get_wishlist(request):
    if request.user.is_authenticated:
        favs = Wishlist.objects.filter(user=request.user)
        products = [i.product for i in favs]

        return products
    else:
        return []


@register.simple_tag()
def count_wishlist(request):
    if request.user.is_authenticated:
        favs = Wishlist.objects.filter(user=request.user)
        count = favs.count
        return count
    else:
        return []


@register.simple_tag()
def avg_rating_dict(avg_rating):
    rating_list = {}
    modulo_op = False
    if avg_rating % 1 != 0:
        modulo_op = avg_rating % 1
    avg_rating = int(avg_rating)
    if avg_rating != 5 :
        for i in range(1, 6):
            if i == avg_rating + 1 and modulo_op:
                rating_list[i] = 'Half'
            elif i in range(1, avg_rating + 1):
                rating_list[i] = True
            else:
                rating_list[i] = False
    else:
        rating_list = dict(zip([i for i in range(1, 6)], [True for i in range(1,6)]))
    return rating_list


@register.simple_tag()
def in_cart(request, pk):
    if request.user.is_authenticated:
        items = CartTool.get_cart_info(request)['items']
        products = [item.product.pk for item in items]
        if pk in products:
            cart_product = True
        else:
            cart_product = False
        return cart_product


@register.simple_tag()
def cart_info(request):
    if request.user.is_authenticated:
        return CartTool(request).get_cart_info()

