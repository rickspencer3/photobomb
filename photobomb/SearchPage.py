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
import urllib
import urllib2
import json
from quickly.widgets.url_fetch_progressbox import UrlFetchProgressBox
import quickly.prompts
import re
from ImageListPage import ImageListPage

class SearchPage(ImageListPage):

    def __init__(self):
        ImageListPage.__init__(self)
 
        hint_text = "Enter a URL to a page or an image"
        lbl = gtk.Label(hint_text)
        lbl.set_line_wrap(True)
        lbl.show()
        self.pack_start(lbl, False, False)

        hb = gtk.HBox(False, 5)
        hb.show()
        txt = gtk.Entry()
        txt.set_tooltip_text(hint_text)
        txt.connect("activate",self.__search,txt)
        txt.show()
        hb.pack_start(txt,True, True)
        sb = gtk.Button(stock=gtk.STOCK_FIND)
        sb.show()
        sb.connect("clicked",self.__search,txt)
        hb.pack_end(sb,False, False)

        self.pack_start(hb, False, False)

    def __search(self, widget, entry):
        search_string = entry.get_text()
        test_string = search_string.lower()
        if test_string.endswith(".png") or test_string.endswith(".jpg") or test_string.endswith(".gif"):
            self.clear_buttons()
            self.get_web_image(search_string)
        else:
            self.get_web_page(search_string)

    def get_web_page(self, url):
        page_fetch = UrlFetchProgressBox(url)
        #page_fetch.show()
        self.pack_start(page_fetch, False, False)    
        page_fetch.connect("downloaded",self.web_page_downloaded)
        page_fetch.connect("download-error",self.web_page_download_error, url)
        
    def web_page_download_error(self, widget, error, url):
        msg = """Could not find page at %s""" % url
        gtk.gdk.threads_enter()
        quickly.prompts.error("Photobomb", msg)
        gtk.gdk.threads_leave()

    def web_page_downloaded(self, widget, html):
        pics_re = "http.*?jpg|http.*?png|http.*?gif" 
        pics = re.findall(pics_re, html,re.MULTILINE | re.IGNORECASE)

        self.clear_buttons()
        self.scraped_img_urls = []
        self.current_scraped_image = 0
        for pic in pics:
            pic_url = "http:" + pic.split("http:")[-1]
            if pic_url not in self.scraped_img_urls:
                self.scraped_img_urls.append(pic_url)
        self.add_next_scraped_image()

    def add_next_scraped_image(self):
        if self.current_scraped_image < len(self.scraped_img_urls):
            url = self.scraped_img_urls[self.current_scraped_image]
            img_fetch = UrlFetchProgressBox(url)
            img_fetch.connect("downloaded",self.scraped_image_fetched, url)
            img_fetch.connect("download-error",self.scraped_image_download_error, url)
            #img_fetch.show()
            self.pack_start(img_fetch, False, False)
            self.current_scraped_image += 1

    def get_web_image(self, url):
        img_fetch = UrlFetchProgressBox(url)
        img_fetch.connect("downloaded",self.image_fetched, url)
        img_fetch.connect("download-error",self.image_fetch_error, url)
        #img_fetch.show()
        self.pack_start(img_fetch, False, False)

    def scraped_image_download_error(self, widget, error, url):
        print "Error downloading " + url
        print error

    def scraped_image_fetched(self, widget, data, url):
        self.image_fetched(self, data, url)
        self.add_next_scraped_image()

    def image_fetched(self,widget, data, url):
        try:
            pixbuf = self.pixbuf_from_data(data)
            self.add_button_from_pixbuf(pixbuf, url)
        except Exception, inst:
            print "Error loading downloaded image:"
            print inst
            msg = "Photo Bomb could not load that image."
            msg += "\nIt appears to be corrupted."
            gtk.gdk.threads_enter()
            quickly.prompts.error("Photo Bomb", msg)
            gtk.gdk.threads_leave()

    def image_fetch_error(self, widget, error, url):
        print "Error downloading " + url
        print error
        
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

        sp = SearchPage()
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
