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

from nav.modulemanager import moduletemplate
from nav.web.webfront.utils import Tool


class module(moduletemplate):
    def __init__(self):
        super().__init__()
        self.name = "example"
        self.version = "0.0"
        self.description = "Example module"
        self.author = "John Doe"
        self.email = "johndoe@mail.url"
        self.urls = "nav.modules.example.urls"
        self.urlprefix = "example"
        self.tool = Tool(
            name="Example Module",
            uri="/example/",
            icon="/example/static/icon.png",
            description="Example module",
            priority=0,
            display=True,
        )
