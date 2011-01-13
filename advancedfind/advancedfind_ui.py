# -*- encoding:utf-8 -*-


# findadvance_ui.py
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

import os.path
import os
#import pango
import re
#import config_manager
import gconf


#gtk.glade.bindtextdomain('advancedfind', os.path.join(os.path.dirname(__file__), 'locale'))
#gtk.glade.bindtextdomain('advancedfind', '/usr/share/locale')
#gtk.glade.textdomain('advancedfind')



class AdvancedFindUI(object):
	def __init__(self, plugin):
		try:
			self._plugin = plugin
			self._instance = self._plugin.get_instance()
			self._window = self._instance._window
		except:
			pass

		gladefile = os.path.join(os.path.dirname(__file__),"FindDialog.glade")
		ui = gtk.Builder()
		ui.set_translation_domain('advancedfind')
		ui.add_from_file(gladefile)
		ui.connect_signals({ "on_findDialog_destroy" : self.on_findDialog_destroy_action,
							
							"on_findButton_clicked" : self.on_findButton_clicked_action,
							"on_replaceButton_clicked" : self.on_replaceButton_clicked_action,
							"on_findAllButton_clicked" : self.on_findAllButton_clicked_action,
							"on_replaceAllButton_clicked" : self.on_replaceAllButton_clicked_action,
							"on_closeButton_clicked" : self.on_closeButton_clicked_action,
							"on_selectPathButton_clicked" : self.on_selectPathButton_clicked_action,
							"on_selectPathDialogOkButton_clicked" : self.on_selectPathDialogOkButton_clicked_action,
							"on_selectPathDialogCancelButton_clicked" : self.on_selectPathDialogCancelButton_clicked_action,
							
							"on_matchWholeWordCheckbutton_toggled" : self.on_matchWholeWordCheckbutton_toggled_action,
							"on_matchCaseCheckbutton_toggled" : self.on_matchCaseCheckbutton_toggled_action,
							"on_wrapAroundCheckbutton_toggled" : self.on_wrapAroundCheckbutton_toggled_action,
							"on_followCurrentDocCheckbutton_toggled" : self.on_followCurrentDocCheckbutton_toggled_action,
							"on_includeSubfolderCheckbutton_toggled" : self.on_includeSubfolderCheckbutton_toggled_action,
							"on_regexSearchCheckbutton_toggled" : self.on_regexSearchCheckbutton_toggled_action,
							
							"on_forwardRadiobutton_toggled" : self.directionRadiobuttonGroup_action,
							"on_backwardRadiobutton_toggled" : self.directionRadiobuttonGroup_action,
							
							"on_currentFileRadiobutton_toggled" : self.scopeRadiobuttonGroup_action,
							"on_allFilesRadiobutton_toggled" : self.scopeRadiobuttonGroup_action,
							"on_allFilesInPathRadiobutton_toggled" : self.scopeRadiobuttonGroup_action,
							"on_currentSelectionRadiobutton_toggled" : self.scopeRadiobuttonGroup_action })

		self.findDialog = ui.get_object("findDialog")
		#self.findDialog.set_keep_above(True)
		self.findDialog.set_transient_for(self._window)

		self.findTextEntry = ui.get_object("findTextComboboxentry")
		#self.findTextListstore = ui.get_object("findTextListstore")
		#find_cell = gtk.CellRendererText()
		#self.findTextEntry.pack_start(find_cell, True)
		#self.findTextEntry.add_attribute(find_cell, 'text', 0)
		self.findTextEntry.set_text_column(0)
		try:
			for find_text in self._instance.find_list:
				self.findTextEntry.append_text(find_text)
		except:
			pass

		self.replaceTextEntry = ui.get_object("replaceTextComboboxentry")
		#self.replaceTextListstore = ui.get_object("replaceTextListstore")
		#replace_cell = gtk.CellRendererText()
		#self.replaceTextEntry.pack_start(replace_cell, True)
		#self.replaceTextEntry.add_attribute(replace_cell, 'text', 0)
		self.replaceTextEntry.set_text_column(0)
		try:
			for replace_text in self._instance.replace_list:
				self.replaceTextEntry.append_text(replace_text)
		except:
			pass
			
		self.filterComboboxentry = ui.get_object("filterComboboxentry")
		self.filterComboboxentry.set_text_column(0)
		self.filterComboboxentry.child.set_text("*")
		#self.filterComboboxentry.append_text("*")
		try:
			for file_filter in self._instance.filter_list:
				self.filterComboboxentry.append_text(file_filter)
		except:
			pass
			
		self.selectPathFilechooserdialog = ui.get_object("selectPathFilechooserdialog")
		
		self.pathComboboxentry = ui.get_object("pathComboboxentry")
		self.pathComboboxentry.set_text_column(0)
		filebrowser_root = self.get_filebrowser_root()
		if filebrowser_root != None and self._instance.options['ROOT_FOLLOW_FILEBROWSER'] == True:
			self.pathComboboxentry.child.set_text(filebrowser_root)
		else:
			self.pathComboboxentry.child.set_text(self.selectPathFilechooserdialog.get_filename())
			
		try:
			for path in self._instance.path_list:
				self.pathComboboxentry.append_text(path)
		except:
			pass
		
		self.matchWholeWordCheckbutton = ui.get_object("matchWholeWordCheckbutton")
		self.matchCaseCheckbutton = ui.get_object("matchCaseCheckbutton")
		self.wrapAroundCheckbutton = ui.get_object("wrapAroundCheckbutton")
		self.followCurrentDocCheckbutton = ui.get_object("followCurrentDocCheckbutton")
		self.includeSubfolderCheckbutton = ui.get_object("includeSubfolderCheckbutton")
		self.regexSearchCheckbutton = ui.get_object("regexSearchCheckbutton")

		self.forwardRadiobutton = ui.get_object("forwardRadiobutton")
		self.backwardRadiobutton = ui.get_object("backwardRadiobutton")
		if self._instance.forwardFlg == True:
			self.forwardRadiobutton.set_active(True)
		else:
			self.backwardRadiobutton.set_active(True)

		self.currentFileRadiobutton = ui.get_object("currentFileRadiobutton")
		self.allFilesRadiobutton = ui.get_object("allFilesRadiobutton")
		self.allFilesInPathRadiobutton = ui.get_object("allFilesInPathRadiobutton")
		self.currentSelectionRadiobutton = ui.get_object("currentSelectionRadiobutton")
		if self._instance.scopeFlg == 0:
			self.currentFileRadiobutton.set_active(True)
		elif self._instance.scopeFlg == 1:
			self.allFilesRadiobutton.set_active(True)
		elif self._instance.scopeFlg == 2:
			self.allFilesInPathRadiobutton.set_active(True)
		elif self._instance.scopeFlg == 3:
			self.currentSelectionRadiobutton.set_active(True)


		self.findButton = ui.get_object("findButton")
		self.replaceButton = ui.get_object("replaceButton")
		self.findAllButton = ui.get_object("findAllButton")
		self.replaceAllButton = ui.get_object("replaceAllButton")
		self.closeButton = ui.get_object("closeButton")
		self.selectPathButton = ui.get_object("selectPathButton")

		self.findDialog.show()

		self.matchWholeWordCheckbutton.set_active(self._instance.options['MATCH_WHOLE_WORD'])
		self.matchCaseCheckbutton.set_active(self._instance.options['MATCH_CASE'])
		self.wrapAroundCheckbutton.set_active(self._instance.options['WRAP_AROUND'])
		self.followCurrentDocCheckbutton.set_active(self._instance.options['FOLLOW_CURRENT_DOC'])
		self.includeSubfolderCheckbutton.set_active(self._instance.options['INCLUDE_SUBFOLDER'])
		self.regexSearchCheckbutton.set_active(self._instance.options['REGEX_SEARCH'])

		if self._instance.options['FOLLOW_CURRENT_DOC'] == True:
			self.pathComboboxentry.child.set_text(os.path.dirname(self._instance._window.get_active_document().get_uri_for_display()))

	def on_findDialog_destroy_action(self, object):
		try:
			self._instance.find_dialog = None
		except:
			pass

	def main(self):
		gtk.main()

	def append_combobox_list(self):
		find_text = self.findTextEntry.get_active_text()
		replace_text = self.replaceTextEntry.get_active_text()
		file_pattern = self.filterComboboxentry.get_active_text()
		path = self.pathComboboxentry.get_active_text()
		self._instance.current_search_pattern = find_text
		self._instance.current_replace_text = replace_text
		#self._instance.current_file_pattern = file_pattern
		#self._instance.current_path = path
		
		if find_text != "" and find_text not in self._instance.find_list:
			self._instance.find_list.append(find_text)
			self.findTextEntry.append_text(find_text)
			
		if replace_text != "" and replace_text not in self._instance.replace_list:
			self._instance.replace_list.append(replace_text)
			self.replaceTextEntry.append_text(replace_text)
			
		if file_pattern != "" and file_pattern not in self._instance.filter_list:
			self._instance.filter_list.append(file_pattern)
			self.filterComboboxentry.append_text(file_pattern)
			
		if path != "" and path not in self._instance.path_list:
			self._instance.path_list.append(path)
			self.pathComboboxentry.append_text(path)

	# button actions       
	def on_findButton_clicked_action(self, object):
		doc = self._instance._window.get_active_document()
		if not doc:
			return
		
		search_pattern = self.findTextEntry.get_active_text()
		if search_pattern == "":
			return
		
		self.append_combobox_list()
		self._instance.advanced_find_in_doc(doc, search_pattern, self._instance.options, self._instance.forwardFlg)
		
	def on_replaceButton_clicked_action(self, object):
		doc = self._instance._window.get_active_document()
		if not doc:
			return
			
		search_pattern = self.findTextEntry.get_active_text()
		if search_pattern == "":
			return
		
		self.append_combobox_list()
		self._instance.advanced_find_in_doc(doc, search_pattern, self._instance.options, self._instance.forwardFlg, True)

	def on_findAllButton_clicked_action(self, object):
		search_pattern = self.findTextEntry.get_active_text()
		if search_pattern == "":
			return
		
		self.append_combobox_list()
		
		it = self._instance._results_view.append_find_pattern(search_pattern)
		
		if self._instance.scopeFlg == 0: #current document
			doc = self._instance._window.get_active_document()
			if not doc:
				return
			self._instance.advanced_find_all_in_doc(it, doc, search_pattern, self._instance.options)
			self._instance._results_view.show_find_result()
			self._instance.show_bottom_panel()
		elif self._instance.scopeFlg == 1: #all opened documents
			docs = self._instance._window.get_documents()
			if not docs:
				return
			for doc in docs:
				self._instance.advanced_find_all_in_doc(it, doc, search_pattern, self._instance.options)
			self._instance._results_view.show_find_result()
			self._instance.show_bottom_panel()
		elif self._instance.scopeFlg == 2: #files in directory
			dir_path = self.pathComboboxentry.get_active_text()
			file_pattern = self.filterComboboxentry.get_active_text()
			self._instance.find_all_in_dir(it, dir_path, file_pattern, search_pattern, self._instance.options)
		elif self._instance.scopeFlg == 3: #current selected text
			doc = self._instance._window.get_active_document()
			if not doc:
				return
			self._instance.advanced_find_all_in_doc(it, doc, search_pattern, self._instance.options, False, True)
			self._instance._results_view.show_find_result()
			self._instance.show_bottom_panel()

	def on_replaceAllButton_clicked_action(self, object):
		search_pattern = self.findTextEntry.get_active_text()
		if search_pattern == "":
			return
		
		self.append_combobox_list()

		it = self._instance._results_view.append_find_pattern(search_pattern, True, self.replaceTextEntry.child.get_text())
		
		if self._instance.scopeFlg == 0: #current document
			doc = self._instance._window.get_active_document()
			if not doc:
				return
			self._instance.advanced_find_all_in_doc(it, doc, search_pattern, self._instance.options, True)
			self._instance._results_view.show_find_result()
			self._instance.show_bottom_panel()
		elif self._instance.scopeFlg == 1: #all opened documents
			docs = self._instance._window.get_documents()
			if not docs:
				return
			for doc in docs:
				self._instance.advanced_find_all_in_doc(it, doc, search_pattern, self._instance.options, True)
			self._instance._results_view.show_find_result()
			self._instance.show_bottom_panel()
		elif self._instance.scopeFlg == 2: #files in directory
			path = str(self._instance._results_view.findResultTreemodel.iter_n_children(None) - 1)
			it = self._instance._results_view.findResultTreemodel.get_iter(path)
			self._instance._results_view.findResultTreemodel.set_value(it, 2, _("Replace in this scope is not supported."))
		elif self._instance.scopeFlg == 3: #current selected text
			doc = self._instance._window.get_active_document()
			if not doc:
				return
			self._instance.advanced_find_all_in_doc(it, doc, search_pattern, self._instance.options, True, True)
			self._instance._results_view.show_find_result()
			self._instance.show_bottom_panel()

	def on_closeButton_clicked_action(self, object):
		self.findDialog.destroy()
		
	def on_selectPathButton_clicked_action(self, object):
		self.selectPathFilechooserdialog.show()

	# select path file chooserr dialog actions
	def on_selectPathDialogOkButton_clicked_action(self, object):
		folder_path = self.selectPathFilechooserdialog.get_filename()
		self.selectPathFilechooserdialog.select_filename(folder_path)
		self.pathComboboxentry.child.set_text(folder_path)
		self.append_combobox_list()
		self.selectPathFilechooserdialog.hide()
		
	def on_selectPathDialogCancelButton_clicked_action(self, object):
		self.selectPathFilechooserdialog.hide()

	# options    
	def on_matchWholeWordCheckbutton_toggled_action(self, object):
		self._instance.options['MATCH_WHOLE_WORD'] = object.get_active()

	def on_matchCaseCheckbutton_toggled_action(self, object):
		self._instance.options['MATCH_CASE'] = object.get_active()

	def on_wrapAroundCheckbutton_toggled_action(self, object):
		self._instance.options['WRAP_AROUND'] = object.get_active()
		
	def on_followCurrentDocCheckbutton_toggled_action(self, object):
		self._instance.options['FOLLOW_CURRENT_DOC'] = object.get_active()
		if object.get_active() == True:
			self.pathComboboxentry.child.set_text(os.path.dirname(self._instance._window.get_active_document().get_uri_for_display()))
		else:
			filebrowser_root = self.get_filebrowser_root()
			if filebrowser_root != None and self._instance.options['ROOT_FOLLOW_FILEBROWSER'] == True:
				self.pathComboboxentry.child.set_text(filebrowser_root)
			else:
				self.pathComboboxentry.child.set_text(self.selectPathFilechooserdialog.get_filename())
			
	def on_includeSubfolderCheckbutton_toggled_action(self, object):
		self._instance.options['INCLUDE_SUBFOLDER'] = object.get_active()
		
	def on_regexSearchCheckbutton_toggled_action(self, object):
		self._instance.options['REGEX_SEARCH'] = object.get_active()


	# radiobutton
	def directionRadiobuttonGroup_action(self, object):
		self._instance.forwardFlg = self.forwardRadiobutton.get_active()

	def scopeRadiobuttonGroup_action(self, object):
		if self.currentFileRadiobutton.get_active() == True:
			self._instance.scopeFlg = 0
		elif self.allFilesRadiobutton.get_active() == True:
			self._instance.scopeFlg = 1
		elif self.allFilesInPathRadiobutton.get_active() == True:
			self._instance.scopeFlg = 2
		elif self.currentSelectionRadiobutton.get_active() == True:
			self._instance.scopeFlg = 3

	# filebrowser integration
	def get_filebrowser_root(self):
		base = u'/apps/gedit-2/plugins/filebrowser/on_load'
		client = gconf.client_get_default()
		client.add_dir(base, gconf.CLIENT_PRELOAD_NONE)
		path = os.path.join(base, u'virtual_root')
		val = client.get(path)
		if val != None:
			return val.get_string()[7:]
		return None
	


if __name__ == "__main__":
	app = AdvancedFindUI(None)
	app.main()

