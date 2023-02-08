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
