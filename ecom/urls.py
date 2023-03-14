
from django.contrib import admin
from django.urls import path
from shop.views import *

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',homepage,name="homepage"),
    path("category/<slug>/", filterProduct, name="filter"),
    path('search/', search, name="search"),
    path("product/<slug>/",viewProduct, name="viewProduct"),
    path('login/',login,name="login"),
    path('register/',register,name="register"),
    path("signout/",signout,name="logout"),
    path("add-to-cart/<slug>/",addToCart, name="addCart"),
    path("remove-from-cart/<slug>/",removeFromCart, name="removeCart"),
    path("cart/",myCart,name="cart"),
    path("add-coupon/",addCoupon,name="addCoupon"),
    path("remove-coupon/",removeCoupon,name="removeCoupon"),
    path("checkout/",checkout,name="checkout"),
    path("checkout-with-save/",checkoutWithSaveAddress,name="checkoutWithSaveAddress"),
] 


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)