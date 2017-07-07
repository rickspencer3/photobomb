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
import Image
import urllib
from quickly.widgets.url_fetch_progressbox import UrlFetchProgressBox
import quickly

class ImageListPage(gtk.VBox):  
    temp_dir = os.path.join(os.environ["HOME"],".tmp","photobomb")
    button_size = 196

    def __init__(self):
        gtk.VBox.__init__(self, False, 5)
        self.set_border_width(5)
        self.loading = False

        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        self.button_box = gtk.VBox(True,5)
        self.button_box.show()

        scroller = gtk.ScrolledWindow()
        scroller.set_property("vscrollbar-policy",gtk.POLICY_AUTOMATIC)
        scroller.set_property("hscrollbar-policy",gtk.POLICY_NEVER)

        scroller.add_with_viewport(self.button_box)
        scroller.show()
        self.pack_end(scroller)

    def on_selected(self):
        self.loaded = True

    def on_deselected(self):
        pass

    def clear_buttons(self):
        #TODO: fix this so it doesn't leak references to signals
        for b in self.button_box:
            self.button_box.remove(b)
            
    def add_button_from_pixbuf(self, pixbuf, tip):
        img = gtk.Image()
        width = pixbuf.get_width()
        height = pixbuf.get_height()

        if width > height:
            height = int((float(height)/float(width)) * self.button_size)
            width = self.button_size
        elif height > width:
            width = int((float(width)/float(height)) * self.button_size)
            height =self.button_size
        else:
            width = self.button_size
            height = self.button_size
        pixbuf2 = pixbuf.scale_simple(width,height,gtk.gdk.INTERP_BILINEAR)

        img.set_from_pixbuf(pixbuf2)
        img.show()
        button = gtk.Button()
        button.set_image(img)
        button.set_tooltip_text(tip)
        button.show()
        self.button_box.pack_start(button, True, True)
        button.connect("clicked", self.image_clicked, pixbuf)
        return button

    def add_button_from_thumb_data(self, data, pic_url):
        pixbuf = self.pixbuf_from_data(data)
        img = gtk.Image()
        img.set_from_pixbuf(pixbuf)
        img_height = img.get_pixbuf().get_height()
        img_width = img.get_pixbuf().get_width()

        if  img_height > self.button_size or img_width > self.button_size:
            new_img_height = self.button_size
            new_img_width = self.button_size
            if img_height > img_width:
                p = float(self.button_size)/img_height
                new_img_width = int(img_width * p)
            elif img_width > img_height:
                p = float(self.button_size)/img_width
                new_img_height = int(img_height * p)
            pb = img.get_pixbuf().scale_simple(new_img_width,new_img_height,
                                               gtk.gdk.INTERP_BILINEAR)
            img = gtk.Image()
            img.set_from_pixbuf(pb)

        img.show()
        button = gtk.Button()
        button.set_image(img)
        button.show()
        self.button_box.pack_start(button, True, True)
        button.connect("clicked", self.thumb_clicked, pic_url)
        return button

    def add_button_from_thumb(self, thm_url, pic_url):
        img_stream = urllib.urlopen(thm_url)
        data = img_stream.read()
        img_stream.close()
        pixbuf = self.pixbuf_from_data(data)

        img = gtk.Image()
        img.set_from_pixbuf(pixbuf)
        img.show()
        button = gtk.Button()
        button.set_image(img)
        button.show()
        self.button_box.pack_start(button, True, True)
        button.connect("clicked", self.thumb_clicked, pic_url)
        return button

    def image_clicked(self, widget, pixbuf):
        self.emit("clicked",pixbuf)

    def thumb_clicked(self, widget, url):
        img_fetch = UrlFetchProgressBox(url)
        img_fetch.progressbar.set_text("Downloading")
        pos = self.button_box.child_get_property(widget, "position")

        img_fetch.connect("downloaded",self.image_downloaded, widget)
        img_fetch.connect("download-error", self.image_download_error, url)
        widget.hide()

        self.button_box.pack_start(img_fetch, True, False)
        self.button_box.child_set_property(img_fetch, "position",pos)
        img_fetch.show()

    def image_download_error(self, widget, error, url):
        print "Error downloading %s :" % url
        print error
        msg = "Sorry, could not find image at %s " % url
        gtk.gdk.threads_enter()
        quickly.prompts.error("Photo Bomb",msg)
        gtk.gdk.threads_leave()
    

    def image_downloaded(self, widget, data, button):
        try:
            pixbuf = self.pixbuf_from_data(data)
            self.emit("clicked",pixbuf)
            button.show()

        except Exception, inst:
            print inst
            gtk.gdk.threads_enter()
            msg = "Sorry, but Photo Bomb is unable to display the image."
            msg += "\nThe image seems to be corrupted"
            quickly.prompts.error("Photo Bomb",msg)
            gtk.gdk.threads_leave()

    def pixbuf_from_data(self, data):
            pbl = gtk.gdk.PixbufLoader()
            pbl.write(data)
            return pbl.get_pixbuf()

    __gsignals__ = {'clicked' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		}


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
