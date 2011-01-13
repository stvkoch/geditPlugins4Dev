# Copyright (C) 2007 Vinicius Baggio Fuentes
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.



import gedit
import gtk
import gobject

import pango

from rubydocreader import RubyDocReader

class RubyDocWindowHelper:
    _handler_list = []

################################################################## __init__
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        self._rubydoc = RubyDocReader()
        self._insert_tab()

        # self._connect_keypress(self._window.get_active_view())

################################################################## deactivate
    def deactivate(self):
       ### print "Plugin stopped for",  self._window
        self._side_panel.remove_item(self._box)

        # Disconnect every keypress_handler
        for (handler_id, view) in self._handler_list:
            view.disconnect(handler_id)

        self._window = None
        self._plugin = None


################################################################## update_ui
    def update_ui(self):
        pass
        # Called whenever the window has been changed, etc.

        # connect a keypress_handler
#         view = self._window.get_active_view()
#         self._connect_keypress(view)

################################################################## _create_model
    def _create_model(self):
        list_store = gtk.ListStore(gobject.TYPE_STRING)
        topics = self._rubydoc.get_topics()
        for line in topics:
            line = line.strip()
            iter = list_store.append()
            list_store.set(iter, 0, line)

        return list_store

################################################################## _create_topics_column

    def _create_topics_column(self, treeview):
        model = treeview.get_model()
        column = gtk.TreeViewColumn('Topic', gtk.CellRendererText(), text=0)
        column.set_sort_column_id(0)
        treeview.append_column(column)

################################################################## _insert_tab

    def _insert_tab(self):
        # Load an icon for the panel
        icon = gtk.Image()

        icon.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_SMALL_TOOLBAR)

        # Creates the packing box and the resizeable box
        self._box = gtk.VBox()
        self._box.set_border_width(0)

        paned_box = gtk.VPaned()
        paned_box.set_border_width(5)

        top_box = gtk.VBox()
        top_box.set_border_width(0)

        # create the model and the TreeView
        model = self._create_model()
        self._topics_list = gtk.TreeView(model)
        self._topics_list.set_search_column(0)
        self._create_topics_column(self._topics_list)
        self._topics_list.set_headers_visible(False) # make columns hide

        # Create the searchbox
        self._searchbox = gtk.Entry(max=50)

        # Now use the searchbox to search for elements in the List of topics
        self._topics_list.set_search_entry(self._searchbox)

        # Creates a scrolled window for the help box
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        # Now for the Index
        sw2 = gtk.ScrolledWindow()
        sw2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw2.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw2.set_size_request(-1, 200)

        # Create the textbox
        self._helpbox = gtk.TextView(buffer=None)
        self._helpbox.set_editable(False)
        self._helpbox.set_wrap_mode(gtk.WRAP_WORD)

        #self._helpbox.set_border_width(2)
        self._buffer = self._helpbox.get_buffer()

        # Tags for the textbox
        self._buffer.create_tag("italic", style=pango.STYLE_ITALIC,family="monospace")
        self._buffer.create_tag("underline",underline=pango.UNDERLINE_SINGLE, family="monospace")
        self._buffer.create_tag("bold", weight=pango.WEIGHT_BOLD, family="monospace")
        self._buffer.create_tag("monospace", family="monospace")
        self._buffer.create_tag("blue", foreground="blue", family="monospace")
        self._buffer.create_tag("red", foreground="red", family="monospace")

        # Connect and show them
        sw.add(self._helpbox)
        sw.show()

        sw2.add(self._topics_list)
        sw2.show()

        self._searchbox.show()

        self._helpbox.show()
        self._topics_list.show()

        paned_box.show()
        top_box.show()

        # add them all to the container
        top_box.pack_start(self._searchbox, False)
        top_box.pack_start(sw2, True, True)

        paned_box.add1(top_box)

        paned_box.add2(sw)

        self._box.pack_start(paned_box)

        # Create a new side panel

        # now gets the panel and add stuff to it
        self._side_panel = self._window.get_side_panel()
        self._side_panel.add_item(self._box, "Ruby Doc", icon)
        iter = self._buffer.get_iter_at_offset(0)
        self._buffer.insert_with_tags_by_name(iter, "Please select a topic", "monospace")

        # now connects the event handler for the topics list
        self._topics_list.connect("cursor-changed", self.topic_select_eventhandler)

