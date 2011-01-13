# -*- encoding:utf-8 -*-


# findadvance.py
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



import gtk
import gedit
import os.path
import os
import fnmatch
import subprocess
import urllib
import re
#import pango

from advancedfind_ui import AdvancedFindUI
from find_result import FindResultView
import config_manager


import gettext
APP_NAME = 'advancedfind'
LOCALE_DIR = '/usr/share/locale'
#LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
#if not os.path.exists(LOCALE_DIR):
#	LOCALE_DIR = '/usr/share/locale'
gettext.install(APP_NAME, LOCALE_DIR, unicode=True)



# Menu item example, insert a new item in the Edit menu
ui_str = """<ui>
	<menubar name="MenuBar">
		<menu name="SearchMenu" action="Search">
			<placeholder name="SearchOps_0">
				<menuitem name="advanced_find_active" action="advanced_find_active"/>
				<menuitem name="select_find_next" action="select_find_next"/>
				<menuitem name="select_find_previous" action="select_find_previous"/>
			</placeholder>
		</menu>
	</menubar>
</ui>
"""


class AdvancedFindWindowHelper:
	def __init__(self, plugin, window):
		self._window = window
		self._plugin = plugin
		self.find_dialog = None
		self.find_list = []
		self.replace_list = []
		self.filter_list = []
		self.path_list = []
		self.current_search_pattern = ""
		self.current_replace_text = ""
		#self.current_file_pattern = ""
		#self.current_path = ""
		self.forwardFlg = True
		self.scopeFlg = 0
		
		'''
		self.result_highlight_tag = gtk.TextTag('result_highlight')
		self.result_highlight_tag.set_properties(foreground='yellow',background='red')
		self.result_highlight_tag.set_property('family', 'Serif')
		self.result_highlight_tag.set_property('size-points', 12)
		self.result_highlight_tag.set_property('weight', pango.WEIGHT_BOLD)
		self.result_highlight_tag.set_property('underline', pango.UNDERLINE_DOUBLE)
		self.result_highlight_tag.set_property('style', pango.STYLE_ITALIC)
		#'''
		
		configfile = os.path.join(os.path.dirname(__file__), "config.xml")
		self.config_manager = config_manager.ConfigManager(configfile)
		self.options = self.config_manager.load_configure('search_option')
		for key in self.options.keys():
			if self.options[key] == 'True':
				self.options[key] = True
			elif self.options[key] == 'False':
				self.options[key] = False
		self.shortcuts = self.config_manager.load_configure('shortcut')
		self.result_highlight = self.config_manager.load_configure('result_highlight')

		self._results_view = FindResultView(window)
		self._window.get_bottom_panel().add_item(self._results_view, _("Advanced Find/Replace"), "gtk-find-and-replace")
		
		self.msgDialog = gtk.MessageDialog(self._window, 
						gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
						gtk.MESSAGE_INFO,
						gtk.BUTTONS_CLOSE,
						None)

		# Insert menu items
		self._insert_menu()

	def deactivate(self):
		# Remove any installed menu items
		self._remove_menu()

		self._window = None
		self._plugin = None
		self.find_dialog = None
		self.find_list = None
		self.replace_list = None
		self.filter_list = None
		self.path_list = None
		self._result_view = None
		
		self.config_manager.update_config_file(self.config_manager.config_file, 'search_option', self.options)
		#self.config_manager.update_config_file(self.config_manager.config_file, 'shortcut', self.shortcuts)
		self.config_manager.update_config_file(self.config_manager.config_file, 'result_highlight', self.result_highlight)
	
	def _insert_menu(self):
		# Get the GtkUIManager
		manager = self._window.get_ui_manager()

		# Create a new action group
		self._action_group = gtk.ActionGroup("AdvancedFindReplaceActions")
		self._action_group.add_actions( [("advanced_find_active", None, _("Advanced Find/Replace"), self.shortcuts['ACTIVATE'], _("Advanced Find/Replace"), self.advanced_find_active),
										("select_find_next", None, _("Select and Find Next"), self.shortcuts['SELECT_FIND_NEXT'], _("Select and Find Next"), self.select_find_next),
										("select_find_previous", None, _("Select and Find Previous"), self.shortcuts['SELECT_FIND_PREVIOUS'], _("Select and Find Previous"), self.select_find_previous)]) 

		# Insert the action group
		manager.insert_action_group(self._action_group, -1)

		# Merge the UI
		self._ui_id = manager.add_ui_from_string(ui_str)

	def _remove_menu(self):
		# Get the GtkUIManager
		manager = self._window.get_ui_manager()

		# Remove the ui
		manager.remove_ui(self._ui_id)

		# Remove the action group
		manager.remove_action_group(self._action_group)

		# Make sure the manager updates
		manager.ensure_update()

	def update_ui(self):
		self._action_group.set_sensitive(self._window.get_active_document() != None)
		
	def show_message_dialog(self, dlg, text):
		dlg.set_property('text', text)
		dlg.run()
		dlg.hide()
		
	def advanced_find_active(self, action):
		doc = self._window.get_active_document()
		if not doc:
			return
			
		try:
			start, end = doc.get_selection_bounds()
			search_text = unicode(doc.get_text(start,end))
		except:
			search_text = self.current_search_pattern

		if self.find_dialog == None:
			self.find_dialog = AdvancedFindUI(self._plugin)
			
		if search_text != "":
			self.find_dialog.findTextEntry.child.set_text(search_text)
		
		if self.current_replace_text != "":
			self.find_dialog.replaceTextEntry.child.set_text(self.current_replace_text)
		'''	
		if self.current_file_pattern != "":
			self.find_dialog.filterComboboxentry.child.set_text(self.current_file_pattern)
			
		if self.current_path != "":
			self.find_dialog.pathComboboxentry.child.set_text(self.current_path)
		#'''

	def create_regex(self, pattern, options):
		if options['REGEX_SEARCH'] == False:
			pattern = re.escape(unicode(pattern, "utf-8"))
		else:
			pattern = unicode(pattern, "utf-8")
		
		if options['MATCH_WHOLE_WORD'] == True:
			pattern = '\\b%s\\b' % pattern
			
		if options['MATCH_CASE'] == True:
			regex = re.compile(pattern)
		else:
			regex = re.compile(pattern, re.IGNORECASE)
		
		return regex
		
	def advanced_find_in_doc(self, doc, search_pattern, options, forward_flg = True, replace_flg = False, around_flg = False):
		if search_pattern == "":
			return
		
		regex = self.create_regex(search_pattern, options)
		
		if doc.get_has_selection():
			selection_start, selection_end = doc.get_selection_bounds()
			match = regex.search(doc.get_text(selection_start, selection_end))
			if match and replace_flg == True:
				if options['REGEX_SEARCH'] == False:
					replace_text = unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8')
				else:
					replace_text = match.expand(unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8'))
				doc.delete_selection(False, False)
				doc.insert_at_cursor(replace_text)
				replace_flg = False
				#return		
			else:			
				if forward_flg == True:
					doc.place_cursor(selection_end)
				else:
					doc.place_cursor(selection_start)
		
		view = self._window.get_active_view()
		if forward_flg == True:
			find_start = doc.get_iter_at_mark(doc.get_insert())
			lines = unicode(doc.get_text(find_start, doc.get_end_iter()), 'utf-8').splitlines(True)
			for line in lines:
				match = regex.search(line)
				if match:
					result_start = doc.get_iter_at_offset(find_start.get_offset() + match.start())
					result_end = doc.get_iter_at_offset(find_start.get_offset() + match.end())
					doc.select_range(result_start, result_end)
					view.scroll_to_cursor()
					
					if replace_flg == True:
						if options['REGEX_SEARCH'] == False:
							replace_text = unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8')
						else:
							replace_text = match.expand(unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8'))
						doc.delete_selection(False, False)
						doc.insert_at_cursor(replace_text)
						replace_end = doc.get_iter_at_mark(doc.get_insert())
						replace_start = doc.get_iter_at_offset(replace_end.get_offset() - len(replace_text))
						doc.select_range(replace_start, replace_end)
						view.scroll_to_cursor()
						
					return
				else:
					find_start = doc.get_iter_at_offset(find_start.get_offset() + len(line))
					
			if options['WRAP_AROUND'] == True and around_flg == False:
				find_start = doc.get_start_iter()
				doc.place_cursor(find_start)
				self.advanced_find_in_doc(doc, search_pattern, options, forward_flg, replace_flg, True)
			else:
				self.show_message_dialog(self.msgDialog, _("Nothing is found."))
					
		else:
			find_end = doc.get_iter_at_mark(doc.get_insert())
			lines = unicode(doc.get_text(doc.get_start_iter(), find_end), 'utf-8').splitlines(True)
			back_lines = []
			for i in range(-1, -1-len(lines), -1):
				back_lines.append(lines[i])
				
			for line in back_lines:
				line_start = doc.get_iter_at_offset(find_end.get_offset() - len(line))
				result = regex.findall(line)
				if result:
					match_pos = 0
					for idx in range(0, len(result)):
						match = regex.search(line[match_pos:])
						result_start = doc.get_iter_at_offset(line_start.get_offset() + match.start() + match_pos)
						result_end = doc.get_iter_at_offset(line_start.get_offset() + match.end() + match_pos)
						match_pos += match.end()
					doc.select_range(result_start, result_end)
					view.scroll_to_cursor()
					
					if replace_flg == True:
						if options['REGEX_SEARCH'] == False:
							replace_text = unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8')
						else:
							replace_text = match.expand(unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8'))
						doc.delete_selection(False, False)
						doc.insert_at_cursor(replace_text)
						replace_end = doc.get_iter_at_mark(doc.get_insert())
						replace_start = doc.get_iter_at_offset(replace_end.get_offset() - len(replace_text))
						doc.select_range(replace_start, replace_end)
						view.scroll_to_cursor()
						
					return
				else:
					doc.place_cursor(doc.get_iter_at_offset(find_end.get_offset() - len(line)))
					find_end = doc.get_iter_at_mark(doc.get_insert())

			if options['WRAP_AROUND'] == True and around_flg == False:
				find_end = doc.get_end_iter()
				doc.place_cursor(find_end)
				self.advanced_find_in_doc(doc, search_pattern, options, forward_flg, replace_flg, True)
			else:
				self.show_message_dialog(self.msgDialog, _("Nothing is found."))
			
				
	def auto_select_word(self):
		doc = self._window.get_active_document()
		if doc.get_has_selection():
			start, end = doc.get_selection_bounds()
			return doc.get_text(start, end)
		else:
			current_iter = doc.get_iter_at_mark(doc.get_insert())
			iter_idx = current_iter.get_line_index()
			line_num = current_iter.get_line()
			lines = doc.get_text(doc.get_start_iter(), doc.get_end_iter()).splitlines(True)
			if lines == []:
				return ""
			line = lines[line_num]
			results = re.findall('[_a-zA-Z][_a-zA-Z0-9]*', line)
			select_text = ''
			match_pos = 0
			for result in results:
				match = re.search(result, line[match_pos:])
				if match:
					if match.start() + match_pos <= iter_idx and iter_idx <= match.end() + match_pos:
						select_text = result
						break
					else:
						match_pos += match.end()
			return select_text
	
	def select_find_next(self, action):
		#print self.auto_select_word()
		self.advanced_find_in_doc(self._window.get_active_document(), self.auto_select_word(), self.options, True, False, False)

	def select_find_previous(self, action):
		#print self.auto_select_word()
		self.advanced_find_in_doc(self._window.get_active_document(), self.auto_select_word(), self.options, False, False, False)

	def advanced_find_all_in_doc(self, parent_it, doc, search_pattern, options, replace_flg = False, selection_only = False):
		if search_pattern == "":
			return
		
		regex = self.create_regex(search_pattern, options)

		self.result_highlight_off(doc)
		start, end = doc.get_bounds()
		text = unicode(doc.get_text(start, end), 'utf-8')
		
		if selection_only == False:
			lines = text.splitlines(True)
			line_number_offset = 1
		else:
			selection_start, selection_end = doc.get_selection_bounds()
			selection_text = unicode(doc.get_text(selection_start, selection_end), 'utf-8')
			lines= selection_text.splitlines(True)
			line_start_offset = selection_start.get_offset()
			#print line_start_offset
			line_number_offset = selection_start.get_line() + 1
			#print line_number_offset

		tree_it = None
		new_text = list(text)
		text_changed = False
		replace_cnt = 0

		for i in range(len(lines)):
			results = regex.findall(lines[i])
			if selection_only == False:
				line_start = doc.get_iter_at_line(i)
			else:
				if i > 0:
					line_start_offset += len(lines[i-1])
				#print line_start_offset
				line_start = doc.get_iter_at_offset(line_start_offset)
				
			if results:
				if not tree_it:
					doc_uri = doc.get_uri()
					if doc_uri == None:
						uri = ''
					else:
						uri = urllib.unquote(doc.get_uri()[7:]).decode('utf-8')
					tree_it = self._results_view.append_find_result_filename(parent_it, doc.get_short_name_for_display(), uri)
				tab = gedit.tab_get_from_document(doc)

				match_pos = 0
				for cnt in range(0, len(results)):
					match = regex.search(lines[i][match_pos:])
					result_offset_start = line_start.get_offset() + match.start() + match_pos
					result_len = len(match.group(0))
					if options['REGEX_SEARCH'] == False:
						replace_text = unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8')
					else:
						replace_text = match.expand(unicode(self.find_dialog.replaceTextEntry.get_active_text(), 'utf-8'))
					replace_text_len = len(replace_text)
					replace_offset = result_len - replace_text_len
					
					if replace_flg == True:
						self._results_view.append_find_result(tree_it, str(line_number_offset + i), lines[i].strip(), tab, result_offset_start - (replace_offset * replace_cnt), replace_text_len)
						replace_start_idx = result_offset_start - (replace_offset * replace_cnt)
						new_text[replace_start_idx:replace_start_idx + result_len] = replace_text
						replace_cnt += 1
						text_changed = True
					else:
						self._results_view.append_find_result(tree_it, str(line_number_offset + i), lines[i].strip(), tab, result_offset_start, result_len)
					match_pos += match.end()
				
		if text_changed == True:
			doc.set_text("".join(new_text))
			
		self.result_highlight_on(tree_it)

	def find_all_in_dir(self, parent_it, dir_path, file_pattern, search_pattern, options, replace_flg = False):
		if search_pattern == "":
			return
		
		d_list = []
		f_list = []
		path_list = []
		
		for root, dirs, files in os.walk(unicode(dir_path, 'utf-8')):
			for d in dirs:
				d_list.append(os.path.join(root, d))	
			for f in files:
				f_list.append(os.path.join(root, f))
		
		if options['INCLUDE_SUBFOLDER'] == True:
			path_list = f_list
		else:
			for f in f_list:
				if os.path.dirname(f) not in d_list:
					path_list.append(f)

		for file_path in path_list:
			if fnmatch.fnmatch(file_path, unicode(file_pattern, 'utf-8')):

				if os.path.isfile(file_path):
					#print file_path
					pipe = subprocess.PIPE
					p1 = subprocess.Popen(["file", "-i", file_path], stdout=pipe)
					p2 = subprocess.Popen(["grep", "text"], stdin=p1.stdout, stdout=pipe)
					output = p2.communicate()[0]
					if output:
						temp_doc = gedit.Document()
						file_uri = "file://" + urllib.pathname2url(file_path.encode('utf-8'))
						temp_doc.load(file_uri, gedit.encoding_get_from_charset('utf-8'), 0, False)
						f_temp = open(file_path, 'r')
						try:
							text = unicode(f_temp.read(), 'utf-8')
						except:
							text = f_temp.read()
						f_temp.close()
						temp_doc.set_text(text)
						
						self.advanced_find_all_in_doc(parent_it, temp_doc, search_pattern, options, replace_flg)

		self._results_view.show_find_result()
		self.show_bottom_panel()
		
	def result_highlight_on(self, file_it):
		if file_it == None:
			return
		if self._results_view.findResultTreemodel.iter_has_child(file_it):
			for n in range(0,self._results_view.findResultTreemodel.iter_n_children(file_it)):
				it = self._results_view.findResultTreemodel.iter_nth_child(file_it, n)
				tab = self._results_view.findResultTreemodel.get_value(it, 3)
				if not tab:
					continue
				
				result_start = self._results_view.findResultTreemodel.get_value(it, 4)
				result_len = self._results_view.findResultTreemodel.get_value(it, 5)
				doc = tab.get_document()
				if doc.get_tag_table().lookup('result_highlight') == None:
					tag = doc.create_tag("result_highlight", foreground=self.result_highlight['FOREGROUND_COLOR'], background=self.result_highlight['BACKGROUND_COLOR'])
				doc.apply_tag_by_name('result_highlight', doc.get_iter_at_offset(result_start), doc.get_iter_at_offset(result_start + result_len))
		
	def result_highlight_off(self, doc):
		start, end = doc.get_bounds()
		if doc.get_tag_table().lookup('result_highlight') == None:
			tag = doc.create_tag("result_highlight", foreground=self.result_highlight['FOREGROUND_COLOR'], background=self.result_highlight['BACKGROUND_COLOR'])
		doc.remove_tag_by_name('result_highlight', start, end)

	def show_bottom_panel(self):
		panel = self._window.get_bottom_panel()
		if panel.get_property("visible") == False:
			panel.set_property("visible", True)
		panel.activate_item(self._results_view)
		
		
		
