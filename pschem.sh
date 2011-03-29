#!/bin/sh

#set style = polyester
#set style = oxygen
#set style = qtcurve
#set style = windows
#set style = windowsxp
#set style = windowsvista
#set style = mac
#set style = plastique
#set style = cleanlooks
#set style = gtk
#set style = motif
#set style = cde

set graphicssystem = native
#set graphicssystem = raster

exec python pschem.py -style ${style} -graphicssystem ${graphicssystem}
