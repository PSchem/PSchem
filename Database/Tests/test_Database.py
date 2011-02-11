import unittest

from Database import Database
from Database.Cells import *
from Database.Design import *

class Client():
    def __init__(self):
        self.timer = False
        self.database = Database.createDatabase(self)
        
    def deferredProcessingRequested(self):
        self.timer = True
        
    def leaveCPU(self):
        pass
    
    def wakeUp(self): #call it manually after test procedure to simulate a "timer" event
        if self.timer:
            self.timer = False
            self.database.runDeferredProcesses()
            
class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.database = self.client.database
        
    def tearDown(self):
        self.database.close()
        self.client.database = None
        self.client = None
        self.database = None
        
    def test_01_create(self):
        self.assertEqual(self.database.__class__.__name__, 'Database')
        self.assertEqual(self.database.libraries.__class__.__name__, 'Libraries')
        self.assertEqual(self.database.designs.__class__.__name__, 'Designs')
        d2 = Database.createDatabase(self.client)
        self.assertEqual(self.database, d2)
        l2 = Libraries.createLibraries(self.database)
        self.assertEqual(self.database.libraries, l2)
        
        #d2 = Designs(self.database)
        #self.assertEqual(self.database.designs, d2)
        
    def test_02_addingSomeLibraries(self):
        root = self.database.libraries
        #referring
        p = Path.createFromPathName('a.b.c.d')
        l = root.libraryByPath(p)
        self.assertEqual(l, None)
        self.assertEqual(root.libraries, set())
        #adding
        l = root.libraryByPath(p, True)
        self.assertEqual(len(root.libraries), 1)
        self.assertEqual(l.__class__.__name__, 'Library')
        self.assertEqual(l.name, 'd')
        self.assertEqual(l.parentLibrary.name, 'c')
        self.assertEqual(l.parentLibrary.parentLibrary.name, 'b')
        self.assertEqual(l.parentLibrary.parentLibrary.parentLibrary.name, 'a')
        self.assertEqual(l.parentLibrary.parentLibrary.parentLibrary.parentLibrary, None)
        self.assertEqual(l.root, root)
        #removing leaf
        lp = l.parentLibrary
        self.assertEqual(len(lp.libraries), 1)
        l.remove()
        self.assertEqual(len(lp.libraries), 0)
        #readding
        self.assertEqual(l.parentLibrary, None)
        l = root.libraryByPath(p, True)
        self.assertEqual(l.parentLibrary, lp)
        
    def test_03_addingSomeLibraries2(self):
        root = self.database.libraries
        #referring
        p = Path.createFromPathName('a.b.c.d')
        o = root.libraryByPath(p)
        self.assertEqual(o, None)
        self.assertEqual(root.libraries, set())
        #adding
        l = root.createLibraryFromPath(p)
        self.assertEqual(l.__class__.__name__, 'Library')
        c = root.createCellFromPath(p)
        self.assertEqual(c.__class__.__name__, 'Cell')
        sc = root.createSchematicFromPath(p)
        self.assertEqual(sc.__class__.__name__, 'Schematic')
        sy = root.createSymbolFromPath(p)
        self.assertEqual(sy.__class__.__name__, 'Symbol')
        
        