from django.urls import re_path
from nav.modules.listmodules.view import ListView

urlpatterns = [
    re_path(r'^$', ListView.as_view(), name='List Plugins'),
]