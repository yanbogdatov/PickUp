
from django.urls import path, re_path
from django.conf.urls import url

from .views import (
        SearchProductView, 
        ) 
app_name = 'search'
urlpatterns = [
    re_path(r'^$', SearchProductView.as_view(), name='query'), 
]