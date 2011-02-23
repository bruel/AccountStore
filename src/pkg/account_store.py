# -*- coding: utf-8 -*-
import gedit
import gtk
import account_engine as ae
from gettext import gettext as _

ui_str = '''<ui> 
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="AccountStore" action="AccountStore"/>
      </placeholder>
    </menu>
  </menubar>
</ui>'''

############### class ##################
class AccountStoreDialog:
    ''' This class implements the account store dialog '''
    def __init__(self, windowhelper):
        print 'ASD.__init__()'
        self.winhelp = windowhelper
        self.dlg = gtk.Dialog('Account Store', self.winhelp.win, 
                              gtk.DIALOG_DESTROY_WITH_PARENT) 
        self.dlg.set_border_width(0)
        self.liststore = gtk.ListStore(str, str, str)
        
        #################### populate ListStore ######################
        self.am = ae.AccountManager()  # ae: account_engine module. am has been
        for act in self.am.accounts:   # populated with accounts ('accounts')
            self.liststore.append(self.am.csv2list(str(act)))
        # Now liststore is populated
    
        ################### setup TreeView widget ####################
        CELL_PAD = 6       # How can I apply CELL_PAD to tvcol titles (inorder
        # TreeViewColumns  # for title and cell content to left align)?
        self.tvcol1 = gtk.TreeViewColumn('Account') # All cols start visible, auth. TODO
        self.tvcol1.set_alignment(0.5)  # 0.5: Title in middle of column
        self.tvcol1.set_property('visible', False)
        self.tvcol2 = gtk.TreeViewColumn('User Name or ...')  # 'or...' indicates not just
        self.tvcol2.set_alignment(0.5)                        # username but also phone-
        self.tvcol2.set_property('visible', False)            # numbers and other stuff
        self.tvcol3 = gtk.TreeViewColumn('Password')
        self.tvcol3.set_alignment(0.5)
        self.tvcol3.set_property('visible', False)
        
        # Create the TreeView using liststore
        self.treeview = gtk.TreeView(self.liststore)
        self.treeview.append_column(self.tvcol1)
        self.treeview.append_column(self.tvcol2)
        self.treeview.append_column(self.tvcol3)
        self.treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        self.treeview.get_selection().connect('changed', self.row_activated_cb)
        
        # Create a scrollwindow and put the TreeView inside it
        self.scroll_win = gtk.ScrolledWindow()
        self.scroll_win.set_size_request(320, 180)
        self.scroll_win.add(self.treeview)
        
        # Create CellRendererText to render the data
        self.cellr1 = gtk.CellRendererText()
        self.cellr1.set_property('xpad', CELL_PAD)
        self.cellr1.set_property('editable', True)
        self.cellr2 = gtk.CellRendererText()
        self.cellr2.set_property('xpad', CELL_PAD)
        self.cellr2.set_property('editable', True)
        self.cellr3 = gtk.CellRendererText()
        self.cellr3.set_property('xpad', CELL_PAD)
        self.cellr3.set_property('editable', True)

        # Add the cellrrenderer to the tvcols. Cannot share same renderer because
        # of updating in but_new_act_cb(). True: allow it to expand
        self.tvcol1.pack_start(self.cellr1, True)
        self.tvcol2.pack_start(self.cellr2, True)
        self.tvcol3.pack_start(self.cellr3, True)

        # Set the cellr's "text" attribute and retrieve text from the respective 
        # columns in liststore
        self.tvcol1.add_attribute(self.cellr1, 'text', 0)
        self.tvcol2.add_attribute(self.cellr2, 'text', 1)
        self.tvcol3.add_attribute(self.cellr3, 'text', 2)

        self.treeview.set_search_column(0)  # Search on account names via Ctrl+f
        
        #################### additional widgets ######################
        self.but_hide_show = gtk.Button('Show')  # We start by hiding the view (=> room 
        self.but_hide_show.connect('clicked', self.but_hide_show_cb)  # for auth. TODO)
        
        self.but_del_act = gtk.Button('Delete Account')
        self.but_del_act.connect('clicked', self.but_del_act_cb)
        self.but_del_act.set_sensitive(False)  # Make it's True only if row activated
        
        self.but_new_act = gtk.Button('New Account')
        self.but_new_act.connect('clicked', self.but_new_act_cb)
        
        self.but_close = gtk.Button('Close')
        self.but_close.connect('clicked', self.but_close_cb)
        
        hbbox = gtk.HButtonBox()
        hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        hbbox.set_spacing(6)  # Spacing between buttons
        hbbox.pack_start(self.but_hide_show, True, False, 2)  # No expand, no 
        hbbox.pack_start(self.but_del_act, True, False, 2)    # fill, pad. 2px
        hbbox.pack_start(self.but_new_act, True, False, 2)
        hbbox.pack_start(self.but_close, True, False, 2)
        
        self.stat_lbl = gtk.Label()
        
        vbox = gtk.VBox(False, 0)
        VBOX_SEP = 6
        vbox.pack_start(self.scroll_win, False, False, VBOX_SEP)
        vbox.pack_start(hbbox, False, False, VBOX_SEP)
        
        hbox_stat = gtk.HBox(False, 0)
        hbox_stat.pack_start(self.stat_lbl, True, False, 0)
        vbox.pack_start(hbox_stat, False, False, 2)
        
        self.dlg.get_action_area().pack_start(vbox, False, False, 0)
        self.dlg.set_position(gtk.WIN_POS_CENTER)
        
        # Make the dialog emit a 'response' signal when its close button is activated
        self.dlg.connect('response', self.dialog_response)
        self.dlg.show_all()
        
    def dialog_response(self, dialog, response):
        print 'ASD.dialog_response()' 
        if response == gtk.RESPONSE_DELETE_EVENT:
            self.winhelp.dlg = None  # Sæt None så ny dialog kan laves    
            self.dlg = None # TODO Tror er unødv?
            
    ################################ callbacks #################################
    def but_hide_show_cb(self, button):
        ''' Callback for but_hide_show '''
        # Visibility property for col 1, 2 and 3 are all true or all false
        # => need only test one of them (here col1)
        cols_visible = self.tvcol1.get_property('visible')
        button.set_label('Show' if cols_visible else 'Hide')
        self.tvcol1.set_property('visible', not cols_visible) # But remember to
        self.tvcol2.set_property('visible', not cols_visible) # set all!
        self.tvcol3.set_property('visible', not cols_visible)
        
    def but_new_act_cb(self, button):
        ''' Callback for but_new_act '''
        self.but_new_act.set_sensitive(False)    # Deactivate buttons when 
        self.but_hide_show.set_sensitive(False)  # editing an account
        
        # Show view
        self.tvcol1.set_property('visible', True)
        self.tvcol2.set_property('visible', True)
        self.tvcol3.set_property('visible', True)
        
        # Make new empty row 
        self.liststore.append(('', '', ''))  # Empty row (empty entries)
        self.cols_valid = [False, False, False]  # All True signals valid entry
        
        # Find row index to the new empty row (a linked list, trav. nessesary :( )
        end_idx = -1
        for row in self.liststore: # We just added an empty row so there's >= 1 row
            end_idx += 1    
            
        self.treeview.scroll_to_cell(end_idx)  # Scroll down to it
        self.treeview.get_selection().select_path(end_idx)  # Select it
                      
        # Connect each CellRenderer to edited_cb() callback with user_data being
        # liststore-reference and index for the column which have been edited
        self.cellr1.connect('edited', self.edited_cb, (self.liststore, 0))
        self.cellr2.connect('edited', self.edited_cb, (self.liststore, 1))
        self.cellr3.connect('edited', self.edited_cb, (self.liststore, 2))

    def but_del_act_cb(self, button):
        ''' TODO Activate a confirmation popup (or an textfield) before succeding 
        with deletion of the row in liststore. '''
        # cur_row_iter is never None when this button is pressed: Once row_activated() is 
        # called it's not-None and once a row is activated there will always be an 
        # activated row
        self.liststore.remove(self.cur_row_iter)  
        self.am.persist(self.liststore)
        self.stat_lbl.set_text('Account deleted')

    def but_close_cb(self, button):  # FIXME Doesn't work
        self.stat_lbl.set_text('Close button doesn\'t work! Please use dialogs close button')
        # None of these work!
        #self.dialog_response(self.dlg, gtk.RESPONSE_DELETE_EVENT)
        #self.dlg.response(gtk.RESPONSE_CANCEL)
        
    def edited_cb(self, cell, path, new_text, user_data):
        ''' Opdates ListStore with newly edited column values '''
        liststore, col_idx = user_data
        liststore[path][col_idx] = new_text
        if new_text != '':  # An empty entry is not an entry
            self.cols_valid[col_idx] = True  # The column flaged valid
            if col_idx == 0 :  # '0' ~ "name" column. Is "prim. key" chk constr. not viol.
                try:
                    self.am.uniq_violation(new_text)
                except self.am.UniquenessException as ue:
                    # Uniqueness warning
                    self.stat_lbl.set_text('Duplicate account name! Please change it')
                    self.cols_valid[col_idx] = False  # Column flaged invalid
                else:    
                    self.stat_lbl.set_text('')
        if reduce(lambda x, y: x & y, self.cols_valid): # ALL cols valid =>
            self.am.persist(liststore)                  # persist liststore
            self.stat_lbl.set_text('Account stored')  # TODO Timer reset after 3s
            self.but_new_act.set_sensitive(True)   # Done editing? Activate 
            self.but_hide_show.set_sensitive(True) # but_new_act & but_hide_show
       
    def row_activated_cb(self, treeselec):
        ''' This method is used instead of common row_selected_cb(), that uses 
        'row-activated' signal, because it requires double clicks for activation. 
        This 'changed' signal which fires on a single click '''
        # Attribute self.cur_row_iter is used by but_del_act_cb()
        self.cur_row_iter = treeselec.get_selected()[1]  
        self.but_del_act.set_sensitive(True)  # Row selected => deletion possible
        self.but_new_act.set_sensitive(True)  # Row selected => new act. possible
        self.stat_lbl.set_text('')
    
