from nav.pluginmanager import plugintemplate
from nav.web.webfront.utils import Tool

class plugin(plugintemplate):
    def __init__(self):
        super().__init__()
        self.name = "example"
        self.version = "1.0"
        self.description = "Example plugin"
        self.author = "John Doe"
        self.email = ""
        self.urls = "nav.plugins.example.urls"
        self.entrypoint = "nav.plugins.example.entry"
        self.urlprefix = "example"
        self.tool = Tool(
            name="Example",
            uri="/example/",
            icon="",
            description="Example plugin",
            priority=0,
            display=True,
        )

