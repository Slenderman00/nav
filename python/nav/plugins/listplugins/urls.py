from django.urls import re_path
from nav.plugins.listplugins.view import ListView

urlpatterns = [
    re_path(r'^$', ListView.as_view(), name='List Plugins'),
]