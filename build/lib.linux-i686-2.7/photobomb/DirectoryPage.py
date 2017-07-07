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
import glib

import quickly.prompts
from ImageListPage import ImageListPage

class DirectoryPage(ImageListPage):
        
    def __init__(self):
        ImageListPage.__init__(self)
        hb = gtk.HBox(False, 5)
        hb.show()
        self.__directory_button = gtk.Button()
        img = gtk.image_new_from_stock(gtk.STOCK_DIRECTORY,  gtk.ICON_SIZE_LARGE_TOOLBAR)
        img.show()
        hb.pack_start(img, False, False)
        img.set_tooltip_text("Choose Directory")
        
        self.__directory_label = gtk.Label()
        self.__directory_label.show()
        self.__directory_button.show()
        self.__directory_button.connect("clicked", self.__choose_dir)
        hb.pack_start(self.__directory_label,False, True)
        self.__directory_button.add(hb)
        self.pack_start(self.__directory_button, False, False)
        self.current_image = 0
        self.file= []

    def on_selected(self):
        if len(self.button_box.get_children()) == 0 and not self.loading:
            self.loading = True
            self.load()

    def load(self, directory = glib.get_user_special_dir(glib.USER_DIRECTORY_PICTURES)):
        self.directory = directory
        self.__get_pics()
        
    def __choose_dir(self, widget, data=None):
        dr = glib.get_user_special_dir(glib.USER_DIRECTORY_PICTURES)
        response, directory = quickly.prompts.choose_directory("Photobomb Choose Directory", dr)
        if response == gtk.RESPONSE_OK:
            self.directory = directory
            self.clear_buttons()
            self.__get_pics()

    def __get_pics(self):
        self.__directory_label.set_text(self.directory)
        self.__directory_label.set_tooltip_text(self.directory)
        self.files = os.listdir(self.directory)
        self.current_image = 0
        self.__directory_button.set_sensitive(False)
        gobject.idle_add(self.add_next_image)
            
    def add_next_image(self):
        if self.current_image >= len(self.files):
            self.__directory_button.set_sensitive(True)
            return False
        else:
            f = self.files[self.current_image]
            img_path = os.path.join(self.directory,f)
            try:
               pixbuf = gtk.gdk.pixbuf_new_from_file(img_path)
               self.add_button_from_pixbuf(pixbuf,f)
            except:
                pass
            self.current_image += 1
            return True

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






