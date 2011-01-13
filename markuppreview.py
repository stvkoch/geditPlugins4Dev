# -*- coding: utf-8 -*-

#  markuppreview.py - Gedit plugin for viewing HTML rendering of various 
#                     markup languages, especially reStructured Text
#  
#  Copyright (C) 2007 - Matt Dorn <matt_dorn@yahoo.com>
#  Portions (c) 2005 - Michele Campeotto
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#   
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#   
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

import gtk
import gedit
from gettext import gettext as _
import gtkhtml2

HAS_RST = True
HAS_TEXTILE = True
HAS_MARKDOWN = True

try:
    from docutils.core import publish_string, default_description
except:
    HAS_RST = False

try:
    import textile
except:
    HAS_TEXTILE = False

try:
    import markdown
except:
    HAS_MARKDOWN = False
    
HTML_TEMPLATE = """<html><head><style type="text/css">
body { background-color: #fff; padding: 8px; }
p, div { margin: 0em; }
p + p, p + div, div + p, div + div { margin-top: 0.8em; }
blockquote { padding-left: 12px; padding-right: 12px; }
pre { padding: 12px; }
</style></head><body>%s</body></html>"""    

class MarkupPreviewWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin

    def __del__(self):
        self._window = None
        self._plugin = None
    
    def deactivate(self):
        pass
        

    def update_ui(self):
        pass


