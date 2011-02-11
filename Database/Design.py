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

#print 'Design in'

#from Primitives import *
#from Cells import *
#from Attributes import *
from xml.etree import ElementTree as et

#print 'Design out'

class DesignUnit():
    def __init__(self, instance, parentDesignUnit):
        self._instance = instance
        self._parentDesignUnit = parentDesignUnit
        self._childDesignUnits = {} #set()
        self._design = parentDesignUnit.design
        self._scene = None
        #self._index = Index()
        self.cellView.designUnitAdded(self)
        parentDesignUnit.childDesignUnitAdded(self)
 
    @property
    def childDesignUnits(self):
        """
        Get a dictionary of child design units (instance->designUnit)
        The dictionary is computed lazily by this function
        (so that it descends down the hierarchy only when the user wants to see it)
        and is cached for future invocations.
        """
        if len(self._childDesignUnits) > 0:   #cache
            return self._childDesignUnits
        schematic = self.cellView.cell.cellViewByName("schematic")
        
        if schematic:
            for i in schematic.instances:
                DesignUnit(i, self) # it should add itself to parent design unit
                #self._childDesignUnits[i] = DesignUnit(i, self)
        return self._childDesignUnits

    @property
    def parentDesignUnit(self):
        return self._parentDesignUnit

    @property
    def scene(self):
        return self._scene
    
    @property
    def instance(self):
        return self._instance

    @property
    def design(self):
        return self._design

    @property
    def cellView(self):
        return self.instance.instanceCell.implementation
        #schematic = self.instance.instanceCell.cellViewByName('schematic')
        #if schematic:
        #    return schematic
        #else:
        #    return self.instance.instanceCellView

    def sceneAdded(self, scene):
        self._scene = scene
        for e in self.cellView.elems:
            e.addToView(scene)
        
    def childDesignUnitAdded(self, designUnit):
        self._childDesignUnits[designUnit.instance] = designUnit
        
    def childDesignUnitRemoved(self, designUnit):
        del self._childDesignUnits[designUnit.instance]

    def updateItem(self):
        if self.scene:
            self.scene.updateItem()

    def addInstance(self, instance):
        #designUnit = self._childDesignUnits.get(instance)
        #if not designUnit:
        designUnit = DesignUnit(instance, self)
        self.childDesignUnits[instance] = designUnit
        self.scene.addInstance(designUnit)
    
    def removeInstance(self, instance):
        designUnit = self._childDesignUnits.get(instance)
        if designUnit:
            self.scene.removeInstance(designUnit)
            del self.childDesignUnits[instance]
    
    def remove(self):
        for co in self.childDesignUnits.values():
            co.remove()
        if self.scene:
            self.scene.instanceRemoved()
            self.cellView.DesignUnitRemoved(self)
        self.parentDesignUnit.childDesignUnitRemoved(self)
        
class Design(DesignUnit):
    def __init__(self, cellView, designs):
        self._cellView = cellView
        self._designs = designs
        self._childDesignUnits = {}
        self._scene = None
        self.cellView.designUnitAdded(self)
        designs.designAdded(self)
            
    @property
    def cellView(self):
        return self._cellView

    @property
    def design(self):
        return self

    @property
    def parentDesignUnit(self):
        return None
    
    @property
    def designs(self):
        return self._designs
        
    def sceneAdded(self, scene):
        self._scene = scene
        for e in self.cellView.elems:
            e.addToView(scene)
            
    def sceneRemoved(self):
        self._scene = None
        self.cellView.designUnitRemoved(self)

    def cellViewRemoved(self):
        if self.scene:
            self.scene.designRemoved()
            
    def remove(self):
        for co in self.childDesignUnits.values():
            co.remove()
        if self.scene:
            self.scene.designRemoved()
        self.cellView.designUnitRemoved(self)
        self.designs.designRemoved(self)

class Designs():
    def __init__(self, database):
        self._database = database
        self._designs = set()
        self._hierarchyViews = set()
       
    @property
    def designs(self):
        return self._designs
        
    @property
    def database(self):
        return self._database
        
    @property
    def hierarchyViews(self):
        return self._hierarchyViews

    def installUpdateHierarchyViewsHook(self, view):
        self.hierarchyViews.add(view)

    def updateHierarchyViews(self):
        "Notify views that the design hierarchy layout has changed"
        for v in self.hierarchyViews:
            v.update()

    def designAdded(self, design):
        #self.add(design)
        self.designs.add(design)
        #self.updateHierarchyViews()
        self.database.requestDeferredProcessing(self)

    def designRemoved(self, design):
        #self.remove(design)
        self.designs.remove(design)
        #self.updateHierarchyViews()
        self.database.requestDeferredProcessing(self)
        
    def runDeferredProcess(self):
        """Runs deferred processes."""
        self.updateHierarchyViews()
        
    def close(self):
        for d in list(self.designs):
            d.remove()
        