############### class ##################
class AccountStoreWindowHelper:
    """ This class registers a menu-item and action to show the accelerator
        dialog. This class is per window-instance """
    def __init__(self, window):
        print "ASWH.__init__()"  # All 'print "abc.xyz()"' statements makes a nice "met-
        self.win = window        # hod trace" when gedit is started from the terminal
        manager = self.win.get_ui_manager()

        self.action_group = gtk.ActionGroup("EditShortcutsPluginActions")
        self.action_group.add_actions([("AccountStore", None, _("_Account Store"), 
                                        None, _("Load the account store"), 
                                        self.show_account_dialog)])
        
        manager.insert_action_group(self.action_group, -1)
        self.ui_id = manager.add_ui_from_string(ui_str)
        
        self.dlg = None # None => new dialog can be made. See show_account_dialog()
        
    def deactivate(self):
        print "ASWH.deactivate()"
        self.remove_menu()
        self.win = None
        self.dlg = None
        self.action_group = None
    
    def remove_menu(self):
        print "ASWH.remove_menu()"
        manager = self.win.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()  # Make sure the manager updates
               
    def update_ui(self):
        print "ASWH.update_ui()"  # Not used sofar...
        
    def show_account_dialog(self, action):
        print "ASWH.show_account_dialog()"
        if self.dlg is None:  # Poor mans Singleton pattern...
            self.dlg = AccountStoreDialog(self)
        
