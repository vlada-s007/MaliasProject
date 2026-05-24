from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .cart_utils import CartTool
from .models import *
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from .filters import filter_products
from django.db.models import Q, QuerySet
import stripe
from electronics_store.settings import STRIPE_SECRET_KEY


# Create your views here.
class IndexView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'maliasStore/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IndexView, self).get_context_data()
        context['title'] = 'index'
        context['sale_products'] = Product.objects.filter(discount__gt=0).order_by('-created_at')
        context['new_products'] = Product.objects.filter(new_status=True).order_by('-created_at')

        context['random_products'] = Product.objects.order_by('?')
        return context


class BaseProductsList(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'maliasStore/products_list.html'
    paginate_by = 7

class SameModel(BaseProductsList):

    def get_queryset(self):
        products = Product.objects.filter(model__slug=self.kwargs['slug'])
        products = filter_products(self.request, products)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SameModel, self).get_context_data()
        model = ModelProduct.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'Compare {model.title} versions'
        context['model'] = model
        return context


class ManufacturerPage(BaseProductsList):


    def get_queryset(self):
        products = Product.objects.filter(brand__slug=self.kwargs['slug'])
        products = filter_products(self.request, products)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ManufacturerPage, self).get_context_data()
        brand = BrandsAndCompanies.objects.get(slug=self.kwargs['slug'])
        context['title'] = f'{brand.title} products'
        context['brand'] = brand
        return context


class SearchView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'maliasStore/products_list.html'
    paginate_by = 7

    def get_queryset(self):
        search_query = self.request.GET.get('q')
        products = Product.objects.all()
        if search_query and search_query is not None:
            products = Product.objects.filter(Q(title__iregex=search_query)|Q(description__iregex=search_query))
        products = filter_products(self.request, products)
        return products.order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data()
        title = 'Search results'
        if self.request.GET.get('q') != '' and self.request.GET.get('q') is not None:
            title += f" for '{self.request.GET.get('q')}'"
        if self.request.GET.get('subcat'):
            cat_slug = self.request.GET.get('subcat')
            if cat_slug == 'all':
                title += f" in All Categories"
            else:
                category = Category.objects.get(slug=cat_slug)
                title += f" in '{category}'"
        context['title'] = f'{title}'
        return context


class CategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'maliasStore/category.html'
    paginate_by = 16

    def get_queryset(self):
        category = Category.objects.get(slug=self.kwargs['slug'])
        products = category.get_sub_products()
        products = filter_products(self.request, products)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CategoryView, self).get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = category.subcategories.all()
        parent = category.parent
        context['title'] = f'{category.title}'
        context['category'] = category
        context['category_parent'] = parent
        context['subcategories'] = subcategories
        return context


class SaleProducts(BaseProductsList):
    extra_context = {
        'title': 'Special Offers',
    }

    def get_queryset(self):
        products = Product.objects.filter(discount__gt=0).order_by('-created_at')
        products = filter_products(self.request, products)
        return products


class Bestsellers(BaseProductsList):
    extra_context = {
        'title': 'Bestsellers',
    }

    def get_queryset(self):
        products = Product.objects.filter(bestseller_status=True)
        products = filter_products(self.request, products)
        return products


class NewProducts(BaseProductsList):

    extra_context = {
        'title': 'New Arrivals',
    }

    def get_queryset(self):
        products = Product.objects.filter(new_status=True)
        products = filter_products(self.request, products)
        return products


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'maliasStore/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data()
        product = context['product']
        context['title'] = f'{product.title}'
        last_category = product.category.last()
        versions = []
        same_model = Product.objects.filter(model=product.model).exclude(pk=product.pk).distinct()
        context['category'] = last_category
        context['category_parent'] = last_category.parent
        try:
            context['similar_products'] = last_category.parent.parent.get_sub_products()
        except:
            pass
        context['version'] = product.version
        for m_product in same_model:
            if m_product.version and m_product.version not in versions and m_product.version != product.version:
                versions.append(m_product)
        context['product_versions'] = set(versions)
        same_model_same_version = same_model.exclude(~Q(version=product.version))
        context['same_model_products'] = same_model_same_version
        context['reviews'] = product.reviews.all()
        context['review_authors'] = [review.customer for review in product.reviews.all()]
        if self.request.user.is_authenticated:
            orders_user = self.request.user.customer.orders.all()
            order_products = [order.get_order_product_slugs for order in orders_user]
            concat_products = [nested for i in order_products for nested in i]
            products = Product.objects.filter(slug__in=concat_products)
            check = products.filter(id=product.id).exists()
            print(bool(check))
            context['permission_review'] = bool(check)

        return context


