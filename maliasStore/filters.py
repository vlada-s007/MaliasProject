import re

from django.db.models import Q

from maliasStore.models import Category


def filter_products(request, products):

    pricerange = request.GET.get('price')
    brand = request.GET.get('brand')
    subcat = request.GET.get('subcat')
    color = request.GET.get('color')
    cat = request.GET.get('cat')
    if brand:
        products = products.filter(brand__slug=brand)
    if subcat:
        subcat = Category.objects.get(slug=subcat)
        products = subcat.get_sub_products()
    if color:
        products = products.filter(color__slug=color)
    if pricerange:
        from_p, to_p = re.findall("[0-9]+", pricerange)
        products = products.filter(price__gte=int(from_p)).filter(price__lte=int(to_p))
    if cat:
        cat = Category.objects.get(slug=cat)
        products = cat.get_sub_products()
        if 'brand' in request.path:
            _, _, brand = request.path.split('/')
            products = products.filter(brand__slug=brand)
    return products
