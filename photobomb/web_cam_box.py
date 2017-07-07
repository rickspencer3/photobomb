#!/usr/bin/python
# -*- coding: utf-8 -*-
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

"""A VBox that tries to turn on and display the default webcam for the
computer on which it is running. It is also capable of saving an image
from the webcam to the user's Picture directory.

Using
#create the a WebCamBox
cam = WebCamBox()

#the camera should be playing before you try to do other
#operations with it, such as taking a picture.
cam.play()

#to save a picture and save it to ~/Pictures
cam.take_picture()

#connect to the image-captured signal to do something
automatically with a picture.
cam.connect("image-captured", self.on_picture_captured)

def on_picture_captured(self,widget, filename, data=None):
    #do something with the filename

Configuring
#You can set a string that prepends the default datestamp filenames
#this will result in filenames such as "myapp_2010-09-04 09:37:32.957580.png"
cam.filename_prefix = "myapp_"

#If you want access to all the gstreamer knobs and dials, you can just
#get a reference to the camerabin (see gstreamer documentation for details.
cam.camerabin.set_property(property_name,value)

#you can send the camerabin signals in this was, as well
cam.camerbin.emit(signal_name)

#You can add Widgets to the WebCamBox simply by packing them in
cam.pack_start(my_widget, False, False)

Extending
A WebCamBox is gtk.VBox
A WebCamBox is a gtk.VBox that contains a gtk.DrawingArea for displaying
webcam output, and a thin wrapper around a camerabin, which is a gstreamer
pipleine sublcass that provides all the camera functionality.

To add GUI elements simple, create them and pack them into WebCamBox, since
it's just a gtk.VBox

Similarly, to add to or change the web cam functionality, modify properties on
the camerabin. You may also want to overide _on_message and/or _on_sync_message
to catch messages from the bus and add behavior.

"""

import sys
import os
import gtk
import gst
import datetime
import gobject
import glib

import gettext
from gettext import gettext as _
gettext.textdomain('quickly-widgets')