def contact_view(request):
    context = {'title': 'Contact Us',
               'form': ContactForm()}
    return render(request, 'maliasStore/contact.html', context)

def save_contact(request):
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact')

def about_view(request):
    context = {'title': 'About Us'}
    return render(request, 'maliasStore/about.html', context)


def logout_view(request):
    logout(request)
    return redirect('index')


class LoginUserView(LoginView):
    form_class = LoginForm
    template_name = 'maliasStore/auth.html'
    next_page = 'index'
    redirect_authenticated_user = 'index'
    extra_context = {'title': 'Log In'}


def register_user_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = RegistrationForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                phone = request.POST.get('phone')
                newsletter = request.POST.get('newsletter')
                sub = False
                if newsletter == 'on':
                    sub = True
                customer = Customer.objects.create(user=user, newsletter=sub, phone=phone)
                cart = Cart.objects.create(customer=customer)
                customer.save()
                cart.save()
                return redirect('auth')
        else:
            form = RegistrationForm()

        context = {
            'title': 'Регистрация',
            'form': form,
        }
        return render(request, 'maliasStore/registration.html', context=context)
    else:
        return redirect('index')

@login_required(login_url='auth')
def account_view(request):

    context = {
        'title': 'My Account',
        'user_form': UserChangeForm(instance=request.user),
        'customer_form': CustomerAccountChangeForm(instance=request.user.customer),
        'dict_city': {i.pk: [[j.name, j.pk] for j in i.cities.all()] for i in Region.objects.all()},
        'order': request.user.customer.orders.last(),
        'orders': Order.objects.filter(customer=request.user.customer).order_by('-created_at')
    }
    print(Order.objects.filter(customer=request.user.customer).order_by('-created_at'))
    return render(request, 'maliasStore/account.html', context)

@login_required(login_url='auth')
def account_change(request):
    next_page = request.META.get('HTTP_REFERER', 'index')
    if request.method == 'POST':
        user_form = UserChangeForm(data=request.POST, instance=request.user)
        customer_form = CustomerAccountChangeForm(data=request.POST, instance=request.user.customer)
        newsletter = request.POST.get('newsletter')
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save(commit=False)
            sub = False
            if newsletter == 'on':
                sub = True
            customer_form.newsletter = sub
            customer_form.save()
        return redirect(next_page)
    else:
        return redirect(next_page)
    

class WishlistProducts(LoginRequiredMixin, ListView):
    model = Wishlist
    context_object_name = 'favs'
    template_name = 'maliasStore/wishlist.html'
    extra_context = {
        'title': 'Wishlist'
    }

    def get_queryset(self):
        products = Wishlist.objects.filter(user=self.request.user)
        return products

@login_required(login_url='auth')
def add_remove_wishlist(request, pk):
    user = request.user
    product = Product.objects.get(pk=pk)
    fav, created = Wishlist.objects.get_or_create(user=user, product=product)
    if not created:
        fav.delete()
    next_page = request.META.get('HTTP_REFERER', 'index')
    return redirect(next_page)

@login_required(login_url='auth')
def cart_view(request):
    cart = CartTool(request)
    context = cart.get_cart_info()
    context['title'] = 'My Cart'
    regions = Region.objects.all()
    context['regions'] = regions
    context['dict_city'] = {i.pk: [[j.name, j.pk] for j in i.cities.all()] for i in regions}
    return render(request, 'maliasStore/cart.html', context)

