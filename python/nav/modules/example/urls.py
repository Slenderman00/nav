from django.urls import re_path
from nav.modules.example.view import ExampleView

urlpatterns = [
    re_path(r"^$", ExampleView.as_view(), name="example"),
]