################################################################## _is_this_ruby

    def _is_this_ruby(self):
        active_document = self._window.get_active_document()

        # returns if there is no active document
        if not active_document:
            return False

        # See if the current document MIME is ruby
        curr_mime = self._window.get_active_document().get_mime_type()
        if curr_mime == "application/x-ruby":
            return True

################################################################## get_selected_word

    # Gets the selected word
    def get_selected_word(self):
        active_document = self._window.get_active_document()
        if not active_document:
            return

        try:
            start, end = active_document.get_selection_bounds()
        except:
            return

        return active_document.get_text(start, end).strip()


################################################################## set_help_text

    def set_help_text(self, text):
        new_text = text
        lt_pos = 0
        gt_pos = 0
        end = False

        self._buffer.set_text("")

        # We should parse it a little to add color etc.
        try:
            # Setup spacing
            new_text = new_text.replace('<p>', '\n  ')
            new_text = new_text.replace('</p>', '\n')

            new_text = new_text.replace('<pre>', '\n')
            new_text = new_text.replace('</pre>', '')

            new_text = new_text.replace('<ul>', '')
            new_text = new_text.replace('</ul>', '')
            new_text = new_text.replace('<li>', '     * ')
            new_text = new_text.replace('</li>', '\n')


            new_text = new_text.replace('<h3>', '\n')


            iter = self._buffer.get_iter_at_offset(0)
#            self._buffer.insert_with_tags_by_name(iter, new_text, "monospace")

            finder = 0
            while not end:
                # Now parse some colors/styles
                new_finder = new_text.find('<', finder)

                if new_finder == -1:
                    # no tags anymore, yay!
                    self._buffer.insert_with_tags_by_name(iter, \
                        new_text[finder+1:], \
                        "monospace" \
                        )
                    end = True
                else:
                    # Check if there is distance from the old finder to the new
                    # if so, add the text to it with no formatting, then add
                    # with formating
                    if finder != new_finder:
                        self._buffer.insert_with_tags_by_name(iter, \
                        new_text[finder+1:new_finder], \
                        "monospace" \
                        )

                        finder = new_finder

                    gt_pos = new_text.find('>', finder)
                    tag = new_text[finder+1:gt_pos]

                    end_of_tagged_text = new_text.find('<', gt_pos)

                    #print tag

                    if tag == "tt":
                        elem = "red"
                    elif tag == "em":
                        elem = "blue"
                    elif tag == "b":
                        elem = "bold"

                   # print new_text[gt_pos+1:end_of_tagged_text]

                    self._buffer.insert_with_tags_by_name(iter, \
                                  new_text[gt_pos+1:end_of_tagged_text], \
                                  elem \
                                )

                    finder = new_text.find('>', end_of_tagged_text)


        except:
            pass

################################################################## topic_select_eventhandler

    # Connects to the selection from the Topics box, so we get the title and
    # asks rubydocreader the topic info
    def topic_select_eventhandler(self, treeview):

        ### Extracts the list string
        ((path,), column) = treeview.get_cursor()
        model = treeview.get_model()
        iter = model.get_iter(path)
        text = model.get_value(iter, 0) # it's always column 0

        self.set_help_text(self._rubydoc.get_help_on(text))



################################################################## _connect_keypress

    # Connects a keypress event. Checks if it isn't already done, and add
    # the handler ID to the list of handlers so it can be deleted later
#     def _connect_keypress(self, view):
#         #checks if this document is a ruby source code
#         if not self._is_this_ruby():
#             return
#         if type(view) == gedit.View:
#             # checks if there is already a handler connected
#             if getattr(view, 'rubydoc_instance', False) == False:
#                 setattr(view, 'rubydoc_instance', self)
#                 handler_id = view.connect('key-press-event', self.keypress_handler)
#                 self._handler_list.append( (handler_id, view) )


################################################################## keypress_handler

#     # Handles the kepress, updating the helpbox
#     def keypress_handler(self, view, event):
#         rubydoc = getattr(view, 'rubydoc_instance', False)
#         if not rubydoc:
#             return

#         buffer = rubydoc.get_helpbox_buffer()
#         sel_word = rubydoc.get_selected_word()

#         if sel_word:
#             buffer.insert(buffer.get_end_iter(), "\n" + sel_word )

################################################################## get_helpbox_buffer

    def get_helpbox_buffer(self):
        return self._buffer
