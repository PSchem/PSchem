﻿# -*- coding: utf-8 -*-

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

from Index import Index
from Primitives import *
#from Design import *
from xml.etree import ElementTree as et

#print 'CellViews out'

class CellView():
    def __init__(self, name, cell):
        self._name = name
        self._attribs = {}
        self._cell = cell
        cell.cellViewAdded(self)
            
    @property
    def name(self):
        return self._name
        
    @property
    def path(self):
        return self.cell.path + '/' + self.name

    @property
    def cell(self):
        return self._cell

    @property
    def attributes(self):
        return self._attribs

    @property
    def library(self):
        return self.cell.library
        
    @property
    def database(self):
        return self.cell.database
        
    def save(self):
        pass
        
    def restore(self):
        pass

    def remove(self):
        #for a in list(self.attributes):
        #    a.remove()
        self.cell.cellViewRemoved(self)
        self.cell = None

    def __repr__(self):
        return "<CellView '" + self.path + "'>"


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

    @property
    def designUnits(self):
        return self._designUnits

    @property
    def items(self):
        return self._items
        
    @property
    def elems(self):
        return self.lines | self.rects | self.labels | \
            self.attributeLabels | self.customPaths | \
            self.ellipses | self.ellipseArcs
            
    @property
    def lines(self):
        return self._lines

    @property
    def rects(self):
        return self._rects

    @property
    def customPaths(self):
        return self._customPaths

    @property
    def ellipses(self):
        return self._ellipses

    @property
    def ellipseArcs(self):
        return self._ellipseArcs

    @property
    def labels(self):
        return self._labels

    @property
    def attributeLabels(self):
        return self._attributeLabels

    @property
    def uu(self):
        return self._attribs['uu']

    @uu.setter
    def uu(self, uu):
        self._attribs['uu'] = uu

    def instanceItemAdded(self, view):
        self.items.add(view)
        for elem in self.elems:
            elem.addToView(view)
        #for designUnit in self._designUnits:
        #    elem.addToDesignUnit(designUnit)
            
    def instanceItemRemoved(self, view):
        self.items.remove(view)
        for elem in self.elems:
            elem.removeFromView()
            
    def designUnitAdded(self, designUnit):
        self.designUnits.add(designUnit)
        scene = designUnit.scene()
        for e in self.elems:
            e.addToView(scene)

    def designUnitRemoved(self, designUnit):
        self.designUnits.remove(designUnit)
        
    #def updateDesignUnits(self):
    #    for d in self._designUnits:
    #        d.updateDesignUnit()
    #        #v.updateItem()

    def elementAdded(self, elem):
        pass
        #for designUnit in self._designUnits:
        #    elem.addToDesignUnit(designUnit)

    def elementChanged(self, elem):
        pass
        #for designUnit in self._designUnits:
        #    elem.addToDesignUnit(designUnit)

    def elementRemoved(self, elem):
        pass
        #for designUnit in self._designUnits:
        #    elem.removeFromDesignUnit(designUnit)
        
    #def addElem(self, elem):
    #    "main entry point for adding new elements to diagram"
    #    #self._elems.add(elem)
    #    elem.addToDiagram(self)
    #    for designUnit in self._designUnits:
    #        elem.addToDesignUnit(designUnit)

    #def removeElem(self, elem):
    #    "main entry point for removing elements from diagram"
    #    for designUnit in self._designUnits:
    #        elem.removeFromDesignUnit(designUnit)
    #    elem.removeFromDiagram(self)

    def lineAdded(self, line):
        self.lines.add(line)
        
    def lineRemoved(self, line):
        self.lines.remove(line)
        
    def rectAdded(self, rect):
        self.rects.add(rect)
        
    def rectRemoved(self, rect):
        self.rects.remove(rect)
        
    def customPathAdded(self, customPath):
        self.customPaths.add(customPath)
        
    def customPathRemoved(self, customPath):
        self.customPaths.remove(customPath)
        
    def ellipseAdded(self, ellipse):
        self.ellipses.add(ellipse)
        
    def ellipseRemoved(self, ellipse):
        self.ellipses.remove(ellipse)
        
    def ellipseArcAdded(self, ellipseArc):
        self.ellipseArcs.add(ellipseArc)
        
    def ellipseArcRemoved(self, ellipseArc):
        self.ellipseArcs.remove(ellipseArc)
        
    def labelAdded(self, label):
        self.labels.add(label)
        
    def labelRemoved(self, label):
        self.labels.remove(label)
        
    def attributeLabelAdded(self, attributeLabel):
        self.attributeLabels.add(attributeLabel)
        
    def attributeLabelRemoved(self, attributeLabel):
        self.attributeLabels.remove(attributeLabel)
        
    def remove(self):
        for e in list(self.elems):
            e.remove()
            #self.removeElem(e)
        for du in list(self.designUnits):
            du.remove()
            #self.removeDesignUnit(o)
        CellView.remove(self)

    def save(self):
        root = et.Element(self.name)
        tree = et.ElementTree(root)
        for a in sorted(self.attributes):
            root.attrib[str(a)] = str(self.attributes[a])
        for e in sorted(self.elems, key=Element.name):
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

    def __repr__(self):
        return "<Diagram '" + self.path + "'>"

                