class WebCamBox(gtk.VBox):
    """WebCamBox - A VBox that tries to turn on and display the default webcam for the
        computer on which it is running. It is also capable of saving an image
        from the webcam to the user's Picture directory.

    """

    def __init__(self):
        """Creates a WebCamBox, incuding initalizing the default camera. Note
        that this does not start the camera streaming. For that call play().
        
        This function has no arguments

        """
        gtk.VBox.__init__(self, False, 5)
        self.video_window = gtk.DrawingArea()
        self.video_window.connect("realize",self.__on_video_window_realized)
        self.pack_start(self.video_window, True, True)
        self.video_window.show()
        self.connect("destroy", self.on_destroy)

        self.camerabin = gst.element_factory_make("camerabin", "camera-source")
        bus = self.camerabin.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self._on_message)
        bus.connect("sync-message::element", self._on_sync_message)
        #self.camerabin.set_property("image-encoder",gst.element_factory_make("pngenc", "png_encoder"))
        self.filename_prefix = ""
        self.realized = False

    def play(self):
        """play - Start the camera streaming and display the output. It is
        necessary to start the camera playing before using most other functions.
    
        This function has no arguments
        
        """

        if not self.realized:
            self._set_video_window_id()
        if not self.realized:
            print _("Cannot display web cam output. Ignoring play command")
        else:
            self.camerabin.set_state(gst.STATE_PLAYING)

    def pause(self):
        """pause - Pause the camera output. It will cause the image to
        "freeze". Use play() to start the camera playng again. Note that
        calling pause before play may cause errors on certain camera.
    
        This function has no arguments
        
        """

        self.camerabin.set_state(gst.STATE_PAUSED)

    def take_picture(self):
        """take_picture - grab a frame from the web cam and save it to
        ~/Pictures/datestamp.png, where datestamp is the current datestamp.
        It's possible to add a prefix to the datestamp by setting the
        filename_prefix property. 

        If play is not called before take_picture,
        an error may occur. If take_picture is called immediately after play,
        the camera may not be fully initialized, and an error may occur.        
    
        Connect to the signal "image-captured" to be alerted when the picture
        is saved.

        This function has no arguments

        returns - a string of the filename used to save the image
        
        """

        stamp = str(datetime.datetime.now())
        extension = ".jpg"#".png"
        directory =  glib.get_user_special_dir(glib.USER_DIRECTORY_PICTURES)
        self.filename = directory + self.filename_prefix + stamp + extension
        self.camerabin.set_property("filename", self.filename)
        self.camerabin.emit("capture-start")
        return self.filename

    def stop(self):
        """stop - Stop the camera streaming and display the output.
    
        This function has no arguments
        
        """

        self.camerabin.set_state(gst.STATE_NULL)

    def _on_message(self, bus, message):
        """ _on_message - internal signal handler for bus messages.
        May be useful to extend in a base class to handle messages
        produced from custom behaviors.


        arguments -
        bus: the bus from which the message was sent, typically self.bus
        message: the message sent

        """

        t = message.type
        if t == gst.MESSAGE_ELEMENT:
            if message.structure.get_name() == "image-captured":
                #work around to keep the camera working after lots
                #of pictures are taken
                self.camerabin.set_state(gst.STATE_NULL)
                self.camerabin.set_state(gst.STATE_PLAYING)

                self.emit("image-captured", self.filename)

        if t == gst.MESSAGE_EOS:
            self.camerabin.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

    def _on_sync_message(self, bus, message):
        """ _on_sync_message - internal signal handler for bus messages.
        May be useful to extend in a base class to handle messages
        produced from custom behaviors.


        arguments -
        bus: the bus from which the message was sent, typically self.bus
        message: the message sent

        """

        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_xwindow_id(self.video_window.window.xid)

    def __on_video_window_realized(self, widget, data=None):
        """__on_video_window_realized - internal signal handler, used
        to set up the xid for the drawing area in thread safe manner.
        Do not call directly.

        """

        self._set_video_window_id()

    def _set_video_window_id(self):
        if not self.realized and self.video_window.window is not None:
            x = self.video_window.window.xid
            self.realized = True

    def on_destroy(self, widget, data=None):
        #clean up the camera before exiting
        self.camerabin.set_state(gst.STATE_NULL)
        
    __gsignals__ = {'image-captured' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
		(gobject.TYPE_PYOBJECT,)),
		} 

def __image_captured(widget, data=None):
    """ __image_captured - internal function for testing callbacks
    from the test app.

    """

    quickly.prompts.info("WebCam Test",data)    

if __name__ == "__main__":
    """creates a test WebCamBox"""
    import quickly.prompts

    #create and show a test window
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    win.set_title("WebCam Test Window")
    win.connect("destroy",gtk.main_quit)
    win.show()

    #create a top level container
    vbox = gtk.VBox(False, 10)
    vbox.show()
    win.add(vbox)

    mb = WebCamBox()
    mb.video_frame_rate = 30
    vbox.add(mb)
    mb.show()
    mb.play()

    mb.connect("image-captured", __image_captured)
    play_butt = gtk.Button("Play")
    pause_butt = gtk.Button("Pause")
    stop_butt = gtk.Button("Stop")
    pic_butt = gtk.Button("Picture")

    play_butt.connect("clicked", lambda x:mb.play())
    play_butt.show()
    mb.pack_end(play_butt, False)

    pause_butt.connect("clicked", lambda x:mb.pause())
    pause_butt.show()
    mb.pack_end(pause_butt, False)

    stop_butt.connect("clicked", lambda x:mb.stop())
    stop_butt.show()
    mb.pack_end(stop_butt, False)

    pic_butt.connect("clicked", lambda x:mb.take_picture())
    pic_butt.show()
    mb.pack_end(pic_butt, False)

    gtk.main()


