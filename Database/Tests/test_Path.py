import unittest

from Database.Path import *

class PathTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01a_createFromPathName(self):
        p = Path.createFromPathName('a.b.c.d/e/f')
        self.assertEqual(p.name, 'a.b.c.d/e/f')
        self.assertEqual(p.absolute, True)
        self.assertEqual(p.libraryPath, ['a', 'b', 'c', 'd'])
        self.assertEqual(p.cellName, 'e')
        self.assertEqual(p.cellViewName, 'f')
        
    def test_01b_createFromNames(self):
        p = Path.createFromNames('a.b.c.d', 'e', 'f')
        self.assertEqual(p.name, 'a.b.c.d/e/f')
        self.assertEqual(p.absolute, True)
        self.assertEqual(p.libraryPath, ['a', 'b', 'c', 'd'])
        self.assertEqual(p.cellName, 'e')
        self.assertEqual(p.cellViewName, 'f')
        
    def test_02_createFromPath(self):
        p1 = Path.createFromPathName('a.b.c.d/e/f')
        p2 = Path.createFromPath(p1)
        self.assertEqual(p1.name, p2.name)
        self.assertEqual(p1.absolute, p2.absolute)
        self.assertEqual(p1.cellName, p2.cellName)
        self.assertEqual(p1.cellViewName, p2.cellViewName)
        self.assertEqual(p1.libraryPath, p2.libraryPath)

    def test_03_descended(self):
        p1 = Path.createFromPathName('a.b.c.d/e/f')
        p2 = p1.descend
        p3 = p2.descend
        p4 = p3.descend
        p5 = p4.descend
        self.assertEqual(p1.libraryPath, ['a', 'b', 'c', 'd'])
        self.assertEqual(p2.libraryPath, ['b', 'c', 'd'])
        self.assertEqual(p2.absolute, False)
        self.assertEqual(p3.libraryPath, ['c', 'd'])
        self.assertEqual(p4.libraryPath, ['d'])
        self.assertNotEqual(p4.subLibrary, None)
        self.assertEqual(p5.libraryPath, [])
        self.assertEqual(p5.subLibrary, None)
        #self.assertRaises(PathError, lambda: p4.descend)

    def test_04_cell(self):
        p1 = Path.createFromPathName('a.b.c.d/e/f')
        p2 = p1.cell
        self.assertEqual('a.b.c.d/e', p2.name)
        self.assertEqual(p1.absolute, p2.absolute)
        self.assertEqual(p1.cellName, p2.cellName)
        self.assertEqual(None, p2.cellViewName)
        self.assertEqual(p1.libraryPath, p2.libraryPath)

    def test_05_library(self):
        p1 = Path.createFromPathName('a.b.c.d/e/f')
        p2 = p1.library
        self.assertEqual('a.b.c.d', p2.name)
        self.assertEqual(p1.absolute, p2.absolute)
        self.assertEqual(None, p2.cellName)
        self.assertEqual(None, p2.cellViewName)
        self.assertEqual(p1.libraryPath, p2.libraryPath)

    def test_06_parentLibrary(self):
        p1 = Path.createFromPathName('a.b.c.d/e/f')
        p2 = p1.parentLibrary
        self.assertEqual('a.b.c', p2.name)
        self.assertEqual(p1.absolute, p2.absolute)
        self.assertEqual(None, p2.cellName)
        self.assertEqual(None, p2.cellViewName)
        self.assertEqual(['a', 'b', 'c'], p2.libraryPath)
        p3 = p2.parentLibrary
        self.assertEqual('a.b', p3.name)
        self.assertNotEqual(p3.subLibrary, None)
        p4 = p3.parentLibrary
        self.assertEqual('a', p4.name)
        self.assertNotEqual(p4.subLibrary, None)
        self.assertEqual(p4.absolute, True)
        self.assertRaises(PathError, lambda: p4.parentLibrary)

    def test_07_relative(self):
        p1 = Path.createFromPathName('.a.b.c.d/e/f')
        #self.assertEqual('.a.b.c.d/e/f', p1.name)
        self.assertEqual(False, p1.absolute)
        self.assertEqual(['a', 'b', 'c', 'd'], p1.libraryPath)
        p1 = Path.createFromPathName('./e/f')
        self.assertEqual('./e/f', p1.name)
        self.assertEqual(False, p1.absolute)
        self.assertEqual([], p1.libraryPath)

    def test_08_exceptions(self):
        self.assertRaises(PathError, Path.createFromPathName, '/e/f')
        self.assertRaises(PathError, Path.createFromPathName, 'a.b.c.d./e/f')
        self.assertRaises(PathError, Path.createFromPathName, 'a.b.c..d/e/f')
        self.assertRaises(PathError, Path.createFromPathName, 'a.b.c.d//f')
        self.assertRaises(PathError, Path.createFromPathName, 'a.b.c.d/e/f/g')
