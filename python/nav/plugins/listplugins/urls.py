from django.conf.urls import url
from nav.plugins.listplugins.view import ListView

urlpatterns = [
    url(r'^$', ListView.as_view(), name='List Plugins'),
]