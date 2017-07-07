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

from photobomb.photobombconfig import getdatapath

class AboutPhotobombDialog(gtk.AboutDialog):
    __gtype_name__ = "AboutPhotobombDialog"

    def __init__(self):
        """__init__ - This function is typically not called directly.
        Creation of a AboutPhotobombDialog requires redeading the associated ui
        file and parsing the ui definition extrenally, 
        and then calling AboutPhotobombDialog.finish_initializing().
    
        Use the convenience function NewAboutPhotobombDialog to create 
        NewAboutPhotobombDialog objects.
    
        """
        pass

    def finish_initializing(self, builder):
        """finish_initalizing should be called after parsing the ui definition
        and creating a AboutPhotobombDialog object with it in order to finish
        initializing the start of the new AboutPhotobombDialog instance.
    
        """
        #get a reference to the builder and set up the signals
        self.builder = builder
        self.builder.connect_signals(self)

        #code for other initialization actions should be added here

def NewAboutPhotobombDialog():
    """NewAboutPhotobombDialog - returns a fully instantiated
    AboutPhotobombDialog object. Use this function rather than
    creating a AboutPhotobombDialog instance directly.
    
    """

    #look for the ui file that describes the ui
    ui_filename = os.path.join(getdatapath(), 'ui', 'AboutPhotobombDialog.ui')
    if not os.path.exists(ui_filename):
        ui_filename = None

    builder = gtk.Builder()
    builder.add_from_file(ui_filename)    
    dialog = builder.get_object("about_photobomb_dialog")
    dialog.finish_initializing(builder)
    return dialog

if __name__ == "__main__":
    dialog = NewAboutPhotobombDialog()
    dialog.show()
    gtk.main()

