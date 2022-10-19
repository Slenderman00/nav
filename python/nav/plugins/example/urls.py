from django.conf.urls import url
from nav.plugins.example.view import ExampleView

urlpatterns = [
    url(r'^$', ExampleView.as_view(), name='example'),
]