import django.http
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.template import Context, Template

from nav.modulemanager import getTemplate

# get template
template1 = getTemplate("example", "template1.html")


# create a view class
class ExampleView(View):
    # create a get method
    def get(self, request):
        # return a response
        return HttpResponse(
            template1.render(Context()),
        )
