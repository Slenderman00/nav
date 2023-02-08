from nav.modulemanager import moduletemplate
from nav.web.webfront.utils import Tool

class module(moduletemplate):
    def __init__(self):
        super().__init__()
        self.name = "listmodules"
        self.version = "1.0"
        self.description = "A list of all installed modules"
        self.author = "Joar Heimonen"
        self.email = "joarheimonen@live.no"
        self.urls = "nav.modules.listmodules.urls"
        self.urlprefix = "list"
        self.tool = Tool(
            name="List Modules",
            uri="/list/",
            icon="/list/static/icon.png",
            description=self.description,
            priority=0,
            display=True,
        )

