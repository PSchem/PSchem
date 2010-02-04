# -*- coding: utf-8 -*-

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

# This file is part of PSchem Database
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with PSchem Database.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
from Database.Primitives import *
from Database.Cells import *
from Database.Layers import *
#from Database.Primitives import Database


class Reader():
    def __init__(self, database):
        self._database = database
    
    def parseSchematic(self, fileName, cellView):
        pass
    
    def parseSymbol(self, fileName, cellView):
        pass
    
    def parseNetlist(self, fileName, cellView):
        pass
    
    def parseLayout(self, fileName, cellView):
        pass
    
    def parsePCB(self, fileName, cellView):
        pass
        
    
class GedaReader(Reader):
    uu = 100 #default database units / user units
    peof = re.compile(r'^$')
    pempty = re.compile(r'^\s*$')
    pschStrip = re.compile(r'\.sch$')
    psymStrip = re.compile(r'\.sym$')
    pnewlineStrip = re.compile(r'\n$')
    pversion = re.compile(r'^v\s+(\d+)\s+(\d+)')
    pline = re.compile(r'^L\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    pbox = re.compile(r'^B\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    pcircle = re.compile(r'^V\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    parc = re.compile(r'^A\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    ptext = re.compile(r'^T\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    pnet = re.compile(r'^N\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    pbus = re.compile(r'^U\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    ppin = re.compile(r'^P\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    pcomponent = re.compile(r'^C\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(\S+)')
    ppath = re.compile(r'^H\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)')
    ppath_move = re.compile(r'^M\s+(-?\d+)[,\s]\s*(-?\d+)$')
    ppath_line = re.compile(r'^L\s+(-?\d+)[,\s]\s*(-?\d+)$')
    ppath_curve = re.compile(r'^C\s+(-?\d+)[,\s]\s*(-?\d+)\s+(-?\d+)[,\s]\s*(-?\d+)\s+(-?\d+)[,\s]\s*(-?\d+)$')
    ppath_close = re.compile(r'^[zZ]$')
    pattr_start = re.compile(r'^\s*\{\s*$')
    pattr_stop = re.compile(r'^\s*\}\s*$')
    pattr = re.compile(r'^(\S+)\s*\=\s*(.+)$')
    pembed_start = re.compile(r'^\s*\[\s*$')
    pembed_stop = re.compile(r'^\s*\]\s*$')


    def __init__(self, importer):
        Reader.__init__(self, importer.database)
        self.importer = importer
        self.inSchematic = False
        self.inSymbol = False
        self.inAttribute = False
        self.view = None
        self.match = None

    def readLine(self):
        return self.f.readline()
    
    def parseVersion(self):
        pass
        #m=self.match
        #a = Attribute(self.view, 'geda_version', [int(m.group(1)), int(m.group(2))])
        #self.last = a
        #self.view.addElem(a)

    def parseLine(self):
        m=self.match
        l = Line(self.view, self._database.layers(), int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        self.last = l
        self.view.addElem(l)

    def parseArc(self):
        m=self.match
        radius = 2 * int(m.group(3))
        e = EllipseArc(self.view, self._database.layers(), int(m.group(1)), int(m.group(2)), radius, radius, int(m.group(4)), int(m.group(5)))
        self.last = e
        self.view.addElem(e)

    def parsePin(self):
        m=self.match
        p = Pin(self.view, self._database.layers(), int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        self.last = p
        self.view.addElem(p)

    def parseNet(self):
        m=self.match
        n = NetSegment(self.view, self._database.layers(), int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        self.last = n
        self.view.addElem(n)

    def parseBox(self):
        m=self.match
        r = Rect(self.view, self._database.layers(), int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        self.last = r
        self.view.addElem(r)

    def parseCustomPath(self):
        m=self.match
        p = CustomPath(self.view, self._database.layers())
        #, int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        for n in range(int(m.group(13))):
            line = self.readLine()
            line = self.pnewlineStrip.sub('', line)
            if (self.regExpSearch(self.ppath_move, line)):
                p.moveTo(int(self.match.group(1)),
                         int(self.match.group(2)))
            elif (self.regExpSearch(self.ppath_line, line)):
                p.lineTo(int(self.match.group(1)),
                         int(self.match.group(2)))
            elif (self.regExpSearch(self.ppath_curve, line)):
                p.curveTo(int(self.match.group(1)),
                          int(self.match.group(2)),
                          int(self.match.group(3)),
                          int(self.match.group(4)),
                          int(self.match.group(5)),
                          int(self.match.group(6)))
            elif (self.regExpSearch(self.ppath_close, line)):
                p.closePath()
        p.setLayer(self._database.layers().layerByName('annotation2', 'drawing'))
        self.last = p
        self.view.addElem(p)

    def parseCircle(self):
        m=self.match
        radius = 2 * int(m.group(3))
        c = Ellipse(self.view, self._database.layers(), int(m.group(1)), int(m.group(2)), radius, radius)
        self.last = c
        self.view.addElem(c)

    def parseComponent(self):
        m=self.match
        symbolName = m.group(6)
        #r = GedaReader(self.importer.database, self.library)
        #r = self
        #c = r.parseSymbol(symbolName)
        cellName = self.psymStrip.sub('', m.group(6))
        lib = self.importer.findCellSymbolLibrary(cellName)
        #print lib
        #print m.group(6)
        #c = self.importer.getCellByName(m.group(6))
        #c = lib.cellByName(m.group(6))
        i = Instance(self.view, self._database.layers())
        i.setXY(int(m.group(1)), int(m.group(2)))
        i.setAngle(int(m.group(4)))
        i.setHMirror(int(m.group(5)) == 1)

        if not lib or lib == self.importer.library:
            i.setCell('', cellName, 'symbol')
            #i = Instance(self.view, int(m.group(1)), int(m.group(2)), int(m.group(4)), int(m.group(5)), '', cellName, 'symbol')
        else:
            i.setCell(lib.name(), cellName, 'symbol')
            #i = Instance(self.view, int(m.group(1)), int(m.group(2)), int(m.group(4)), int(m.group(5)), lib.name(), cellName, 'symbol')
        self.last = i
        #self.view.addComponent(c)
        self.view.addElem(i)

    def parseAttribute(self, mAttr):
        m=self.match
        key = m.group(1)
        val = m.group(2)
        if (self.inAttribute):
            a = Attribute(self.last, self._database.layers(), key, val)
            self.last.addAttribute(a)
        else:
            a = Attribute(self.view, self._database.layers(), key, val)
            self.view.addElem(a)
        a.setXY(int(mAttr.group(1)), int(mAttr.group(2)))
        #a.setLayer(None)  #int(mAttr.group(3))
        a.setTextSize(int(mAttr.group(4))*13.888)
        a.setVisible(int(mAttr.group(5)) == 1)
        a.setVisibleKey(int(mAttr.group(6)) != 1)
        #a.setVisibleValue(int(mAttr.group(6)) < 2)
        a.setAngle(int(mAttr.group(7)))
        align = int(mAttr.group(8))/3
        if align == 0:
            a.setHAlign(Attribute.AlignLeft)
        elif align == 1:
            a.setHAlign(Attribute.AlignCenter)
        else:
            a.setHAlign(Attribute.AlignRight)
        align = int(mAttr.group(8))%3
        if align == 0:
            a.setVAlign(Attribute.AlignBottom)
        elif align == 1:
            a.setVAlign(Attribute.AlignCenter)
        else:
            a.setVAlign(Attribute.AlignTop)

    def parseText(self):
        m=self.match
        text = ''
        for n in range(int(m.group(9))):
            text += self.readLine()
        text = self.pnewlineStrip.sub('', text)
        if (self.regExpSearch(self.pattr, text)):
            self.parseAttribute(m)
        else:
            l = Label(self.view, self._database.layers())
            #l = Label(self.view, int(m.group(1)), int(m.group(2)), int(int(m.group(4))*13.888))
            l.setText(text)
            l.setXY(int(m.group(1)), int(m.group(2)))
            #l.setLayer(None)  #int(m.group(3))
            l.setTextSize(int(int(m.group(4))*13.888))
            l.setVisible(int(m.group(5)) == 1)
            l.setAngle(int(m.group(7)))
            align = int(m.group(8))/3
            if align == 0:
                l.setHAlign(Label.AlignLeft)
            elif align == 1:
                l.setHAlign(Label.AlignCenter)
            else:
                l.setHAlign(Label.AlignRight)
            align = int(m.group(8))%3
            if align == 0:
                l.setVAlign(Label.AlignBottom)
            elif align == 1:
                l.setVAlign(Label.AlignCenter)
            else:
                l.setVAlign(Label.AlignTop)
            self.last = l
            self.view.addElem(l)

    def regExpSearch(self, regExp, text):
        self.match = regExp.search(text)
        return self.match

    def parseCommand(self, mode):
        text = self.readLine()
        if self.regExpSearch(self.pline, text):
            self.parseLine()
        elif (mode == 'schematic' and
              self.regExpSearch(self.pcomponent, text)):
            self.parseComponent()
        elif (mode == 'schematic' and
              self.regExpSearch(self.pnet, text)):
            self.parseNet()
        elif (mode == 'symbol' and
              self.regExpSearch(self.ppin, text)):
            self.parsePin()
        elif (self.regExpSearch(self.pbox, text)):
            self.parseBox()
        elif (self.regExpSearch(self.ppath, text)):
            self.parseCustomPath()
        elif (self.regExpSearch(self.pcircle, text)):
            self.parseCircle()
        elif (self.regExpSearch(self.parc, text)):
            self.parseArc()
        elif (self.regExpSearch(self.ptext, text)):
            self.parseText()
        elif (self.regExpSearch(self.pattr_start, text)):
            self.inAttribute = True
        elif (self.regExpSearch(self.pattr_stop, text)):
            self.inAttribute = False
        elif (self.regExpSearch(self.peof, text)):
            self.eof = True
        else:
            self.error = False
            return


    def parseFile(self, fileName, mode):
        self.f = open(fileName, 'r')
        self.error = False
        self.eof = False
        self.last = None
        #first line
        text = self.readLine()
        if (self.regExpSearch(self.pversion, text)):
            self.parseVersion()
        else:
            self.error = True
        #rest of the file
        while (not self.error and not self.eof):
            self.parseCommand(mode)
        self.f.close()
        return self.view
    
    def parseSchematic(self, fileName, cellView):
        self.inSchematic = True
        mode = 'schematic'
        self.view = cellView
        #cellName = self.pschStrip.sub('', fileName)
        #self.cell = self.importer.library.cellByName(cellName)
        #if not self.cell:
        #    self.cell = Cell(cellName)
        #    self.library.addCell(self.cell)
        ##self.view = self.cell.viewByName(fileName)
        #self.view = self.cell.viewByName('schematic')
        #if self.view:
        #    print 'Overwriting cell view: '+self.library.name()+'/'+cellName+'/schematic'
        #    self.cell.removeView(self.view)
        #self.view = self.database.makeSchematic(fileName)
        ##self.view = Schematic('schematic')
        #self.cell.addView(self.view)
        self.view.setUU(self.uu)
        schematic = self.parseFile(fileName, mode)
        schematic.checkNetSegments()
        schematic.checkSolderDots()
        return schematic

    def parseSymbol(self, fileName, cellView):
        self.inSymbol = True
        mode = 'symbol'
        self.view = cellView
        #cellName = self.importer.fileName
        #self.psymStrip.sub('', fileName)
        #self.cell = self.importer.cell
        #self.library.cellByName(cellName)
        #if not self.cell:
        #    self.cell = Cell(cellName)
        #    self.library.addCell(self.cell)
        #self.view = self.cell.viewByName(fileName)
        #self.view = self.cell.viewByName('symbol')
        #if self.view:
        #    return self.view
        #    print 'Overwriting cell view: '+self.library.name()+'/'+cellName+'/symbol'
        #    self.cell.removeView(self.view)
        #self.view = self.database.makeSymbol(fileName)
        ##self.view = Symbol('symbol')
        #self.cell.addView(self.view)
        self.view.setUU(self.uu)
        return self.parseFile(fileName, mode)



class GedaImporter(Importer):
    pstrip = re.compile(r'(\.sch|\.sym)$')
    psymStrip = re.compile(r'\.sym$')
    pschStrip = re.compile(r'\.sch$')
    def __init__(self, database):
        Importer.__init__(self, database)
        self.database = database
        self.componentLibraryList = []
        self.sourceLibraryList = []
        
    def importLibraryList(self, componentList, sourceList):
        self.componentLibraryList = componentList
        self.sourceLibraryList = sourceList
        for l in self.componentLibraryList:
            self.importComponentLibrary(l)
        for l in self.sourceLibraryList:
            self.importSourceLibrary(l)
                
    def findCellSymbolLibrary(self, cellName):
        cell = self.database.viewByName(self.library.name(), cellName, 'symbol')
        if cell:
            return self.library
        else:
            for l in self.database.libraries():
                if not l == self.library:
                    cell = self.database.viewByName(l.name(), cellName, 'symbol')
                    #print l.name, cell
                    if cell:
                        return l
            return None

    def cellName(self, fileName):
        f = os.path.basename(fileName)
        return self.pstrip.sub('', f)
    
    def importComponentLibrary(self, lib):
        library = lib[0]
        directory = lib[1]
        directory = os.path.expanduser(directory)

        if (os.path.exists(directory) and
            os.path.isdir(directory)):
            files = os.listdir(directory)
            files = map(
                lambda f: os.path.join(directory, f),
                files)
            files = filter(
                lambda f: os.path.isfile(f) and self.psymStrip.search(f),
                files)
            for f in files:
                #f = os.path.join(directory, f)
                #print f, os.path.isfile(f) #, self.psymStrip.search(f)
                #if os.path.isfile(f) and self.psymStrip.search(f):
                if (not self.database.viewByName(library, self.cellName(f), 'symbol')):
                    print 'Importing component symbol', f
                    self.library = self.database.libraryByName(library)
                    if not self.library:
                        self.library = Library(library)
                        self.database.addLibrary(self.library)
                    self.cell = self.library.cellByName(self.cellName(f))
                    if not self.cell:
                        self.cell = Cell(self.cellName(f))
                        self.library.addCell(self.cell)
                    cv = self.cell.viewByName('symbol')
                    if not cv:
                        cv = Symbol('symbol')
                        self.cell.addView(cv)
                        r = GedaReader(self)
                        cv = r.parseSymbol(f, cv)
                    #cv = r.parseSymbol(f)
                    #self.cell.addView(cv)
                else:
                    print 'Skipping component symbol', f

    def importSourceLibrary(self, lib):
        library = lib[0]
        directory = lib[1]
        directory = os.path.expanduser(directory)
        
        if (os.path.exists(directory) and
            os.path.isdir(directory)):
            files = os.listdir(directory)
            files = map(
                lambda f: os.path.join(directory, f),
                files)
            files = filter(
                lambda f: os.path.isfile(f) and self.pschStrip.search(f),
                files)
            for f in files:
                #f = os.path.join(directory, f)
                if (not self.database.viewByName(library, self.cellName(f), 'schematic')):
                    print 'Importing component schematic', f
                    self.library = self.database.libraryByName(library)
                    if not self.library:
                        self.library = Library(library)
                        self.database.addLibrary(self.library)
                    self.cell = self.library.cellByName(self.cellName(f))
                    if not self.cell:
                        self.cell = Cell(self.cellName(f))
                        self.library.addCell(self.cell)
                    cv = self.cell.viewByName('schematic')
                    if not cv:
                        cv = Schematic('schematic')
                        self.cell.addView(cv)
                        r = GedaReader(self)
                        r.parseSchematic(f, cv)
                    #self.cell.addView(cv)
                else:
                    print 'Skipping component schematic', f


