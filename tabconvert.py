'''
I love Python, but indentation drives me nuts.
This plugin adds two entries to the edit menu.
- convert tabs to whitespace
- convert whitespace to tabs

The size of the whitespace is read from the current 
sourceView, ie. from the user preferences.

Basic plugin code stolen from:
http://gnome.org/~pborelli/gedit-plugins/par.py.txt

Copyright (C) 2006 Frederic Back (fredericback@gmail.com)
'''

import gedit
import gtk

class TabConvertPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)

    def convertToWhitespace(self, widget, window):
        doc = window.get_active_document()
        tabsize = window.get_active_view().get_tabs_width()
        start, end = doc.get_bounds()
        text = doc.get_text(start, end)
        text = text.expandtabs(tabsize)

        doc.begin_user_action()
        it = doc.get_iter_at_mark(doc.get_insert())
        line = it.get_line()
        doc.delete(start, end)
        doc.insert(start, text)
        #it = doc.get_iter_at_line_offset(line,0)
        #doc.place_cursor(it)
        #window.get_active_view().scroll_to_iter(it,0.2
        print line

        doc.end_user_action()

    def convertToTabs(self, widget, window):
        ''' Note that only leading tabs will be removed.
            Helps to avoid replacing quoted whitespace. '''
        doc = window.get_active_document()
        tabsize = window.get_active_view().get_tabs_width()
        start, end = doc.get_bounds()
        text = doc.get_text(start, end)

        newlines = []
        for line in text.splitlines():

            # count and remove leading whitespace
            count = 0
            ln = line
            if len(ln) > 0:
                while ln[0] == " ":
                    ln = ln[1:]
                    if len(ln) == 0: break

            # compare length with/without whitespace
            d = len(line)-len(ln) 

            # add whitespace if count doesn't match
            # example: '    hello'  -> '\thello'
            #          '     hello' -> '\t hello'
            ln = (" " * (d-tabsize*(d/tabsize))) + ln

            # add as many tabs as possible
            for i in range(d/tabsize): ln = "\t"+ln

            newlines.append(ln)

        doc.begin_user_action()
        it = doc.get_iter_at_mark(doc.get_insert())
        l = it.get_line()
        doc.delete(start, end)
        doc.insert(start, "\n".join(newlines))
        #it = doc.get_iter_at_line_offset(l,0)
        #doc.place_cursor(it)
        #window.get_active_view().scroll_to_iter(it,0.0)
        doc.end_user_action()   

    def activate(self, window):
        actions = (
            ("tabconvert",None,"Convert Tabs",None,None),
            ("tab2white", gtk.STOCK_INDENT, 
            "Convert tabs to whitespace", None,
            "Convert tabs to whitespace",
            self.convertToWhitespace),
            ("white2tab", gtk.STOCK_INDENT, 
            "Convert whitespace to tabs", None,
            "Convert whitespace to tabs",
            self.convertToTabs)
        )

        # store per window data in the window object
        windowdata = dict()
        window.set_data("TabConverterPluginWindowDataKey", windowdata)

        windowdata["action_group"] = gtk.ActionGroup("GeditTabConverterPluginActions")
        #windowdata["action_group"].set_translation_domain(GETTEXT_PACKAGE)
        windowdata["action_group"].add_actions(actions, window)

        manager = window.get_ui_manager()
        manager.insert_action_group(windowdata["action_group"], -1)
        windowdata["ui_id"] = manager.new_merge_id ()

        submenu = "<ui>\
          <menubar name='MenuBar'>\
            <menu name='EditMenu' action='Edit'>\
              <placeholder name='EditOps_6'>\
                <menu action='tabconvert'>\
                  <menuitem action='white2tab'/>\
                  <menuitem action='tab2white'/>\
                </menu>\
              </placeholder>\
            </menu>\
          </menubar>\
        </ui>"

        manager.add_ui_from_string(submenu)


    def deactivate(self, window):
        windowdata = window.get_data("TabConverterPluginWindowDataKey")
        manager = window.get_ui_manager()
        manager.remove_ui(windowdata["ui_id"])
        manager.remove_action_group(windowdata["action_group"])

    def update_ui(self, window):
        view = window.get_active_view()
        windowdata = window.get_data("TabConverterPluginWindowDataKey")
        windowdata["action_group"].set_sensitive(bool(view and view.get_editable()))
