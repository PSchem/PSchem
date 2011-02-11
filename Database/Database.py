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

#print 'Database in'

from Cells import *
from Design import *

#print 'Database out'

class Database():
    theDatabase = None

    @classmethod
    def createDatabase(cls, client):
        """Construct a Database object, or return an existing one."""
        if Database.theDatabase:
            self = Database.theDatabase
            #self._client = client
        else:
            self = cls()
            Database.theDatabase = self
            self._client = client
            self._libraries = Libraries.createLibraries(self)
            self._layers = None
            self._designs = Designs(self)
            self._deferredProcessingObjects = set()
        return self
    
    @property
    def client(self):
        return self._client
        
    @property
    def libraries(self):
        return self._libraries
        
    @property
    def layers(self):
        return self._layers
        
    @layers.setter
    def layers(self, layers):
        self._layers = layers
        #self.updateViews()

    @property
    def designs(self):
        return self._designs

    def wasDeferredProcessingRequested(self, object=None):
        if object:
            return object in self._deferredProcessingObjects
        else:
            return len(self._deferredProcessingObjects) > 0
        
    def requestDeferredProcessing(self, object):
        """
        Request deferred processing of object's notifications.
        Once per object. No priorities or order guarantees.
        """
        self._deferredProcessingObjects.add(object)
        ##print self.__class__.__name__, "request", object
        self.client.deferredProcessingRequested()
        self.leaveCPU()
            
    def cancelDeferredProcessing(self, object):
        """
        Cancel deferred processing of a given object.
        For example, if it has already been triggered manually.
        """
        self._deferredProcessingObjects.remove(object)
        
    def runDeferredProcesses(self, object = None):
        """
        Force execution of all deferred processes.
        To be called synchronously or from within the main loop
        (an "idle" function).
        """
        if object:
            while self.wasDeferredProcessingRequested(object):
                self.cancelDeferredProcessing(object)
                o.runDeferredProcess()
        else:
            while self.wasDeferredProcessingRequested(object):
                dpos = list(self._deferredProcessingObjects)
                self._deferredProcessingObjects = set()
                for o in dpos:
                    ##print self.__class__.__name__, "run", o
                    o.runDeferredProcess()
            
    def leaveCPU(self):
        self.client.leaveCPU()

    def close(self):
        self.runDeferredProcesses()
        self.designs.close()
        self.libraries.close()
        Database.theDatabase = None
        