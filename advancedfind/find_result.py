# -*- encoding:utf-8 -*-


# find_result.py
#
#
# Copyright 2010 swatch
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#


import sys
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

import gedit
import os.path
import urllib
#import pango
import re


class FindResultView(gtk.HBox):
	def __init__(self, window):
		gtk.HBox.__init__(self)
		self._window = window
		
		# initialize find result treeview
		self.findResultTreeview = gtk.TreeView()
		self.findResultTreeview.append_column(gtk.TreeViewColumn("line", gtk.CellRendererText(), text=1))
		self.findResultTreeview.append_column(gtk.TreeViewColumn("content", gtk.CellRendererText(), text=2))
		#self.findResultTreeview.append_column(gtk.TreeViewColumn("result_start", gtk.CellRendererText(), text=4))
		#self.findResultTreeview.append_column(gtk.TreeViewColumn("result_len", gtk.CellRendererText(), text=5))
		self.findResultTreeview.append_column(gtk.TreeViewColumn("uri", gtk.CellRendererText(), text=6))
		self.findResultTreeview.set_headers_visible(False)
		self.findResultTreeview.set_rules_hint(True)
		self.findResultTreemodel = gtk.TreeStore(int, str, str, object, int, int, str)
		self.findResultTreemodel.set_sort_column_id(0, gtk.SORT_ASCENDING)
		self.findResultTreeview.connect("cursor-changed", self.on_findResultTreeview_cursor_changed_action)
		self.findResultTreeview.set_model(self.findResultTreemodel)

		# initialize scrolled window
		scrollWindow = gtk.ScrolledWindow()
		scrollWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scrollWindow.add(self.findResultTreeview)
		
		# put a separator
		v_separator1 = gtk.VSeparator()
		
		# initialize button box
		v_box = gtk.VBox()
		v_buttonbox = gtk.VButtonBox()
		v_buttonbox.set_layout(gtk.BUTTONBOX_END)
		v_buttonbox.set_spacing(5)
		self.selectNextButton = gtk.Button(_("Next"))
		self.selectNextButton.connect("clicked", self.on_selectNextButton_clicked_action)
		#self.findAgainButton = gtk.Button("Find again")
		#self.findAgainButton.connect("clicked", self.on_findAgainButton_clicked_action)
		self.expandAllButton = gtk.Button(_("Expand All"))
		self.expandAllButton.connect("clicked", self.on_expandAllButton_clicked_action)
		self.collapseAllButton = gtk.Button(_("Collapse All"))
		self.collapseAllButton.connect("clicked", self.on_collapseAllButton_clicked_action)
		self.clearHighlightButton = gtk.Button(_("Clear Highlight"))
		self.clearHighlightButton.connect("clicked", self.on_clearHightlightButton_clicked_action)
		self.clearButton = gtk.Button(_("Clear"))
		self.clearButton.connect("clicked", self.on_clearButton_clicked_action)
		#self.closeButton = gtk.Button("Close")
		#self.closeButton.connect("clicked", self.on_closeButton_clicked_action)
		v_buttonbox.pack_start(self.selectNextButton, False, False, 5)
		#v_buttonbox.pack_start(self.findAgainButton, False, False, 5)
		v_buttonbox.pack_start(self.expandAllButton, False, False, 5)
		v_buttonbox.pack_start(self.collapseAllButton, False, False, 5)
		v_buttonbox.pack_start(self.clearHighlightButton, False, False, 5)
		v_buttonbox.pack_start(self.clearButton, False, False, 5)
		#v_buttonbox.pack_start(self.closeButton, False, False, 5)
		v_box.pack_end(v_buttonbox, False, False, 5)
		
		#self._status = gtk.Label()
		#v_box.pack_start(self._status, False)
		
		self.pack_start(scrollWindow, True, True, 5)
		self.pack_start(v_separator1, False, False)
		self.pack_start(v_box, False, False, 5)
		
		self.show_all()
		
	def on_findResultTreeview_cursor_changed_action(self, object):
		model, it = object.get_selection().get_selected()
		if not it:
			return
		
		try:
			line = int(model.get_value(it, 1)[5:-2])
		except:
			return
		
		tab = model.get_value(it, 3)
		result_start = model.get_value(it, 4)
		result_len = model.get_value(it, 5)
		#uri = model.get_value(it, 6)
		
		parent_it = model.iter_parent(it)
		if parent_it:
			uri = "file://" + urllib.pathname2url(model.get_value(parent_it, 6).encode('utf-8'))
		else:
			uri = ""
			
		if uri == "":
			return
		
		# Tab wasn't passed, try to find one		
		if not tab:
			for doc in self._window.get_documents():
				if doc.get_uri() == uri:
					tab = gedit.tab_get_from_document(doc)					
			
		# Still nothing? Open the file then
		if not tab:
			tab = self._window.create_tab_from_uri(uri, None, line, False, False)
			
		if tab:
			self._window.set_active_tab(tab)
			doc = tab.get_document()
			view = tab.get_view()
			if result_len > 0:
				doc.select_range(doc.get_iter_at_offset(result_start), doc.get_iter_at_offset(result_start + result_len))
			
			view.scroll_to_cursor()

	#'''
	def on_selectNextButton_clicked_action(self, object):
		path, column = self.findResultTreeview.get_cursor()
		it = self.findResultTreemodel.get_iter(path)
		if self.findResultTreemodel.iter_has_child(it):
			self.findResultTreeview.expand_row(path, True)
			it1 = self.findResultTreemodel.iter_children(it)
		else:
			it1 = self.findResultTreemodel.iter_next(it)
			
		if not it1:
			it1 = self.findResultTreemodel.iter_parent(it)
			it2 = self.findResultTreemodel.iter_next(it1)
			if not it2:
				it2 = self.findResultTreemodel.iter_parent(it1)
				it3 = self.findResultTreemodel.iter_next(it2)
				path = self.findResultTreemodel.get_path(it3)
			else:
		 		path = self.findResultTreemodel.get_path(it2)
		else:
			path = self.findResultTreemodel.get_path(it1) 
		self.findResultTreeview.set_cursor(path, column, False)
	#'''

	'''
	def on_findAgainButton_clicked_action(self, object):
		pass
	#'''
	
	def on_clearHightlightButton_clicked_action(self, object):
		for doc in self._window.get_documents():
			start, end = doc.get_bounds()
			if doc.get_tag_table().lookup('result_highlight') == None:
				tag = doc.create_tag("result_highlight", foreground='yellow', background='red')
			doc.remove_tag_by_name('result_highlight', start, end)
		
	def on_expandAllButton_clicked_action(self, object):
		self.findResultTreeview.expand_all()
		
	def on_collapseAllButton_clicked_action(self, object):
		self.findResultTreeview.collapse_all()
		
	def on_clearButton_clicked_action(self, object):
		self.clear_find_result()
		'''
		for doc in self._window.get_documents():
			start, end = doc.get_bounds()
			if doc.get_tag_table().lookup('result_highlight') == None:
				tag = doc.create_tag("result_highlight", foreground='yellow', background='red')
			doc.remove_tag_by_name('result_highlight', start, end)
		#'''

	'''
	def on_closeButton_clicked_action(self, boject):
		self._window.get_bottom_panel().set_property("visible", False)
	#'''

	def append_find_pattern(self, pattern, replace_flg = False, replace_text = None):
		self.findResultTreeview.collapse_all()
		idx = self.findResultTreemodel.iter_n_children(None)
		header = '#' + str(idx) + ' - '
		if replace_flg == True:
			it = self.findResultTreemodel.append(None, [idx, header + 'Replace \"' + pattern + '\" with \"' + replace_text + ' \"', '', None, 0, 0, ''])
		else:
			it = self.findResultTreemodel.append(None, [idx, header + 'Search \"' + pattern + '\"', '', None, 0, 0, ''])
		return it
	
	def append_find_result_filename(self, parent_it, filename, uri):
		it = self.findResultTreemodel.append(parent_it, [0, filename, '', None, 0, 0, uri])
		return it
		
	def append_find_result(self, parent_it, line, text, tab, result_offset_start = 0, result_len = 0, uri = ""):
		self.findResultTreemodel.append(parent_it, [int(line), 'Line ' + line + ': ', text, tab, result_offset_start, result_len, uri])
		
	def show_find_result(self):
		path = str(self.findResultTreemodel.iter_n_children(None) - 1)
		self.findResultTreeview.expand_row(path, True)
		pattern_it = self.findResultTreemodel.get_iter(path)
		#file_it = self.findResultTreemodel.iter_nth_child(pattern_it, 0)
		#cursor_it = self.findResultTreemodel.iter_nth_child(file_it, 0)
		#self.findResultTreeview.set_cursor(self.findResultTreemodel.get_path(cursor_it))
		self.findResultTreeview.set_cursor(self.findResultTreemodel.get_path(pattern_it))
		
		file_cnt = self.findResultTreemodel.iter_n_children(pattern_it)
		total_hits = 0
		for i in range(0, file_cnt):
			it1 = self.findResultTreemodel.iter_nth_child(pattern_it, i)
			hits_cnt = self.findResultTreemodel.iter_n_children(it1)
			total_hits += hits_cnt
			self.findResultTreemodel.set_value(it1, 2, str(hits_cnt) + ' hits')
		self.findResultTreemodel.set_value(pattern_it, 2, str(total_hits) + ' hits in ' + str(file_cnt) + ' files')
		
	def clear_find_result(self):
		self.findResultTreemodel.clear()
	



if __name__ == "__main__":
	view = FindResultView(None)
	window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	window.add(view)
	window.show_all()
	gtk.main()


