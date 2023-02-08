from nav.pluginmanager import plugintemplate
from nav.web.webfront.utils import Tool

class plugin(plugintemplate):
    def __init__(self):
        super().__init__()
        self.name = "listmodules"
        self.version = "1.0"
        self.description = "A list of all installed plugins"
        self.author = "Joar Heimonen"
        self.email = ""
        self.urls = "nav.plugins.listplugins.urls"
        self.urlprefix = "list"
        self.tool = Tool(
            name="List Plugins",
            uri="/list/",
            icon="/list/static/icon.png",
            description=self.description,
            priority=0,
            display=True,
        )

