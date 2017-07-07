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
import gtk
import gobject
#from quickly.widgets.web_cam_box import WebCamBox
from ImageListPage import ImageListPage
from web_cam_box import WebCamBox

class CameraPage(ImageListPage):  
    def __init__(self):
        gtk.VBox.__init__(self,False, 0)
        self.__camera = WebCamBox()
        self.__camera.connect("image-captured",self.image_captured)
        self.__camera.show()
        self.__camera.set_size_request(196, 196)
        self.pack_start(self.__camera, False, False)

        button = gtk.Button("Take Picture")
        button.show()
        button.connect("clicked", lambda x:self.__camera.take_picture())
        self.pack_start(button, False, False)
        self.waiting_for_camera = False       
        self.wait_ticks = 0

    def image_captured(self, widget, path):
        self.emit("clicked",path)

    def on_selected(self):
        if self.__camera.realized:
            self.__camera.play()
        else:
            if not self.waiting_for_camera:
                self.waiting_for_camera = True
                gobject.timeout_add(100, self._play_if_ready)

    def _play_if_ready(self):
        if self.__camera.realized:
            self.__camera.play()
            self.waiting_for_camera = False       
            self.wait_ticks = 0
            return False
        else:
            self.wait_ticks += 1
            if self.wait_ticks > 20:
                print _("Camera not ready, aborting wait")
                self.waiting_for_camera = False       
                self.wait_ticks = 0
                return False
            else:
                return True

    def on_deselected(self):
        self.__camera.stop()

