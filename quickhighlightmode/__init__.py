import gedit
import gtk
import gconf
import os
import os.path
from gettext import gettext as _
import gtk.glade
import gtksourceview

ui_str = """
<ui>
    <menubar name="MenuBar">
        <menu name="ViewMenu" action="View">
            <menuitem name="QuickHighlightMode" action="QuickHighlightMode"/>
        </menu>
    </menubar>
</ui>
"""

GLADE_FILE = os.path.join(os.path.dirname(__file__), "quickhighlightmode.glade")

class QuickHighlightPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)

    def activate(self, window):
        self.window = window
        self.dialog = None
        self.language_manager = gtksourceview.SourceLanguagesManager()
        langs = self.language_manager.get_available_languages()
        self.model = gtk.ListStore(str, str)
        
        for lang in langs:
            self.model.append([lang.get_name(), lang.get_mime_types()[0]])
        
        actions = [
            ('QuickHighlightMode', gtk.STOCK_SELECT_COLOR, _('Quick Highlight Mode'), '<Control><Shift>h', _("Press Ctrl+Shift+H for quick highlight selection"), self.on_open)
        ]
        
        action_group = gtk.ActionGroup("QuickHighlightModeActions")
        action_group.add_actions(actions, self.window)
        
        self.manager = self.window.get_ui_manager()
        self.manager.insert_action_group(action_group, -1)
        self.manager.add_ui_from_string(ui_str)
    
    def on_open(self, *args):
        glade_xml = gtk.glade.XML(GLADE_FILE)
        
        if self.dialog:
            self.dialog.set_focus(True)
            return
        
        self.selected_language = self.language_manager.get_language_from_mime_type('text/plain')
        
        self.dialog = glade_xml.get_widget('quickhighlight_dialog')
        self.dialog.connect('delete_event', self.on_close)
        self.dialog.show_all()
        self.dialog.set_transient_for(self.window)
        
        self.combo = glade_xml.get_widget('language_list')
        
        self.cancel_button = glade_xml.get_widget('cancel_button')
        self.cancel_button.connect('clicked', self.on_cancel)
        
        self.apply_button = glade_xml.get_widget('apply_button')
        self.apply_button.connect('clicked', self.on_apply)
        
        self.combo.set_model(self.model)
        self.combo.set_text_column(0)
        
        self.completion = gtk.EntryCompletion()
        self.completion.connect('match-selected', self.on_selected)
        self.completion.set_model(self.model)
        self.completion.set_text_column(0)
        
        self.entry = self.combo.get_children()[0]
        self.entry.set_completion(self.completion)
        
        self.combo.connect('changed', self.on_change)
    
    def on_change(self, widget):
        model = widget.get_model()
        iter = widget.get_active_iter()
        
        if iter:
            self.set_language(iter)
    
    def set_language(self, iter, model=None):
        if not model:
            model = self.model
        
        mime = model[iter][1]
        language = self.language_manager.get_language_from_mime_type(mime)
        self.selected_language = language
    
    def close_dialog(self):
        self.dialog.destroy()
        self.dialog = None
    
    def on_selected(self, completion, model, iter):
        self.set_language(iter, model)
    
    def on_close(self, *args):
        self.close_dialog()
    
    def on_cancel(self, *args):
        self.close_dialog()
    
    def on_apply(self, *args):
        view = self.window.get_active_view()
        buffer = view.get_buffer()
        
        if self.selected_language:
            buffer.set_language(self.selected_language)
        
        self.close_dialog()
