# tabulation.py - Tabulation defined per file type.
#
# Copyright (C) 2007 - Nando Vieira
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import gedit
import gconf
import os
import os.path

class TabulationPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self.tabs = {'py': [True, 4], 'rb': [True, 2], 'php': [True, 4]}
    
    def update(self):
        print '[tabulation] calling update'
        self.apply_tabulation()
    
    def activate(self, window):
        for view in window.get_views(): 
            self.connect_handlers(view)

        tab_added_id = window.connect("tab_added", 
                            lambda w, t: self.connect_handlers(t.get_view()))
        window.set_data("TabulationPluginHandlerId", tab_added_id)
        
        #statusbar
        self.window = window
        self.statusbar = window.get_statusbar()
        self.context_id = self.statusbar.get_context_id("Tabulation")
        self.message_id = None

    def deactivate(self, window):
        tab_added_id = window.get_data("TabulationPluginHandlerId")
        window.disconnect(tab_added_id)
        window.set_data("TabulationPluginHandlerId", None)

        for view in window.get_views():
            self.disconnect_handlers(view)

    def connect_handlers(self, view):
        doc = view.get_buffer()
        loaded_id = doc.connect("loaded", self.apply_tabulation, view)
        saved_id  = doc.connect("saved", self.apply_tabulation, view)
        doc.set_data("TabulationPluginHandlerIds", (loaded_id, saved_id))
    
    #~ taken from autotab plugin
    #~ http://code.google.com/p/gedit-autotab/
    def update_status(self):
        view = self.window.get_active_view()
        if view:
            space = view.get_insert_spaces_instead_of_tabs()
            size = view.get_tabs_width()
            message = "%i%s" % (size, space and 'S' or 'T')
        if self.message_id:
            self.statusbar.remove(self.context_id, self.message_id)
        self.message_id = self.statusbar.push(self.context_id, "Tab: %s" % message)
    
    def disconnect_handlers(self, view):
        doc = view.get_buffer()
        loaded_id, saved_id = doc.get_data("TabulationPluginHandlerIds")
        doc.disconnect(loaded_id)
        doc.disconnect(saved_id)
        doc.set_data("TabulationPluginHandlerIds", None)

    def apply_tabulation(self, *args):
        view = self.window.get_active_view()
        doc = view.get_buffer()
        info = os.path.splitext(doc.get_uri())
        ext = info[1][1:].lower()

        if self.tabs.has_key(ext):
            tab_size = int(self.tabs[ext][1])

            if self.tabs[ext][0]:
                use_spaces = True
            else:
                use_spaces = False
        else:
            use_spaces = gconf_get_bool("/apps/gedit-2/preferences/editor/tabs/insert_spaces", False)
            tab_size = gconf_get_int("/apps/gedit-2/preferences/editor/tabs/tabs_size", 4)

        view.set_tabs_width(tab_size)
        view.set_insert_spaces_instead_of_tabs(use_spaces)
        self.update_status()

gconf_client = gconf.client_get_default()
def gconf_get_bool(key, default = False):
    val = gconf_client.get(key)
    if val is not None and val.type == gconf.VALUE_BOOL:
        return val.get_bool()
    else:
        return default

def gconf_get_str(key, default = ""):
    val = gconf_client.get(key)
    if val is not None and val.type == gconf.VALUE_STRING:
        return val.get_string()
    else:
        return default

def gconf_get_int(key, default = 0):
    val = gconf_client.get(key)
    if val is not None and val.type == gconf.VALUE_INT:
        return val.get_int()
    else:
        return default