@login_required(login_url='auth')
def estimate_delivery(request):
    cart_info = CartTool(request).get_cart_info()
    if request.method == 'POST':
        region = int(request.POST.get('region'))
        city = int(request.POST.get('city'))
        print(region)
        print(city)
        if region == 1:
            if city != 1:
                delivery_cost = 10
            else:
                delivery_cost = 5
        if int(cart_info['cart_price']) > 500:
            delivery_cost = 0
        else:
            delivery_cost = 15
        int(cart_info['cart_price'])
        est = CartTool(request).cart_params(action='delivery_est', value=delivery_cost)
    return redirect('cart')

@login_required(login_url='auth')
def review_product(request):
    next_page = request.META.get('HTTP_REFERER', 'index')
    if request.method == 'POST':
        content = request.POST.get('review-text')
        rating = request.POST.get('rating')
        slug = request.POST.get('product-review')
        product = Product.objects.get(slug=slug)
        if rating:
            UserRating.objects.create(customer=request.user.customer, product=product,
                                      content=content, rating=int(rating))
        return redirect(next_page)
    else:
        return redirect(next_page)



@login_required(login_url='auth')
def add_or_remove_cart(request, pk, action):
    next_page = request.META.get('HTTP_REFERER', 'index')

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        gift = request.POST.get('gift_cart')
        print(action, gift, quantity)
        if gift == 'on':
            gift = True
        print(gift)
        if not quantity:
            quantity = 1
        cart_user = CartTool(request, pk=pk, action=action, quantity=quantity, gift=gift)
        return redirect(next_page)
    else:
        return redirect(next_page)

def alter_cart(request, action):
    next_page = request.META.get('HTTP_REFERER', 'index')
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        voucher = request.POST.get('voucher')
        print(coupon, voucher, action)
        if action == 'coupon_discount':
            value = coupon
        elif action == 'voucher':
            value = voucher

        cart_user = CartTool(request, action=action, value=value)
        cart = CartTool.get_cart_info(request)['cart']
        return redirect(next_page)
    else:
        return redirect(next_page)


@login_required(login_url='auth')
def checkout_view(request):
    cart = CartTool(request)
    if cart.get_cart_info()['items']:
        context = {}
        cart_info = cart.get_cart_info()
        context['items'] = cart_info['items']
        regions = Region.objects.all()
        context['dict_city'] = {i.pk: [[j.name, j.pk] for j in i.cities.all()] for i in regions}
        context['title'] = 'Checkout'
        context['user_form'] = UserChangeForm(instance=request.user)
        context['customer_form'] = CustomerAccountChangeForm(instance=request.user.customer)
        delivery_form = DeliveryForm(instance=request.user.customer)
        context['form'] = delivery_form
        return render(request, 'maliasStore/checkout.html', context)

    else:
        return redirect('index')

@login_required(login_url='auth')
def create_checkout_session(request):
    stripe.api_key = STRIPE_SECRET_KEY
    cart = CartTool(request)
    cart_info = cart.get_cart_info()
    if request.method == 'POST' and cart_info['items']:
        cart_price = cart_info['cart_price']
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': ', '.join(i.product.title for i in cart_info['items'])},
                    'unit_amount': int(cart_price) * 100
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout')),
        )
        delivery_form = request.POST
        request.session[f'form_{request.user.pk}'] = delivery_form

        return redirect(session.url)

@login_required(login_url='auth')
def success_payment_view(request):
    cart = CartTool(request)
    cart_info = cart.get_cart_info()
    try:
        form = request.session.get(f'form_{request.user.pk}')
        request.session.pop(f'form_{request.user.pk}')
    except:
        form = False

    if cart_info['items'] and form:
        delivery_form = DeliveryForm(data=form)
        if delivery_form.is_valid():
            delivery = delivery_form.save(commit=False)
            delivery.customer = request.user.customer
            delivery.save()
            cart.save_order(request, delivery)
        else:
            return redirect('checkout')
        context = {'title': 'Payment successful',
                   'order': request.user.customer.orders.last()}
        return render(request, 'maliasStore/success.html', context)
    else:
        return redirect('index')

