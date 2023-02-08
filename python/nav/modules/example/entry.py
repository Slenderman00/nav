from nav.modulemanager import moduletemplate
from nav.web.webfront.utils import Tool

class module(moduletemplate):
    def __init__(self):
        super().__init__()
        self.name = "example"
        self.version = "0.0"
        self.description = "Example plugin"
        self.author = "John Doe"
        self.email = ""
        self.urls = "nav.modules.example.urls"
        self.urlprefix = "example"
        self.tool = Tool(
            name="Example",
            uri="/example/",
            icon="/example/static/icon.png",
            description="Example plugin",
            priority=0,
            display=True,
        )