############################### gedit territory ################################
class AccountStore(gedit.Plugin):
    def __init__(self):
        ''' Called by gedit as the first method '''
        print '\nAS.__init__()'
        gedit.Plugin.__init__(self)
        self._instances = dict()

    def activate(self, window):
        ''' Called by gedit when window have been made '''
        print 'AS.activate()'
        self._instances[window] = AccountStoreWindowHelper(window)
        
    def deactivate(self, window):
        ''' Called by gedit when window closes '''
        print 'AS.deactivate()***'
        self._instances[window].deactivate()
        del self._instances[window]
        
    def update_ui(self, window):
        print 'AS.update_ui()'
        self._instances[window].update_ui()


################## bugs ##################
'''
*) The Close button doesn't work. One needs to close Account Store on the 
   dialogs close button (upper right corner) (a temp. warning has been made    )
*) If one makes fast double clicks on an account name the 'Duplicate account 
   name...' warning is triggered. Why and what to do?
'''

###### future features and thoughts ######
''' (H High, M Medium, L Low, * Thoughts)

H) Implement use case 'Update Account' (missing CRUD)
H) System needs to check if the account file account_store.txt exists and if not
   create an empty file in /usr/lib/gedit-2/plugins.
H) Make Account Store configurable. E.g. the location of the file 
   account_store.txt (e.g. somewhere in the users homedir)
H) Implement crypto part (encryption/decryption of file). What algos? Use 
   steganography? Use file compression (zip, gzip)?
H) Implement use case 'Validate use of Account Store' (actually a 'Login' use 
   case). One should only be allowed to see all the codes via a "master 
   password". Where should that be stored? (Likely in a config file, encrypted?)
H) The use case 'Create Account' is too rigid: One have to complete an entry. 
   E.g. the Show/Hide doesn't get activated unless one has completed an entry. So
   If one makes an error he/she should complete the entry, delete it and then
   recreate it(!)
---
H) Make horisontal size (x-size) of dialog adapt to the size of treeview (at 
   least with reasonably x ranges e.g. 320px-700px). It's irritating to use 
   scrollbars. Also consider scrollbars on one or all columns (maybe only Account
   Name column has long entries). Would make it possible to fix the size of the
   treeview and dialog
M) Use case 'Delete Account' is without any warning ("real men cry"). Change this
M) Make it possible to sort the columns by clicking on the column headers (is 
   builtin to treeviewcolumn afaik)
M) Better handling of null values (sofar its not done right - user can input 
   one/more spaces so it _looks_ like its null)
---
L) Implement a timed_notify(lbl, txt, wait) method that displays the 'txt' text
   on label 'lbl' for 'wait' seconds. If wait is left out it should be set 
   "very large" effectively making it an ordinary notify(). Note this requires 
   use of threads. Concrete used for 'Account deleted' notification (but probably
   others i future)
L) Implement use case 'View Additional Account Information'. Additional info 
   could be an accounts expiration date, reason of having the account, eventual
   problems with the account etc.
L) Implement at test suite for Account Store (what test tools?)
L) Better search: The builtin Search functinality searches from the beginning of 
   rows (on Account Name). Make it a possibility to search on words positioned
   anywhere on a row. Use: E.g. to search for 'tel' which could in the account 
   names 'Alice's tel', 'Tel MyISP support' (case-indifferent search). Effecti-
   vely this would make it useful to "tag" accounts
L) Possibility to use Tab to do column jumping when creating and updating an 
   account. Now one have use click on the given row. In general minimize mouse 
   dependability
L) Various colors: 1) Activated rows background color in some grey - or at least 
   different from the blue background color shared by the dialog title and scroll-
   bars. 2) Warnings in red or orange text
L) It seems like closing the Account Store via the Close button takes more time
   and involves disk activity whereas closing it one the dialogs native close 
   button (upper right corner) closes it like a breeze. Why this difference?
---
*) Should this 'Account Store' turn into a general purpose PIM (Personal Infor-
   mation Manager)? If so: should the user be able to configure number of 
   columns, their names, relations between accounts, etc.
*) Diff write-backs? To reduce amount of disk activity one could use diff(1) to
   only write-back diffs (maybe only one diff which is overwriten) and then on 
   quit assemble and encrypt the file. Seems overkill by now though
*) I lack a high level view the states when hacking on gui. Explore how to refine 
   the control/tracking of the state that Account Store is in. Draw a state graph 
   and maybe look at state patterns
'''