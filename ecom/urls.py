
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
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)