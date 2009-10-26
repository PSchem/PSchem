#!/usr/bin/env python

import sys

#import cProfile
#import pstats

from PyQt4 import QtCore, QtGui

#import PSchem
from PSchem import *
#from Database import *


import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


if __name__ == "__main__":
    #QtGui.QApplication.setGraphicsSystem('raster')
    app = QtGui.QApplication(sys.argv)
    QtCore.qsrand(QtCore.QTime(0,0,0).secsTo(QtCore.QTime.currentTime()))
    window = PWindow.PWindow()
    window.show()

    sys.exit(app.exec_())

    #cProfile.run('app.exec_()', 'profdata')
    #p = pstats.Stats('profdata')
    #p.sort_stats('time').print_stats()
