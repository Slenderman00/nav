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

from django.urls import re_path
from nav.modules.jobman.view import JobmanView, JobmanEditView

urlpatterns = [
    re_path(r"^$", JobmanView.as_view(), name="jobman"),
    re_path(r"^edit/(?P<job_id>\d+)/$", JobmanEditView.as_view(), name="jobman_edit"),
]
