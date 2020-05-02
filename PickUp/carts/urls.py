
from django.urls import path, re_path
from django.conf.urls import url

from .views import (
        cart_home, 
        cart_update,
        checkout_home,
        checkout_done_view
        )
app_name = 'carts'
urlpatterns = [
    re_path(r'^$', cart_home,name='home'), 
    re_path(r'^update/$', cart_update,name="update"),
     re_path(r'^checkout/success$', checkout_done_view,name="success"),
     re_path(r'^checkout/$', checkout_home,name="checkout"),
]