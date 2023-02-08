#
# Copyright (C) 2018,2019 Joar Heimonen
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

import django.http
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render
from django.template import Context, Template

from nav.modulemanager import getTemplate, getTools, getModules
from nav.django.context_processors import account_processor
from nav.web.utils import get_navpath_root

# get template
listtemp = getTemplate("listmodules", "list.html")


# create a view class
class ListView(View):
    # create a get method
    def get(self, request):

        # This is boilerplate and should be added to the modulemanager
        data = {
            **account_processor(request),
            **{"STATIC_URL": "../static/"},
            **{"navpath": [get_navpath_root(), ("list",)]},
            **{"modules": getModules()},
        }

        # return a response
        return HttpResponse(
            listtemp.render(Context(data)),
        )
