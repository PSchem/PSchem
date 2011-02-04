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

class Index():
    def __init__(self):
        #following indices store sets of objects
        self._instancesAtCoord = {}
        self._netsAtCoord = {}
        self._netsAtXCoord = {}
        self._netsAtYCoord = {}
        self._solderDotsAtCoord = {}
        #following indices store pairs of x, y coordinates
        self._coordsOfInstance = {}
        self._coordsOfNet = {}
        self._coordsOfSolderDot = {}
    
    def netSegmentAdded(self, netSegment):
        #print self.__class__.__name__, "ns added", netSegment
        p1 = netSegment.x(), netSegment.y()
        p2 = netSegment.x2(), netSegment.y2()
        if p1 in self._netsAtCoord:
            self._netsAtCoord[p1].add(netSegment)
        else:
            self._netsAtCoord[p1] = set([netSegment])
        if p2 in self._netsAtCoord:
            self._netsAtCoord[p2].add(netSegment)
        else:
            self._netsAtCoord[p2] = set([netSegment])
        if netSegment.isVertical(): #p1[0] == p2[0]:
            if p1[0] in self._netsAtXCoord:
                self._netsAtXCoord[p1[0]].add(netSegment)
            else:
                self._netsAtXCoord[p1[0]] = set([netSegment])
        if netSegment.isHorizontal(): #p1[1] == p2[1]:
            if p1[1] in self._netsAtYCoord:
                self._netsAtYCoord[p1[1]].add(netSegment)
            else:
                self._netsAtYCoord[p1[1]] = set([netSegment])
        self._coordsOfNet[netSegment] = p1, p2
        
    def netSegmentRemoved(self, netSegment):
        #print self.__class__.__name__, "ns removed", netSegment
        if netSegment in self._coordsOfNet:
            p1, p2 = self._coordsOfNet[netSegment]
            del self._coordsOfNet[netSegment]
            self._netsAtCoord[p1].remove(netSegment)
            if len(self._netsAtCoord[p1]) == 0:
                del self._netsAtCoord[p1]
            self._netsAtCoord[p2].remove(netSegment)
            if len(self._netsAtCoord[p2]) == 0:
                del self._netsAtCoord[p2]
            if netSegment.isVertical():
                self._netsAtXCoord[p1[0]].remove(netSegment)
                if len(self._netsAtXCoord[p1[0]]) == 0:
                    del self._netsAtXCoord[p1[0]]
            if netSegment.isHorizontal():
                self._netsAtYCoord[p1[1]].remove(netSegment)
                if len(self._netsAtYCoord[p1[1]]) == 0:
                    del self._netsAtYCoord[p1[1]]
    
    def solderDotAdded(self, solderDot):
        p = solderDot.x(), solderDot.y()
        if p in self._solderDotsAtCoord:
            self._solderDotsAtCoord[p].add(solderDot) # multiple solder dots at same location?
        else:
            self._solderDotsAtCoord[p] = set([solderDot])
            
    def solderDotRemoved(self, solderDot):
        if solderDot in self._coordsOfSolderDot:
            del self._coordsOfSolderDot[solderDot]
    
    def netSegmentsAt(self, x, y):
        return self.netSegmentsEndPointsAt(x, y) | self.netSegmentsMidPointsAt(x, y)

    def netSegmentsEndPointsAt(self, x, y):
        s = set()
        if (x, y) in self._netsAtCoord:
            s |= self._netsAtCoord[(x, y)]
        return s

    def netSegmentsMidPointsAt(self, x, y):
        s = set()
        if x in self._netsAtXCoord:
            s2 = self._netsAtXCoord[x]
            for netSegment in s2:
                p1, p2 = self._coordsOfNet[netSegment]
                if (p1[1] < y < p2[1]) or (p1[1] > y > p2[1]):
                    s.add(netSegment)
        if y in self._netsAtYCoord:
            s2 = self._netsAtYCoord[y]
            for netSegment in s2:
                p1, p2 = self._coordsOfNet[netSegment]
                if (p1[0] < x < p2[0]) or (p1[0] > x > p2[0]):
                    s.add(netSegment)
        return s

    def coordsOfNetSegments(self):
        return self._coordsOfNet #a dict, net->pair coords
        
    def netSegmentsEndPoints(self):
        return self._netsAtCoord.keys() #a list

    def solderDotsAt(self, x, y):
        s = set()
        if (x, y) in self._solderDotsAtCoord:
            s |= self._solderDotsAtCoord[(x, y)]
        return s

