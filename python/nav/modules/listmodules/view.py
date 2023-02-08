import django.http
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.template import Context, Template

from nav.modulemanager import getTemplate, getTools, getModules
from nav.django.context_processors import account_processor
from nav.web.utils import get_navpath_root

#get template
listtemp = getTemplate('listmodules', 'list.html')


# create a view class
class ListView(View):
    # create a get method
    def get(self, request):
        
        #This is boilerplate and should be added to the modulemanager
        data = { 
                **account_processor(request), 
                **{'STATIC_URL': '../static/'},  
                **{'navpath': [get_navpath_root(), ('list', )]}, 
                **{'modules': getModules()},
                
            }

        # return a response
        return HttpResponse(listtemp.render(Context(data)), )
