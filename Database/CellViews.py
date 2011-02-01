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

#print 'CellViews in'

from Database.Primitives import *
#from Database.Design import *
from xml.etree import ElementTree as et

#print 'CellViews out'

class CellView():
    def __init__(self, name, cell):
        self._name = name
        self._attribs = {}
        self._cell = cell
        cell.cellViewAdded(self)
            
    def name(self):
        return self._name

    def cell(self):
        return self._cell

    def attributes(self):
        return self._attribs

    def library(self):
        return self.cell().library()
        
    def database(self):
        return self.cell().database()
        
    def save(self):
        pass
        
    def restore(self):
        pass

    def remove(self):
        for a in list(self.attributes()):
            a.remove()
        self.cell().cellViewRemoved(self)

class Diagram(CellView):
    def __init__(self, name, cell):
        CellView.__init__(self, name, cell)
        #self._elems = set()
        self._items = set()
        self._lines = set()
        self._rects = set()
        self._customPaths = set()
        self._ellipses = set()
        self._ellipseArcs = set()
        self._labels = set()
        self._attributeLabels = set()
        #self._uu = 160 # default DB units per user units
        self._attribs['uu'] = 160 # default DB units per user units
        #self._name = 'diagram'
        self._designUnits = set()

    def instanceItemAdded(self, view):
        self._items.add(view)
        for elem in self.elems():
            elem.addToView(view)
            
    def instanceItemRemoved(self, view):
        self._items.remove(view)
        for elem in self.elems():
            elem.removeFromView(view)
            
    def designUnitAdded(self, designUnit):
        self._designUnits.add(designUnit)
        scene = designUnit.scene()
        for e in self.elems():
            e.addToView(scene)

    def designUnitRemoved(self, designUnit):
        self._designUnits.remove(designUnit)

    #def updateDesignUnits(self):
    #    for d in self._designUnits:
    #        d.updateDesignUnit()
    #        #v.updateItem()

    def setUU(self, uu):
        self._attribs['uu'] = uu

    def items(self):
        return self._items
        
    def elems(self):
        return self.lines() | self.rects() | self.labels() | \
            self.attributeLabels() | self.customPaths() | \
            self.ellipses() | self.ellipseArcs()
            
    def elementAdded(self, elem):
        for designUnit in self._designUnits:
            elem.addToDesignUnit(designUnit)

    def elementRemoved(self, elem):
        for designUnit in self._designUnits:
            elem.removeFromDesignUnit(designUnit)
        
    def addElem(self, elem):
        "main entry point for adding new elements to diagram"
        #self._elems.add(elem)
        elem.addToDiagram(self)
        for designUnit in self._designUnits:
            elem.addToDesignUnit(designUnit)

    def removeElem(self, elem):
        "main entry point for removing elements from diagram"
        for designUnit in self._designUnits:
            elem.removeFromDesignUnit(designUnit)
        elem.removeFromDiagram(self)

    def lineAdded(self, line):
        self._lines.add(line)
        
    def lineRemoved(self, line):
        self._lines.remove(line)
        
    def lines(self):
        return self._lines

    def rectAdded(self, rect):
        self._rects.add(rect)
        
    def rectRemoved(self, rect):
        self._rects.remove(rect)
        
    def rects(self):
        return self._rects

    def customPathAdded(self, customPath):
        self._customPaths.add(customPath)
        
    def customPathRemoved(self, customPath):
        self._customPaths.remove(customPath)
        
    def customPaths(self):
        return self._customPaths

    def ellipseAdded(self, ellipse):
        self._ellipses.add(ellipse)
        
    def ellipseRemoved(self, ellipse):
        self._ellipses.remove(ellipse)
        
    def ellipses(self):
        return self._ellipses

    def ellipseArcAdded(self, ellipseArc):
        self._ellipseArcs.add(ellipseArc)
        
    def ellipseArcRemoved(self, ellipseArc):
        self._ellipseArcs.remove(ellipseArc)
        
    def ellipseArcs(self):
        return self._ellipseArcs

    def labelAdded(self, label):
        self._labels.add(label)
        
    def labelRemoved(self, label):
        self._labels.remove(label)
        
    def labels(self):
        return self._labels

    def attributeLabelAdded(self, attributeLabel):
        self._attributeLabels.add(attributeLabel)
        
    def attributeLabelRemoved(self, attributeLabel):
        self._attributeLabels.remove(attributeLabel)
        
    def attributeLabels(self):
        return self._attributeLabels

    def uu(self):
        return self._attribs['uu']

    def remove(self):
        for e in list(self.elems()):
            e.remove()
            #self.removeElem(e)
        for du in list(self.designUnits()):
            du.remove()
            #self.removeDesignUnit(o)
        CellView.remove(self)

    def save(self):
        root = et.Element(self._name)
        tree = et.ElementTree(root)
        for a in sorted(self.attribs()):
            root.attrib[str(a)] = str(self.attribs()[a])
        for e in sorted(self.elems(), key=Element.name):
            xElem = e.toXml()
            root.append(xElem)
        self._indentET(tree.getroot())
        et.dump(tree)
        #return tree
        
    def restore(self):
        pass
    
    def _indentET(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indentET(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
class Schematic(Diagram):
    def __init__(self, name, cell):
        Diagram.__init__(self, name, cell)
        #self._name = 'schematic'
        self._pins = set()
        self._instances = set()
        self._netSegments = set()
        self._solderDots = set()
        self._nets = set()

    def designUnitAdded(self, designUnit):
        self._designUnits.add(designUnit)
        scene = designUnit.scene()
        #for e in self.elems()-self.instances():
        for e in self.elems():
            e.addToView(scene)
        #for i in self.instances():
        #    i.addToView(designUnit)

    #def components(self):
    #    components = map(lambda i: i.cell(), self.instances())
    #    return components.sort()

    def elems(self):
        return Diagram.elems(self) | self.pins() | self.instances() | self.netSegments() | self.solderDots()

    def pinAdded(self, pin):
        self._pins.add(pin)
       
    def pinRemoved(self, pin):
        self._pins.remove(pin)
        
    def pins(self):
        return self._pins

    def instanceAdded(self, instance):
        self._instances.add(instance)
        
    def instanceRemoved(self, instance):
        self._instances.remove(instance)
        
    def instances(self):
        return self._instances

    #def addNet(self, net):
    #    "call only from addToDiagram"
    #    self._nets.add(net)
        
    #def removeNet(self, net):
    #    "call only from removeFromDiagram"
    #    self._nets.remove(net)
        
    #def nets(self):
    #    return self._nets #filter(lambda e: isinstance(e, CNet), self.elems())

    def netSegmentAdded(self, netSegment):
        self._netSegments.add(netSegment)
        
    def netSegmentRemoved(self, netSegment):
        self._netSegments.remove(netSegment)
        
    def netSegments(self):
        return self._netSegments

    def solderDotAdded(self, solderDot):
        self._solderDots.add(solderDot)
        
    def solderDotRemoved(self, solderDot):
        self._solderDots.remove(solderDot)
        
    def solderDots(self):
        return self._solderDots

    def checkNetSegments(self, segments = None):
        if not segments:
            segments = self.netSegments()
        origNetSegments = segments
        for n in list(origNetSegments):
            splitPoints = set()
            for n2 in origNetSegments:
                if n.containsInside(n2.x1(), n2.y1()):
                    splitPoints.add((n2.x1(), n2.y1()))
                    #print n.x1(), n.y1()
                if n.containsInside(n2.x2(), n2.y2()):
                    splitPoints.add((n2.x2(), n2.y2()))
                    #print n.x2(), n.y2()
            if splitPoints:
                splitPoints.add((n.x1(), n.y1()))
                splitPoints.add((n.x2(), n.y2()))
                pointList = list(splitPoints)
                if (n.x1() != n.x2()):
                    pointList.sort(lambda p1, p2: cmp(p1[0], p2[0]))
                else:
                    pointList.sort(lambda p1, p2: cmp(p1[1], p2[1]))
                prevPoint = pointList[0]
                for p in pointList[1:]:
                    newSegment = NetSegment(n.diagram(), n.layers(), prevPoint[0], prevPoint[1], p[0], p[1])
                    #self.addElem(newSegment)
                    #print prevPoint[0], p[0], prevPoint[1], p[1]
                    prevPoint = p
                n.remove() #self.removeElem(n)

    def checkSolderDots(self, segments = None):
        if not segments:
            segments = self.netSegments()
        origNetSegments = segments
        origSolderDots = self.solderDots()
        for n in origNetSegments:
            count1 = -1
            count2 = -1
            solder1 = filter(lambda sd: sd.x() == n.x1() and sd.y() == n.x2, origSolderDots)
            solder2 = filter(lambda sd: sd.x() == n.x1() and sd.y() == n.x2, origSolderDots)
            for n2 in origNetSegments:
                if ((n.x1() == n2.x1() and n.y1() == n2.y1()) or
                    (n.x1() == n2.x2() and n.y1() == n2.y2())):
                    count1 += 1
                if ((n.x2() == n2.x1() and n.y2() == n2.y1()) or
                    (n.x2() == n2.x2() and n.y2() == n2.y2())):
                    count2 += 1
            if count1 > 1:
                if not solder1:
                    solder = SolderDot(n.diagram(), n.layers(), n.x1(), n.y1())
                    #self.addElem(solder)
            elif solder1:
                    solder1.remove()
                    #self.removeElem(solder1)
            if count2 > 1:
                if not solder2:
                    solder = SolderDot(n.diagram(), n.layers(), n.x2(), n.y2())
                    #self.addElem(solder)
            elif solder2:
                    solder2.remove()
                    #self.removeElem(solder2)
                
class Symbol(Diagram):
    def __init__(self, name, cell):
        Diagram.__init__(self, name, cell)
        #self._name = 'symbol'
        self._symbolPins = set()

    def designUnitAdded(self, designUnit):
        self._designUnits.add(designUnit)
        scene = designUnit.scene()
        for e in self.elems():
            e.addToView(scene)

    def elems(self):
        return Diagram.elems(self) | self.symbolPins()
        
    def symbolPinAdded(self, symbolPin):
        self._symbolPins.add(symbolPin)
       
    def symbolPinRemoved(self, symbolPin):
        self._symbolPins.remove(symbolPin)
        
    def symbolPins(self):
        return self._symbolPins

class Netlist(CellView):
    def __init__(self, name, cell):
        CellView.__init__(self, name, cell)
        #self._name = 'netlist'