class MarkupPreviewPlugin(gedit.Plugin):
    WINDOW_DATA_KEY = "MarkupPreviewPluginWindowData"

    ui_str = """<ui>
    <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
    <placeholder name="ToolsOps_2">
            <menuitem name="MarkupPreview" action="MarkupPreview"/>
            <menu name="MarkupLanguage" action="MarkupLanguage">
              <menuitem action="HTMLPrev"/>
              <menuitem action="RSTPrev"/>
              <menuitem action="MarkdownPrev"/>
              <menuitem action="TextilePrev"/>
            </menu>
    </placeholder>
    </menu>
    </menubar>
    </ui>
    """

    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        helper = MarkupPreviewWindowHelper(self, window)
        window.set_data(self.WINDOW_DATA_KEY, helper)
        self._insert_menu(window)
        langs = ('RST', 'Markdown', 'Textile')        
        for lang in langs:
            # only make active the langs with available modules
            const = eval('HAS_' + lang.upper())
            action = self._action_group.get_action(lang + 'Prev')
            action.set_sensitive(const)

        # Store data in the window object
        windowdata = dict()
        window.set_data("MarkupPreviewData", windowdata)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_property("hscrollbar-policy",gtk.POLICY_AUTOMATIC)
        scrolled_window.set_property("vscrollbar-policy",gtk.POLICY_AUTOMATIC)
        scrolled_window.set_property("shadow-type",gtk.SHADOW_IN)

        html_view = gtkhtml2.View()
        html_doc = gtkhtml2.Document()
        html_view.set_document(html_doc)

        html_doc.clear()
        html_doc.open_stream("text/html")
        html_doc.write_stream(HTML_TEMPLATE % ("",))
        html_doc.close_stream()

        scrolled_window.set_hadjustment(html_view.get_hadjustment())
        scrolled_window.set_vadjustment(html_view.get_vadjustment())
        scrolled_window.add(html_view)
        scrolled_window.show_all()

        bottom = window.get_bottom_panel()
        image = gtk.Image()
        image.set_from_icon_name("gnome-mime-text-html", gtk.ICON_SIZE_MENU)
        bottom.add_item(scrolled_window, "Markup Preview", image)
        windowdata["bottom_panel"] = scrolled_window
        windowdata["html_doc"] = html_doc

        
    
    def deactivate(self, window):
        window.get_data(self.WINDOW_DATA_KEY).deactivate()        
        window.set_data(self.WINDOW_DATA_KEY, None)
        self._remove_menu(window)
        
    def update_ui(self, window):
        window.get_data(self.WINDOW_DATA_KEY).update_ui()
        manager = window.get_ui_manager()
        doc = window.get_active_document()
        if doc is not None:
            if doc.get_mime_type() == 'text/restructured':
                # Automatically set the RST radio button as the active one if we 
                # know the document is RST, based on MIME type
                widget = manager.get_widget('/MenuBar/ToolsMenu/ToolsOps_2/MarkupLanguage/RSTPrev')
                widget.set_active(True)
            else:
                # must be HTML
                widget = manager.get_widget('/MenuBar/ToolsMenu/ToolsOps_2/MarkupLanguage/HTMLPrev')
                widget.set_active(True)                
            # TODO: If anyone actually uses mime types for Textile and
            # Markdown, they can extend the logic here



    def _insert_menu(self, window):
        # Get the GtkUIManager
        manager = window.get_ui_manager()

        # Create a new action group
        self._action_group = gtk.ActionGroup("ExamplePyPluginActions")
        #self._action_group.add_actions([("ExamplePy", None, _("Clear document"),
        #                                 None, _("Clear the document"),
        #                                 self.on_clear_document_activate)])

        # Create actions
        self._action_group.add_actions([('MarkupPreview', 
                                         None,
                                         _('_Markup Preview'), 
                                         '<Control><Shift>M', 
                                         _('Update the HTML preview'), 
                                         lambda x, y: self.update_preview(y)),
                                         ('MarkupLanguage', 
                                          None, 
                                          _('Markup Language'),
                                          None,
                                          _('Select the markup language to render'))
                                     ], window)

        # Create some RadioActions
        self._action_group.add_radio_actions([('HTMLPrev', None, _('HTML'), None, _('Set preview mode to HTML'), 0),
                                       ('RSTPrev', None, _('reStructuredText'), None, _('Set preview mode to reStructuredText'), 1),
                                       ('MarkdownPrev', None, _('Markdown'), None, _('Set preview mode to Markdown'), 2),
                                       ('TextilePrev', None, _('Textile'), None, _('Set preview mode to Textile'), 3),
                                       ], 0, None)

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)
        
        # Merge the UI
        self._ui_id = manager.add_ui_from_string(self.ui_str)
    

    def _remove_menu(self, window):
        # Get the GtkUIManager
        manager = window.get_ui_manager()

        # Remove the ui
        manager.remove_ui(self._ui_id)
        
        # Remove the action group
        manager.remove_action_group(self._action_group)
        
        # Make sure the manager updates
        manager.ensure_update()
        
    def update_preview(self, window):

        windowdata = window.get_data("MarkupPreviewData")

        view = window.get_active_view()
        if not view:
            return

        doc = view.get_buffer()
        
        start = doc.get_start_iter()
        end = doc.get_end_iter()
        
        if doc.get_selection_bounds():
            start = doc.get_iter_at_mark(doc.get_insert())
            end = doc.get_iter_at_mark(doc.get_selection_bound())
        
        text = doc.get_text(start, end)
        if len(text) < 5:
            # TODO: For some reason, if the buffer contains no more than 2 or 3 
            # characters, GEdit crashes with the following message:
            # *** glibc detected *** double free or corruption (fasttop): 0x083da8d8 ***            
            html = HTML_TEMPLATE % ("",)
        else:
            # Render HTML based on which markup lang selected
            path = '/MenuBar/ToolsMenu/ToolsOps_2/MarkupLanguage'
            manager = window.get_ui_manager()
            # TODO: there must be a way to get the selected value
            widget_html = manager.get_widget(path + '/HTMLPrev')                
            widget_rst = manager.get_widget(path + '/RSTPrev')
            widget_markdown = manager.get_widget(path + '/MarkdownPrev')
            widget_textile = manager.get_widget(path + '/TextilePrev')
            if widget_rst.get_active():
                # reStructured Text
                html =  publish_string(text, writer_name='html')
            elif widget_markdown.get_active():
                # Markdown
                html = HTML_TEMPLATE % (markdown.markdown(text),)
            elif widget_textile.get_active():
                # Textile
                html = HTML_TEMPLATE % (textile.textile(text),)
            else:
                # must be HTML
                html = text

        
        p = windowdata["bottom_panel"].get_placement()
        
        html_doc = windowdata["html_doc"]
        html_doc.clear()
        html_doc.open_stream("text/html")
        html_doc.write_stream(html)
        html_doc.close_stream()
        
        windowdata["bottom_panel"].set_placement(p)