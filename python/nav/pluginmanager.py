#!/usr/bin/env python
#
# Copyright (C) 2022 Uninett AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

from pathlib import Path
import importlib
import os
import nav
from django.urls import re_path, include
from django.conf.urls import url
import django.http
from django.http import HttpResponse, FileResponse
from django.views.generic import View
from django.shortcuts import render
from django.http import Http404
from django.template import Template

PLUGIN_DIR = Path(os.path.dirname(nav.__file__), 'plugins')

def getTemplate(pluginName, path):
    pluginPath = Path(PLUGIN_DIR, pluginName, 'templates')
    templatePath = Path(pluginPath, path)
    if templatePath.is_file():
        return Template(Path(templatePath).read_text())

def getTools():
    tools = []
    for plugin in getPlugins():
        tools.append(plugin.tool)
    return tools

#TODO: implement some sort of database and interface to allow disabling and enabling of plugins
def getPlugins():
    plugins = []
    for plugin in PLUGIN_DIR.iterdir():
        if plugin.is_dir():
            if "__" not in plugin.name: 
                plugins.append((importlib.import_module(f'nav.plugins.{plugin.name}.entry')).plugin())
    return plugins

class pluginmanager:
    def __init__(self):
        self.plugins = getPlugins()
        
    def getUrlPatterns(self):
        patterns = []
        for plugin in self.plugins:
            try:
                patterns.append(plugin.returnPath())
                patterns.append(plugin.returnStaticContentPath())
            except ImportError:
                pass
        return patterns

class plugintemplate:
    def __init__(self):
        self.name = None
        self.urlprefix = None
        self.version = None
        self.description = None
        self.author = None
        self.email = None
        self.entrypoint = None
        self.urls = None
        self.tool = None

    def getEntryPoint(self):
        return self.entrypoint
    
    def returnPath(self):
        path = re_path(r'^%s/' % self.urlprefix, include(self.urls))
        return path

    #python badness, but it works. might be replaced with a lambda expression
    def returnStaticContentPath(self):
        path = url(r'^%s/' % self.urlprefix + r'static', self.returnStaticContentView(self).as_view(), name='staticContent')
        return path

    #since apache is serving the static content, we need to pretend that we are apache
    def returnStaticContentView(self, plugin):
        class staticContentView(View):
            def __init__(self):
                pass
            
            def getFile(self, path):
                #TODO: make sure path is not escaping the plugin directory
                path = Path(PLUGIN_DIR, plugin.name, 'static', path.split('/static/')[1])
                if path.is_file():
                    return open(path, 'r')
                return False
            

            def get(self, request):
                file = self.getFile(request.path)
                if file:
                    return FileResponse(file)
                else:
                    raise Http404("File not found")
        return staticContentView