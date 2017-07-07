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
import time
import sqlite3
import json
import re
import Image
import dbus
import json

import quickly.prompts
from gwibber.microblog.util.const import SQLITE_DB_FILENAME
from quickly.widgets.url_fetch_progressbox import UrlFetchProgressBox

from ImageListPage import ImageListPage

class GwibberPage(ImageListPage):
    def __init__(self):
        ImageListPage.__init__(self)

        hb = gtk.HBox(False, 5)
        hb.show()
        img = gtk.image_new_from_stock(gtk.STOCK_REFRESH,  gtk.ICON_SIZE_LARGE_TOOLBAR)
        img.show()
        refresh_button = gtk.Button()
        refresh_button.set_image(img)
        refresh_button.show()
        refresh_button.set_tooltip_text("Refresh")
        refresh_button.connect("clicked",self.refresh_clicked)  
        hb.pack_start(refresh_button, False, False)
        self.pack_start(hb, False, False)

    def on_selected(self):
        if len(self.button_box.get_children()) == 0 and not self.loading:
            self.loading = True
            gobject.idle_add(self.refresh)
            self.parse_results_progress = gtk.ProgressBar()
            self.parse_results_progress.set_text("Finding Pics in Feeds")
            self.parse_results_progress.show()  
            self.pack_start(self.parse_results_progress, False, False)

    def refresh_clicked(self, widget, data=None):
        if not self.loading:
            self.refresh()

    def on_deslected(self):
        pass

    def refresh(self):
        self.clear_buttons()

        #TODO: find out how to specify the days to retrieve
        days_to_retrieve = 7
        recent_messages = int(time.time() - (60 * 60 * 24 * days_to_retrieve))

        bus = dbus.SessionBus()
        streams = bus.get_object("com.Gwibber.Streams", "/com/gwibber/Streams", follow_name_owner_changes=True)
        jsn = json.loads(streams.Messages("images", "all", recent_messages, "0", "0", "time", "DESC", 0))
        
        self.parse_results_progress.set_text("Loading")
        self.total_images = len(jsn)
        self.counted_results = 0

        if len(jsn) < 1:
            self.remove(self.parse_results_progress)
            return False

        for obj in jsn:
            if 'photo' in obj:
                if 'picture' in obj['photo']:
                    thumb = obj['photo']['picture']
                    if thumb is not None:
                        gobject.idle_add(self.add_thumb, thumb, get_image_uri(thumb))
                else:
                    self.counted_results += 1
            elif 'images' in obj:
                for i in obj['images']:
                    if 'thumb' in i and 'full' in i:
                        gobject.idle_add(self.add_thumb, i['thumb'], i['full'])
                    elif 'src' in i:
                            try:
                                resolved_img =  get_image_uri(i['url'])
                                if type(resolved_img) == dict:
                                    resolved_img = resolved_img["img_uri"]
                                    gobject.idle_add(self.add_thumb, i['src'], resolved_img)
                                elif type(resolved_img) == unicode:
                                    gobject.idle_add(self.add_thumb, i['src'], resolved_img)
                                else:
                                    self.counted_results += 1
                            except Exception, inst:
                                self.counted_results += 1
                    else: 
                        self.counted_results += 1

            else:
                self.counted_results += 1
        self.loading = False
        return False

    def add_thumb(self, thm_url, pic_url):
        try:
            thumb_fetcher = UrlFetchProgressBox(thm_url)
            thumb_fetcher.connect("downloaded", self.thumb_downloaded, pic_url)
            thumb_fetcher.connect("download-error", self.thumb_download_error, thm_url)
        except Exception, inst:
            print inst
        return False

    def thumb_download_error(self, widget, error, thm_url):
        self.handle_progress_bar()
        print "Error Downloading Thumbnail at:"
        print thm_url
        print error

    def thumb_downloaded(self, widget, data, pic_url):
        try:
            self.add_button_from_thumb_data(data, pic_url)
        except:
            pass
        self.handle_progress_bar()

    def handle_progress_bar(self):
        fraction = float(self.counted_results)/self.total_images
        self.parse_results_progress.set_fraction(fraction)
        self.counted_results += 1
        if self.counted_results >= self.total_images:
            self.remove(self.parse_results_progress)

