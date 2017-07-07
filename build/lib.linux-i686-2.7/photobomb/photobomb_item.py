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

import goocanvas
import Image, ImageEnhance
import os
import StringIO
import gtk
from photobomb.photobombconfig import getdatapath

#TODO Make a PhotobombItem baseclass, and multiple inherit
class PhotobombItem(object):
    __color_property = "fill_color_rgba"
    def __init__(self, goocanvas):
        self.opacity = 65535
        self.goocanvas = goocanvas

    @property
    def line_width(self):
        return None

    @line_width.setter
    def line_width(self, width):
        pass

    @property
    def color(self):
        return None

    @color.setter
    def color(self, ink_color):
        pass

    @property
    def font(self):
        return None

    @font.setter
    def font(self, font_name):
        pass

    @property
    def text(self):
        return ""

    @text.setter
    def text(self, text):
        pass

    def set_clip_path(self, data):
        if data is not None:
            self._clip_path = data
            self.set_property("clip-path", self._clip_path)

    def grow(self):
        bounds = self.get_bounds()
        cx = bounds.x1 + (bounds.x2-bounds.x1)/2
        cy = bounds.y1 + (bounds.y2-bounds.y1)/2
        old_cx, old_cy = self.goocanvas.convert_to_item_space(self,cx, cy)

        self.scale(1.1,1.1)
        cx = bounds.x1 + (bounds.x2-bounds.x1)/2
        cy = bounds.y1 + (bounds.y2-bounds.y1)/2
        new_cx, new_cy = self.goocanvas.convert_to_item_space(self,cx, cy)
        self.translate(new_cx - old_cx, new_cy - old_cy)

    def shrink(self):
        bounds = self.get_bounds()
        cx = bounds.x1 + (bounds.x2-bounds.x1)/2
        cy = bounds.y1 + (bounds.y2-bounds.y1)/2
        old_cx, old_cy = self.goocanvas.convert_to_item_space(self,cx, cy)

        self.scale(.9,.9)
        cx = bounds.x1 + (bounds.x2-bounds.x1)/2
        cy = bounds.y1 + (bounds.y2-bounds.y1)/2
        new_cx, new_cy = self.goocanvas.convert_to_item_space(self,cx, cy)
        self.translate(new_cx - old_cx, new_cy - old_cy)

    def rotate(self, degrees):
        bounds = self.get_bounds()
        cx = bounds.x1 + (bounds.x2-bounds.x1)/2
        cy = bounds.y1 + (bounds.y2-bounds.y1)/2
        new_cx, new_cy = self.goocanvas.convert_to_item_space(self,cx, cy)
        goocanvas.Item.rotate(self,degrees,new_cx,new_cy)

    def move(self, x_distance, y_distance):
        bounds = self.get_bounds()
        cx = bounds.x1 + (bounds.x2-bounds.x1)/2
        cy = bounds.y1 + (bounds.y2-bounds.y1)/2
        old_cx, old_cy = self.goocanvas.convert_to_item_space(self,cx, cy)

        new_cx, new_cy = self.goocanvas.convert_to_item_space(self,cx + x_distance, cy + y_distance)
        self.translate(new_cx - old_cx, new_cy - old_cy)

    def move_to_bounds(self, new_bounds):
        old_bounds = self.get_bounds()
        old_x, old_y = self.goocanvas.convert_to_item_space(self, old_bounds.x1, old_bounds.y1)
        new_x, new_y = self.goocanvas.convert_to_item_space(self, new_bounds.x1, new_bounds.y1)
        self.translate(new_x - old_x, new_y - old_y)

    def bring_to_top(self):
        goocanvas.Item.raise_(self, None)

    def send_to_bottom(self):
        goocanvas.Item.lower(self, None)

    def increase_opacity(self):
        opac = self.opacity + 65535/20
        if opac >= 65535:
            opac = 65535
        self.opacity = opac
        self.change_opacity(opac)

    def decrease_opacity(self):
        opac = self.opacity - 65535/20
        if opac < (65535/20):
            opac = 65535/20
        self.opacity = opac
        self.change_opacity(opac)

    @property
    def opacity_percentage(self):
        return int(float(self.opacity)/65535 * 100)

    @opacity_percentage.setter
    def opacity_percentage(self, percent):    
        opac = int(65535 * (percent/100.00))
        self.opacity = opac
        self.change_opacity(opac)
                
    def change_opacity(self, opacity):
        color = self.get_property("fill_color_rgba")
        color = self._rgba_change_opacity(color,opacity)
        self.set_property("fill_color_rgba",color)

    def _rgba_change_opacity(self, color, opac):
            red = color * 0x100 >> 24
            green = color * 0x100 >> 16
            blue = color * 0x100 >> 8
            color =  (((red / 0x100) << 24) | ((green / 0x100) << 16) | ((blue / 0x100) << 8) | (opac / 0x100))
            return color

    @property
    def rgba_color(self):
        return self.get_property(self.__color_property)

    @rgba_color.setter
    def rgba_color(self, color):
        self.set_property(self.__color_property, color)

