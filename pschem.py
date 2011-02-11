#!/usr/bin/env python

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

# This file is part of PSchem.
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PSchem.  If not, see <http://www.gnu.org/licenses/>.

import sys

#import cProfile
#import pstats

from PyQt4 import QtCore, QtGui

from PSchem import PWindow

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():    
    #QtGui.QApplication.setGraphicsSystem('raster')
    app = QtGui.QApplication(sys.argv)
    sf = QtGui.QStyleFactory()
    print list(sf.keys())
    print QtGui.qApp.style().metaObject().className()
    QtGui.qApp.setStyle(sf.create('windowsxp'))
    #QtGui.qApp.setStyle(sf.create('cleanlooks'))
    #QtGui.qApp.setStyle(sf.create('motif'))
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))
    window = PWindow.PWindow()
    window.show()

    sys.exit(app.exec_())

    #cProfile.run('app.exec_()', 'profdata')
    #p = pstats.Stats('profdata')
    #p.sort_stats('time').print_stats()


if __name__ == "__main__":
    main()