def get_image_uri(text):
  thumbre = {
    'twitpic': 'http://.*twitpic.com/(?!photos)([A-Za-z0-9]+)',
    'img.gd': 'http://img.gd/(?!photos)([A-Za-z0-9]+)',
    'imgur': 'http://.*imgur.com/(?!gallery)([A-Za-z0-9]+)',
    'twitgoo': 'http://.*twitgoo.com/(?!u/)([A-Za-z0-9]+)',
    'yfrog.us': 'http://.*yfrog.us/(?!froggy)([A-Za-z0-9]+)',
    'yfrog.com': 'http://.*yfrog.com/(?!froggy)([A-Za-z0-9]+)',
    'twitvid': 'http://.*twitvid.com/(?!videos)([A-Za-z0-9]+)',
    'img.ly': 'http://img.ly/(?!images)([A-Za-z0-9]+)', 
    'flic.kr': 'http://flic.kr/p/([A-Za-z0-9]+)',
    'youtu.be': 'http://youtu.be/([A-Za-z0-9-_]+)',
    'youtube.com': 'http://.*youtube.com/watch\?v=([A-Za-z0-9-_]+)',
    'tweetphoto': 'http://.*tweetphoto.com/(0-9]+)',
    'pic.gd': 'http://pic.gd/([A-Za-z0-9]+)',
    'brizzly': 'http://.*brizzly.com/pic/([A-Za-z0-9]+)',
    'twitxr': 'http://.*twitxr.com\/[^ ]+\/updates\/([0-9]+)',
    'ow.ly': 'http://ow.ly/i/([A-Za-z0-9]+)',
    'ts1.in': 'http://ts1.in/([0-9]+)',
    'twitsnaps': 'http://.*twitsnaps.com/([0-9]+)',
    'hellotext': 'http://.*hellotxt.com/i/([A-Za-z0-9]+)',
    'htxt.it': 'http://htxt.it/i/([A-Za-z0-9]+)',
    'moby.to': 'http://moby.to/([A-Za-z0-9]+)',
    'movapic': 'http://.*movapic.com/pic/([A-Za-z0-9]+)',
    'znl.me': 'http://znl.me/([A-Za-z0-9-_]+)',
    'bcphotoshare': 'http://.*bcphotoshare.com/photos/[0-9]+/([0-9]+)',
    'twitvideo.jp': 'http://.*twitvideo.jp/(?!contents)([A-Za-z0-9-_]+)'
    }
  thumburi = {
    'twitpic': 'http://twitpic.com/show/thumb/@',
    'img.gd': 'http://img.gd/show/thumb/@',
    'imgur': 'http://i.imgur.com/@s.jpg',
    'twitgoo': 'http://twitgoo.com/show/thumb/@',
    'yfrog.us': 'http://yfrog.us/@.th.jpg',
    'yfrog.com': 'http://yfrog.com/@.th.jpg',
    'twitvid': 'http://images.twitvid.com/@.jpg',
    'img.ly': 'http://img.ly/show/thumb/@',
    'flic.kr': 'http://flic.kr/p/img/@_m.jpg',
    'youtu.be': 'http://img.youtube.com/vi/@/default.jpg',
    'youtube.com': 'http://img.youtube.com/vi/@/default.jpg',
    'tweetphoto': 'http://TweetPhotoAPI.com/api/TPAPI.svc/json/imagefromurl?size=thumbnail&url=@',
    'pic.gd': 'http://TweetPhotoAPI.com/api/TPAPI.svc/json/imagefromurl?size=thumbnail&url=@',
    'brizzly': 'http://pics.brizzly.com/thumb_sm_@.jpg',
    'twitxr': 'http://twitxr.com/image/@/th/',
    'ow.ly': 'http://static.ow.ly/photos/thumb/@.jpg',
    'ts1.in': 'http://ts1.in/mini/@',
    'twitsnaps': 'http://twitsnaps.com/mini/@',
    'hellotext': 'http://hellotxt.com/image/@.s.jpg',
    'htxt.it': 'http://hellotxt.com/image/@.s.jpg',
    'moby.to': 'http://api.mobypicture.com?s=small&format=plain&k=6JQhCKX6Z9h2m9Lo&t=@',
    'movapic': 'http://image.movapic.com/pic/s_@.jpeg',
    'znl.me': 'http://app.zannel.com/content/@/Image-160x120-P-JPG.jpg',
    'bcphotoshare': 'http://images.bcphotoshare.com/storages/@/thumbnail.jpg',
    'twitvideo.jp': 'http://twitvideo.jp/img/thumb/@'
    }

  imguri = {
    'twitpic': 'http://twitpic.com/show/full/@',
    'img.gd': 'http://img.gd/show/thumb/@',#will have to screenscrape full image
    'imgur': 'http://i.imgur.com/@l.jpg',
    'twitgoo': 'http://twitgoo.com/show/thumb/@',
    'yfrog.us': 'http://yfrog.com/@:medium',
    'yfrog.com': 'http://yfrog.com/@:medium',
    'twitvid': 'http://images.twitvid.com/@.jpg',
    'img.ly': 'http://img.ly/show/thumb/@',
    'flic.kr': 'http://flic.kr/p/img/@_m.jpg',#(http://www.flickr.com/services/api/misc.urls.html)
    'youtu.be': 'http://img.youtube.com/vi/@/0.jpg',
    'youtube.com': 'http://img.youtube.com/vi/@/0.jpg',
    'tweetphoto': 'http://TweetPhotoAPI.com/api/TPAPI.svc/json/imagefromurl?size=thumbnail&url=@',
    'pic.gd': 'http://TweetPhotoAPI.com/api/TPAPI.svc/json/imagefromurl?size=thumbnail&url=@',
    'brizzly': 'http://pics.brizzly.com/thumb_sm_@.jpg',
    'twitxr': 'http://twitxr.com/image/@/th/',
    'ow.ly': 'http://static.ow.ly/photos/thumb/@.jpg',
    'ts1.in': 'http://ts1.in/mini/@',
    'twitsnaps': 'http://twitsnaps.com/mini/@',
    'hellotext': 'http://hellotxt.com/image/@.s.jpg',
    'htxt.it': 'http://hellotxt.com/image/@.s.jpg',
    'moby.to': 'http://api.mobypicture.com?s=small&format=plain&k=6JQhCKX6Z9h2m9Lo&t=@',
    'movapic': 'http://image.movapic.com/pic/s_@.jpeg',
    'znl.me': 'http://app.zannel.com/content/@/Image-160x120-P-JPG.jpg',
    'bcphotoshare': 'http://images.bcphotoshare.com/storages/@/thumbnail.jpg',
    'twitvideo.jp': 'http://twitvideo.jp/img/thumb/@'
    }


  if text.find("fbcdn.net") > -1:
    return text.replace("_s.jpg","_n.jpg")

  for r, u, i in zip(thumbre, thumburi, imguri):
    for match in re.finditer(thumbre[r], text):
      if r == 'tweetphoto' or r == 'pic.gd' or r == 'moby.to':
        image = ({"th_uri": thumburi[u].replace('@', match.group(0)) , 
                  "src": match.group(0) ,
                  "img_uri": imguri[i].replace('@', match.group(0))})
      else:
        image = ({"th_uri": thumburi[u].replace('@', match.group(1)) ,
                  "src": match.group(0) ,
                  "img_uri": imguri[i].replace('@', match.group(1))})
      return image


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
