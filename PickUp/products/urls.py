
from django.urls import path, re_path
from django.conf.urls import url

from .views import (
        ProductListView, 
        ProductDetailSlugView,
        )
app_name = 'products'
urlpatterns = [
    re_path(r'^$', ProductListView.as_view(),name='list'), 
    re_path(r'^(?P<slug>\w+)/$', ProductDetailSlugView.as_view(),name="detail"),
]