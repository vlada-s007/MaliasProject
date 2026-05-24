from django.urls import path
from .views import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('contact/', contact_view, name='contact'),
    path('contact/save', save_contact, name='save_contact_form'),
    path('about/', about_view, name='about'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    path('search/', SearchView.as_view(), name='search'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('bestsellers/', Bestsellers.as_view(), name='bestsellers'),
    path('special-offers/', SaleProducts.as_view(), name='special-offers'),
    path('new-products/', SaleProducts.as_view(), name='new_products'),
    path('log-in/', LoginUserView.as_view(), name='auth'),
    path('sign-up/', register_user_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('account/', account_view, name='account'),
    path('account/change', account_change, name='change_account'),
    path('wishlist/', WishlistProducts.as_view(), name='wishlist'),
    path('action/wishlist/<int:pk>', add_remove_wishlist, name='action_wishlist'),
    path('action/review/', review_product, name='action_review'),
    path('cart/', cart_view, name='cart'),
    path('action/cart/<int:pk>/<str:action>/', add_or_remove_cart, name='action_cart'),
    path('action/cart/<str:action>/', alter_cart, name='alter_cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('action/estimate/', estimate_delivery, name='estimate_delivery'),
    path('payment/', create_checkout_session, name='payment'),
    path('success/payment/', success_payment_view, name='success'),
    path('compare/model/<slug:slug>', SameModel.as_view(), name='compare'),
    path('brand/<slug:slug>', ManufacturerPage.as_view(), name='brand'),
    # path('action/cart/<int:pk>/<str:action>/<int:quanitity>/', add_or_remove_cart, name='action_cart'),
    # path('company/<slug:slug>/', CategoryView.as_view(), name='category')

]