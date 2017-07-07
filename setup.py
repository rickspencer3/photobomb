#!/usr/bin/env python
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

###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

try:
    import DistUtilsExtra.auto
except ImportError:
    import sys
    print >> sys.stderr, 'To build photobomb you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)

assert DistUtilsExtra.auto.__version__ >= '2.10', 'needs DistUtilsExtra.auto >= 2.10'
import os


def update_data_path(prefix, oldvalue=None):

    try:
        fin = file('photobomb/photobombconfig.py', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:            
            fields = line.split(' = ') # Separate variable from value
            if fields[0] == '__photobomb_data_directory__':
                # update to prefix, store oldvalue
                if not oldvalue:
                    oldvalue = fields[1]
                    line = "%s = '%s'\n" % (fields[0], prefix)
                else: # restore oldvalue
                    line = "%s = %s" % (fields[0], oldvalue)
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find photobomb/photobombconfig.py")
        sys.exit(1)
    return oldvalue


def update_desktop_file(datadir):

    try:
        fin = file('photobomb.desktop.in', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:            
            if 'Icon=' in line:
                line = "Icon=%s\n" % (datadir + 'media/icon.png')
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find photobomb.desktop.in")
        sys.exit(1)


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        if self.root or self.home:
            print "WARNING: You don't use a standard --prefix installation, take care that you eventually " \
            "need to update quickly/quicklyconfig.py file to adjust __quickly_data_directory__. You can " \
            "ignore this warning if you are packaging and uses --prefix."
        previous_value = update_data_path(self.prefix + '/share/photobomb/')
        update_desktop_file(self.prefix + '/share/photobomb/')
        DistUtilsExtra.auto.install_auto.run(self)
        update_data_path(self.prefix, previous_value)


        
##################################################################################
###################### YOU SHOULD MODIFY ONLY WHAT IS BELOW ######################
##################################################################################

DistUtilsExtra.auto.setup(
    name='photobomb',
    version='11.08.2',
    license='GPL-3',
    author='Rick Spencer',
    author_email='rick.spencer@canonical.com',
    description='Easy and Social Image Editor',
    long_description='Photobomb give you easy access to images in your social networking feeds, pictures on your computer and peripherals, and pictures on the web, and let\'s you draw, write, crop, combine, and generally have a blast mashing \'em all up. Then you can save off your photobomb, or tweet your creation right back to your social network.',
    url='https://launchpad.net/photobomb',
    cmdclass={'install': InstallAndUpdateDataDirectory}
    )