class Schematic(Diagram):
    def __init__(self, name, cell):
        Diagram.__init__(self, name, cell)
        #self._name = 'schematic'
        self._pins = set()
        self._instances = set()
        self._netSegments = set()
        self._solderDots = set()
        self._nets = set()
        self._index = Index()
        
        #self._netSegmentsAdded = set()
        #self._netSegmentsRemoved = set()
        
    def designUnitAdded(self, designUnit):
        self.designUnits.add(designUnit)
        #scene = designUnit.scene
        #for e in self.elems-self.instances:
        #for e in self.elems:
        #    e.addToView(scene)
        #for i in self.instances():
        #    i.addToView(designUnit)
        #for ns in self.netSegments():
        #    ns.addToDesignUnit(designUnit)
        #designUnit.checkNets()

    #def components(self):
    #    components = map(lambda i: i.cell(), self.instances())
    #    return components.sort()

    @property
    def elems(self):
        return self.lines | self.rects | self.labels | \
            self.attributeLabels | self.customPaths | \
            self.ellipses | self.ellipseArcs | \
            self.pins | self.instances | self.netSegments | self.solderDots

    @property
    def pins(self):
        return self._pins

    @property
    def instances(self):
        return self._instances

    @property
    def netSegments(self):
        self.database.runDeferredProcesses(self)
        return self._netSegments

    @property
    def solderDots(self):
        self.database.runDeferredProcesses(self)
        return self._solderDots

    @property
    def index(self):
        return self._index

    def pinAdded(self, pin):
        self.pins.add(pin)
       
    def pinRemoved(self, pin):
        self.pins.remove(pin)
        
    def instanceAdded(self, instance):
        self.instances.add(instance)
        
    def instanceRemoved(self, instance):
        self.instances.remove(instance)
        
    #def addNet(self, net):
    #    "call only from addToDiagram"
    #    self.nets.add(net)
        
    #def removeNet(self, net):
    #    "call only from removeFromDiagram"
    #    self.nets.remove(net)
        
    #@property
    #def nets(self):
    #    return self._nets #filter(lambda e: isinstance(e, CNet), self.elems)

    def netSegmentAdded(self, netSegment):
        #print self.__class__.__name__, "ns added", netSegment
        self.index.netSegmentAdded(netSegment)
        self._netSegments.add(netSegment) #don't trigger deferred processing
        #self._netSegmentsAdded.add(netSegment)
        self.database.requestDeferredProcessing(self)
        #self.splitNetSegment(netSegment)
        #for designUnit in self._designUnits:
        #    netSegment.addToDesignUnit(designUnit)
        #    if designUnit.scene():
        #        netSegment.addToView(designUnit.scene())
        
    def netSegmentRemoved(self, netSegment):
        #print self.__class__.__name__, "ns removed", netSegment
        self.index.netSegmentRemoved(netSegment)
        self._netSegments.remove(netSegment) #don't trigger deferred processing
        #self._netSegmentsRemoved.add(netSegment)
        self.database.requestDeferredProcessing(self)
        
    def solderDotAdded(self, solderDot):
        self.index.solderDotAdded(solderDot)
        #for designUnit in self._designUnits:
        #    #solderDot.addToDesignUnit(designUnit)
        #    if designUnit.scene():
        #        solderDot.addToView(designUnit.scene())
        self._solderDots.add(solderDot) #don't trigger deferred processing
        
    def solderDotRemoved(self, solderDot):
        self.index.solderDotRemoved(solderDot)
        self._solderDots.remove(solderDot) #don't trigger deferred processing
        
    def splitNetSegment(self, netSegment):
        """
        Check if (newly added) netSegment should be split or if it requires
        other net segments to split.
        """
        idx = self.index
        (p1, p2) = idx.coordsOfNetSegments[netSegment]
        n = 0
        #first split other segments
        for p in (p1, p2):
            segments = idx.netSegmentsMidPointsAt(p[0], p[1])
            for s in list(segments):
                if s in idx.coordsOfNetSegments:
                    #print "split ", s, p, idx.coordsOfNetSegments()[s]
                    s.splitAt(p)
                    n += 1
        #then, if necessary, split the netSegment
        for p in list(idx.netSegmentsEndPoints):
            if netSegment in idx.netSegmentsMidPointsAt(p[0], p[1]):
                #print "split ", netSegment, p
                netSegment.splitAt(p)
                n += 1
                break
        #print self.__class__.__name__, "split", n, "segments"

    def splitNetSegments(self):
        """
        Go through all net segments in the design unit and make sure that
        none of them crosses an end point (of a segment), an instance pin
        or a port.
        """
        idx = self.index
        n = 0
        for p in list(idx.netSegmentsEndPoints):
            segments = idx.netSegmentsMidPointsAt(p[0], p[1])
            for s in list(segments):
                if s in idx.coordsOfNetSegments:
                    #print "split ", s, p
                    s.splitAt(p)
                    n += 1
        #print self.__class__.__name__, "split", n, "segments"
        
    def mergeNetSegments(self):
        """
        Go through all net segments in the design unit and make sure that
        there are no two or more segments being just a continuation of each other.
        """
        idx = self.index
        n = 0
        for p in list(idx.netSegmentsEndPoints):
            segments = list(idx.netSegmentsEndPointsAt(p[0], p[1]))
            if len(segments) > 1:
                if all(s.isHorizontal for s in segments) or \
                    all(s.isVertical for s in segments) or \
                    all(s.isDiagonal45 for s in segments) or \
                    all(s.isDiagonal135 for s in segments):
                        n += len(segments)
                        segments[0].mergeSegments(segments)
        #print self.__class__.__name__, "merged", n, "segments"
        
    def checkSolderDots(self):
        """
        Goes through all endpoints and counts the number of segments connected there.
        If it larger than 2 check if a solder dot exists
        and if not, add it.
        """
        idx = self.index
        n = 0
        for p in list(idx.netSegmentsEndPoints):
            segments = idx.netSegmentsEndPointsAt(p[0], p[1])
            if len(segments) > 2:
                if len(idx.solderDotsAt(p[0], p[1])) == 0:
                    SolderDot(self, self.database.layers, p[0], p[1])
                    n += 1
        #print self.__class__.__name__, "added", n, "solder dots"
            
    def checkNets(self):
        self.splitNetSegments()
        self.mergeNetSegments()
        self.checkSolderDots()

    def runDeferredProcess(self):
        """
        Runs deferred processes of the Schematic class.
        Do not call it directly, Use Database.runDeferredProcesses(object)
        """
        self.checkNets()
        
    def __repr__(self):
        return "<Schematic '" + self.path + "'>"

class Symbol(Diagram):
    def __init__(self, name, cell):
        Diagram.__init__(self, name, cell)
        #self._name = 'symbol'
        self._symbolPins = set()

    def designUnitAdded(self, designUnit):
        self.designUnits.add(designUnit)
        #scene = designUnit.scene
        #for e in self.elems:
        #    e.addToView(scene)

    @property
    def elems(self):
        return self.lines | self.rects | self.labels | \
            self.attributeLabels | self.customPaths | \
            self.ellipses | self.ellipseArcs | \
            self.symbolPins
        
    @property
    def symbolPins(self):
        return self._symbolPins

    def symbolPinAdded(self, symbolPin):
        self.symbolPins.add(symbolPin)
       
    def symbolPinRemoved(self, symbolPin):
        self.symbolPins.remove(symbolPin)
        
    def __repr__(self):
        return "<Symbol '" + self.path + "'>"

class Netlist(CellView):
    def __init__(self, name, cell):
        CellView.__init__(self, name, cell)
        #self._name = 'netlist'

    def __repr__(self):
        return "<Netlist '" + self.path + "'>"

