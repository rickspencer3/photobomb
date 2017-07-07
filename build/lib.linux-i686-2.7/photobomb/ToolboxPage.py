# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Rick Spencer <rick.spencer@canonical.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import sys
import os
import gtk
import gobject
import quickly

class ToolboxPage(gtk.VBox):  
    def __init__(self):
        gtk.VBox.__init__(self, False, 5)
        self.set_border_width(5)

    def on_selected(self):
        pass

    def on_deselected(self):
        pass

class TestWindow(gtk.Window):
    """For testing and demonstrating search_page.

    """

    def __init__(self):
        #create a window a VBox to hold the controls
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("Camera Test Window")
        windowbox = gtk.VBox(False, 2)
        windowbox.show()
        self.add(windowbox)

        sp = DirectoryPage()
        sp.show()
        windowbox.pack_start(sp)
  
        self.show()
  
        #finish wiring up the window
        self.connect("destroy", self.destroy)

        #start up gtk.main in a threaded environment  
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()

        #called when the window is destroyed
    def destroy(self, widget, data = None):
        gtk.main_quit()

if __name__== "__main__":
    test = TestWindow()



