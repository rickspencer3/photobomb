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

from photobomb.photobombconfig import getdatapath
from gwibber.lib.gtk import widgets

class MicroblogDialog(gtk.Window):

    def __init__(self, contents, parent=None):
        gtk.Window.__init__(self)
        self.set_default_size(420,140)
        poster = widgets.GwibberPosterVBox()
        poster.input.connect("submit",self.submitted)
        poster.button_send.connect("clicked", self.submitted)
        self.expose_event = poster.connect("expose-event", self.on_expose_input, contents)
        self.add(poster)
        self.show_all()

    def on_expose_input(self, widget, event, contents):
        widget.disconnect(self.expose_event)
        widget.input.set_text(contents)

    def submitted(self, *args):
        self.destroy()