class PhotobombPath(PhotobombItem, goocanvas.Path):
    __color_property = "stroke_color_rgba"
    def __init__(self, gc, data, width, ink_color):
        self.__data = data
        self._clip_path = None
        self._stroke_color = ink_color
        goocanvas.Path.__init__(self, data=data, parent=gc.get_root_item(), 
                                   line_width=width, stroke_color=str(ink_color))
        PhotobombItem.__init__(self, gc)
        point_strings = data.split("C")[1].split(" ")
        self._end_x = float(point_strings[-2])
        self._end_y = float(point_strings[1])
        self._draw_tick = 0
        self._temp_path = ""
     

    @property
    def line_width(self):
        return self.get_property("line_width")

    @line_width.setter
    def line_width(self, width):
        self.set_property("line_width",width)        

    @property
    def color(self):
        return self._stroke_color

    @color.setter
    def color(self, ink_color):
        self._stroke_color = ink_color
        self.set_property("stroke_color",str(ink_color))
        self.change_opacity(self.opacity)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self,data):
        self.set_property("data",data)
        self.__data = data

    def duplicate(self, with_clip=True, offset=True):
        pi = PhotobombPath(self.goocanvas, self.data, self.line_width, self.color)
        if self._clip_path is not None and with_clip:
            pi.set_clip_path(self._clip_path)        
        pi.set_transform(self.get_transform())
        pi.color = self.color
        pi.font = self.font
        if offset:
            pi.translate(10,10)
        pi.opacity = self.opacity
        pi.change_opacity(pi.opacity)
        return pi

    def change_opacity(self, opacity):
        color = self.get_property("stroke_color_rgba")
        color = self._rgba_change_opacity(color,opacity)
        self.set_property("stroke_color_rgba",color)

    def append(self, x, y):
        self.data += " " + str(x) + " " + str(y)
        return
        #here's how it's going to go:
        #we'll draw segments in sets of 100 to start
        #so, keep drawing and drawing until there are 100 segments
        #then finish that stroke, and start a new stroke, and that one has been drawn 100 times
        self._draw_tick += 1

        if self._temp_path == "":
            self.temp_path = "M " + str(self._end_x) + " " + str(self._end_y)
            self.temp_path += "C" + str(x) + " " + str(y)
        goocanvas.Path(data=path_data,parent=self.goocanvas.get_root_item())
        self._end_x = x
        self._end_y = y

class PhotobombText(PhotobombItem, goocanvas.Text):
    def __init__(self, gc, text,ink_color):
        self._clip_path = None
        self._ink_color = ink_color
        goocanvas.Text.__init__(self, parent=gc.get_root_item(),text=text, x=100, y=100, fill_color=str(ink_color))
        PhotobombItem.__init__(self, gc)

    @property
    def color(self):
        return self._ink_color

    @color.setter
    def color(self, ink_color):
        self.set_property("fill-color",str(ink_color))
        self._ink_color = ink_color
        self.change_opacity(self.opacity)

    @property
    def font(self):
        return self.get_property("font")

    @font.setter
    def font(self, font_name):
        self.set_property("font", font_name)

    @property
    def text(self):
        return self.get_property("text")

    @text.setter
    def text(self, text):
        self.set_property("text",text)

    def duplicate(self, with_clip=True, offset=True):
        pi = PhotobombText(self.goocanvas, self.text, self.color)

        if self._clip_path is not None and with_clip:
            pi.set_clip_path(self._clip_path)        
        pi.set_transform(self.get_transform())
        pi.color = self.color
        pi.font = self.font
        if offset:
            pi.translate(10,10)

        pi.opacity = self.opacity
        pi.change_opacity(pi.opacity)
        return pi

class PhotobombImage(PhotobombItem, goocanvas.Image):
    temp_dir = os.path.join(os.environ["HOME"],".tmp","photobomb")
    def __init__(self, gc, pixbuf,x=None,y=None):
        self.pixbuf = pixbuf
        self._original_pixbuf = pixbuf
        self._clip_path = None
        if x is None and y is None:
            cont_left, cont_top, cont_right, cont_bottom = gc.get_bounds()
            img_w = self.pixbuf.get_width()
            img_h = self.pixbuf.get_height()
            img_left = (cont_right - img_w)/2
            img_top = (cont_bottom - img_h)/2
        else:
            img_left = x
            img_top = y

        goocanvas.Image.__init__(self, parent=gc.get_root_item(), pixbuf=self.pixbuf,
                                x=img_left,y=img_top)
        PhotobombItem.__init__(self, gc)
        path = os.path.join(getdatapath(),"media","trans.png")
        self.transparent_img = gtk.gdk.pixbuf_new_from_file(path)
        self.opacity = 255

    def increase_opacity(self):
        opac = self.opacity + 255/20
        if opac >= 255:
            opac = 255
        self.opacity = opac
        self.change_opacity(opac)

    def decrease_opacity(self):
        opac = self.opacity - 255/20
        if opac < (255/20):
            opac = 255/20
        self.opacity = opac
        self.change_opacity(opac)

    @property
    def opacity_percentage(self):
        return int(float(self.opacity)/255 * 100)

    @opacity_percentage.setter
    def opacity_percentage(self, percent):    
        opac = int(255 * (percent/100.00))
        self.opacity = opac
        self.change_opacity(opac)

    def change_opacity(self, opacity):
        """
        change_opacity - changes the opacity by combining
        the pixbuf with a pixbuf derived from a transparent .png

        arguments:
        opacity - the degree of desired opacity (between 0 and 255)

        """

        trans = self.transparent_img
        width = self.pixbuf.get_width()
        height = self.pixbuf.get_height()
        trans = trans.scale_simple(width,height,gtk.gdk.INTERP_NEAREST)
        self.pixbuf.composite(trans, 0, 0, width, height, 0, 0, 1, 1, gtk.gdk.INTERP_NEAREST, opacity)
        self.set_property("pixbuf", trans)

    def duplicate(self, with_clip=True, offset=True):

        pi = PhotobombImage(self.goocanvas, self.pixbuf)

        if self._clip_path is not None and with_clip:
            pi.set_clip_path(self._clip_path)        
        pi.set_transform(self.get_transform())
        if offset:
            pi.translate(10,10)
        pi.opacity = self.opacity
        pi.change_opacity(pi.opacity)
        return pi

