# -*- coding: utf-8 -*-

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

# This file is part of PSchem.
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PSchem.  If not, see <http://www.gnu.org/licenses/>.

import Globals
Qt = __import__(Globals.UI,  globals(),  locals(),  ['QtCore',  'QtGui'])
QtCore = Qt.QtCore
QtGui = Qt.QtGui

#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

#from ..PSchem.ConsoleWidget import *
from PSchem.ConsoleWidget import *
from PSchem.Controller import *
from PSchem.LibraryHierarchyWidget import *
from PSchem.DesignHierarchyWidget import *
from PSchem.LayerWidget import *
from PSchem.ToolOptions import *
from PSchem.DesignView import *
from PSchem.GraphicsScene import *
from PSchem.LayerView import *
from PSchem.Resources_rc import *
from Database import Database
from Database import Cells, Reader
import os

class SubWindow(QtGui.QMdiSubWindow):
    def __init__(self, window):
        QtGui.QMdiSubWindow.__init__(self)
        self.mainWindow = window

    def closeEvent(self, event):
        self.mainWindow.updateMdi()
        
class PWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.docks = set()
        self.hiddenDocks = set()

        self._currentView = None

        self._databaseTimer = None
        self.database = Database.createDatabase(self)

        #print os.path.join(os.getcwd(), 'pschem.ini')
        self.settings = QtCore.QSettings('pschem', 'pschem')
        self.actions = QtCore.QSettings(
            os.path.join(os.getcwd(), 'pschem_actions.ini'),
            QtCore.QSettings.IniFormat)
        #self.settings.setPath(
        #    QtCore.QSettings.NativeFormat,
        #    QtCore.QSettings.UserScope,
        #    sys.argv[0])
        val = self.settings.value('window/geometry')
        ##if (val.canConvert(QtCore.QVariant.ByteArray)):
        ##    self.restoreGeometry(val.toByteArray())
        self.createConsole()
        self.createToolOptions()
        self.createLibraryHierarchyWidget()
        self.createDesignHierarchyWidget()
        self.createLayerWidget()
        self.createEditorWidget()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        #self.setCorner(QtCore.Qt.TopLeftCorner,
        #               QtCore.Qt.LeftDockWidgetArea)
        #self.setCorner(QtCore.Qt.BottomLeftCorner,
        #               QtCore.Qt.LeftDockWidgetArea)
        #self.setCorner(QtCore.Qt.TopRightCorner,
        #               QtCore.Qt.RightDockWidgetArea)
        #self.setCorner(QtCore.Qt.BottomRightCorner,
        #               QtCore.Qt.RightDockWidgetArea)
        self.tabifyDockWidget(self.dockTool, self.dockH)
        self.tabifyDockWidget(self.dockH, self.dockD)

        #val = self.settings.value('window/state')
        #if (val.canConvert(QtCore.QVariant.ByteArray)):
        #    self.restoreState(val.toByteArray())

    def show(self):
        QtGui.QMainWindow.show(self)
        #self.controller.repl()
    
    def createConsole(self):
        self.consoleWidget = ConsoleWidget(self)
        self.controller = Controller(self)
        #self.controller.setConsole(self.consoleWidget)
        #self.setCentralWidget(self.consoleWidget)
        self.dockC = QtGui.QDockWidget(self.tr("Console"), self)
        self.dockC.setObjectName('consoleDock')
        self.docks.add(self.dockC)
        self.dockC.setWidget(self.consoleWidget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockC)


    def createLibraryHierarchyWidget(self):
        self.dockD = QtGui.QDockWidget(self.tr("Libraries"), self)
        self.dockD.setObjectName('librariesDock')
        self.docks.add(self.dockD)
        self.libraryHierarchyModel = LibraryHierarchyModel(self.database.libraries)
        self.libraryHierarchyWidget = LibraryHierarchyWidget(self, self.libraryHierarchyModel)
        self.dockD.setWidget(self.libraryHierarchyWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockD)
        #self.tabifyDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

    def createDesignHierarchyWidget(self):
        self.dockH = QtGui.QDockWidget(self.tr("Designs"), self)
        self.dockH.setObjectName('designsDock')
        self.docks.add(self.dockH)
        self.designHierarchyModel = DesignHierarchyModel(self.database.designs)
        self.designHierarchyWidget = DesignHierarchyWidget(self, self.designHierarchyModel)
        
        self.dockH.setWidget(self.designHierarchyWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockH)

    def loadLayers(self):
        self.layers = Layers(self.database)
        self.layersView = LayersView(self.layers)

        l = Layer()
        l.name = 'background'
        l.type = 'drawing'
        l.linePattern = LinePattern(LinePattern.Solid, 0, 0)
        l.fillPattern = FillPattern(FillPattern.Solid)
        #l.fillPattern = FillPattern(FillPattern.DiagCross)
        l.color = Color(Color.Black)
        l.zValue = 0
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'gridminor'
        l.type = 'drawing'
        l.linePattern = LinePattern(LinePattern.Solid, 0, 0)
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color([40, 40, 40])
        l.zValue = 1
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'gridmajor'
        l.type = 'drawing'
        l.linePattern = LinePattern(LinePattern.Solid, 0, 0)
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color([50, 50, 50])
        l.zValue = 2
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'axes'
        l.type = 'drawing'
        l.linePattern = LinePattern(LinePattern.Solid, 0, 0)
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color([60, 60, 60])
        l.zValue = 3
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'net'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0.1, 1)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Cyan)
        l.zValue = 100
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'bus'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0.5, 1)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Cyan)
        l.zValue = 100
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'pin'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0.1, 1)
        #p.setEndStyle = LinePattern.SquareEnd
        p.setEndStyle = LinePattern.FlatEnd
        l.linePattern = p
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Red)
        l.zValue = 200
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'annotation' #no fill
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0.1, 1)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        l.color = Color(Color.Green)
        l.zValue = 50
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'annotation2'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0.1, 1)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        #l.fillPattern = FillPattern(FillPattern.Solid)
        l.fillPattern = FillPattern(FillPattern.Dense4)
        l.color = Color(Color.Green)
        l.zValue = 55
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'attribute'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0.1, 1)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Yellow)
        l.zValue = 400
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'instance'
        l.type = 'drawing'
        p = LinePattern(LinePattern.NoLine, 0, 0)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        l.color = Color(Color.White)
        l.zValue = 1000
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'selection'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0, 1)
        p.setEndStyle = LinePattern.RoundEnd
        l.linePattern = p
        #l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Red)
        l.zValue = 900000
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'preselection'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Dash, 0, 1)
        p.setEndStyle = LinePattern.FlatEnd
        l.linePattern = p
        #l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Yellow)
        l.zValue = 900010
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'lasso'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Dash, 0, 1)
        p.setEndStyle = LinePattern.FlatEnd
        l.linePattern = p
        #l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.White)
        l.zValue = 900020
        self.layers.addLayer(l)

        l = Layer()
        l.name = 'cursor'
        l.type = 'drawing'
        p = LinePattern(LinePattern.Solid, 0, 1)
        l.linePattern = p
        #l.fillPattern = FillPattern(FillPattern.Solid)
        l.color = Color(Color.Yellow)
        l.zValue = 1000000
        self.layers.addLayer(l)

        self.database.layers = self.layers

    def createLayerWidget(self):
        self.loadLayers()
        self.dockL = QtGui.QDockWidget(self.tr("Layers"), self)
        self.dockL.setObjectName('layerDock')
        self.docks.add(self.dockL)
        #self.dockL.setTitleBarWidget(None)
        #self.dockL.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar)
        self.layerModel = LayerModel(self.layersView)
        self.layerWidget = LayerWidget(self)
        self.layerWidget.setSourceModel(self.layerModel)
        
        #self.hierarchyWidget.setModel(self.hierarchyProxyModel)
        #self.hierarchyWidget.setSortingEnabled(True)
        self.dockL.setWidget(self.layerWidget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockL)

    def createToolOptions(self):
        self.dockTool = QtGui.QDockWidget(self.tr("Tool Options"), self)
        self.dockTool.setObjectName('toolOptionsDock')
        self.docks.add(self.dockTool)
        #self.selectToolOptions = SelectToolOptions()
        self.selectToolOptions = ToolOptions()
        self.dockTool.setWidget(self.selectToolOptions)
        #self.consoleWidget.setObjectName('')
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dockTool)

    def createEditorWidget(self):
        self.mdiArea = QtGui.QMdiArea()
        #self.mdiArea = QtGui.QTabWidget()
        #self.mdiArea.addTab(None, '')
        #versionMaj = QtCore.QT_VERSION / 256 / 256
        #versionMin = QtCore.QT_VERSION / 256 % 256
        #if versionMaj >= 4 and versionMin >=6:
        #    self.mdiArea.setMovable(True)
        #    self.mdiArea.setTabsClosable(True)
        
        self.mdiArea.setViewMode(QtGui.QMdiArea.TabbedView)
        #self.mdiArea.setTabShape(QtGui.QTabWidget.Triangular)
        self.setCentralWidget(self.mdiArea)
        self.connect(self.mdiArea, QtCore.SIGNAL("subWindowActivated(QMdiSubWindow *)"),
                     self.updateMdi);


    def writeActionsArray(self, array, prefix):
        self.actions.beginWriteArray(prefix)
        for i in range(len(array)):
            self.actions.setArrayIndex(i)
            if array[i].has_key('type'):
                self.actions.setValue('type', QtCore.QVariant(array[i]['type']))
            if array[i].has_key('text'):
                self.actions.setValue('text', QtCore.QVariant(array[i]['text']))
            if array[i].has_key('longText'):
                self.actions.setValue('longText', QtCore.QVariant(array[i]['longText']))
            if array[i].has_key('icon'):
                self.actions.setValue('icon', QtCore.QVariant(array[i]['icon']))
            if array[i].has_key('shortcut'):
                self.actions.setValue('shortcut', QtCore.QVariant(array[i]['shortcut']))
            if array[i].has_key('command'):
                self.actions.setValue('command', QtCore.QVariant(array[i]['command']))
        self.actions.endArray()
        

    def readActionsArray(self, array, prefix):
        size = self.actions.beginReadArray(prefix)
        for i in range(size):
            #print i
            self.actions.setArrayIndex(i)
            array.append({})
            if self.actions.contains('type'):
                array[i]['type'] = str(self.actions.value('type').toString())
            array[i]['text'] = str(self.actions.value('text').toString())
            array[i]['longText'] = str(self.actions.value('longText').toString())
            array[i]['longText'] = str(self.actions.value('longText').toString())
            array[i]['icon'] = str(self.actions.value('icon').toString())
            array[i]['shortcut'] = str(self.actions.value('shortcut').toString())
            array[i]['command'] = str(self.actions.value('command').toString())
        self.actions.endArray()

    def createActions(self):
        #val = self.settings.value('window/state')
        #if (val.canConvert(QtCore.QVariant.ByteArray)):
        #    self.restoreState(val.toByteArray())

        #self.actions.beginGroup('actions')
        #self.databaseActions = []
        #self.schematicActions = []
        #self.symbolActions = []
        #self.windowsActions = []
        #self.helpActions = []
        #self.readActionsArray(self.databaseActions, 'actions/database')
        #self.readActionsArray(self.schematicActions, 'actions/schematic')
        #self.readActionsArray(self.symbolActions, 'actions/symbol')
        #self.readActionsArray(self.windowsActions, 'actions/windows')
        #self.readActionsArray(self.helpActions, 'actions/help')


        self.openCellViewAct = QtGui.QAction(self.tr("&Open cellview"), self)
        self.openCellViewAct.setShortcut(self.tr("Ctrl+O"))
        self.openCellViewAct.setStatusTip(self.tr("Open selected cellview"))
        self.openCellViewCmd = Command("window.openCellView(window.libraryHierarchyWidget.selectedCellView())")
        self.connect(self.openCellViewAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.openCellViewCmd))


        self.exitAct = QtGui.QAction(self.tr("E&xit"), self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(self.tr("Exit the application"))
        self.exitCmd = Command("window.close()")
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.exitCmd))

        
        self.toggleDocksAct = QtGui.QAction(self.tr("Toggle Docks"), self)
        self.toggleDocksAct.setShortcut(self.tr("F11"))
        self.toggleDocksAct.setStatusTip(self.tr("Toggle visibility of the main window docks"))
        self.toggleDocksCmd = Command("window.toggleDocks()")
        self.connect(self.toggleDocksAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.toggleDocksCmd))


        self.aboutAct = QtGui.QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        #self.aboutCmd = Command("About.about()")
        #self.connect(self.aboutAct, QtCore.SIGNAL("triggered()"),
        #            lambda: self.controller.execute(self.aboutCmd))
        

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.aboutQtCmd = Command("QtGui.qApp.aboutQt()")
        self.connect(self.aboutQtAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.aboutQtCmd))


        self.tileWindowsAct = QtGui.QAction(self.tr("Tile Windows"), self)
        self.tileWindowsAct.setStatusTip(self.tr("Tile Windows"))
        self.tileWindowsCmd = Command("window.mdiArea.tileSubWindows()")
        self.connect(self.tileWindowsAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.tileWindowsCmd))


        self.cascadeWindowsAct = QtGui.QAction(self.tr("Cascade Windows"), self)
        self.cascadeWindowsAct.setStatusTip(self.tr("Cascade Windows"))
        self.cascadeWindowsCmd = Command("window.mdiArea.cascadeSubWindows()")
        self.connect(self.cascadeWindowsAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.cascadeWindowsCmd))


        self.closeWindowsAct = QtGui.QAction(self.tr("Close All Windows"), self)
        self.closeWindowsAct.setStatusTip(self.tr("Close All Windows"))
        self.closeWindowsCmd = Command("window.mdiArea.closeAllSubWindow()")
        self.connect(self.closeWindowsAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.closeWindowsCmd))


        self.closeWindowAct = QtGui.QAction(self.tr("Close Window"), self)
        self.closeWindowAct.setStatusTip(self.tr("Close Window"))
        self.closeWindowCmd = Command("window.mdiArea.closeActiveSubWindow()")
        self.connect(self.closeWindowAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.closeWindowCmd))


        self.maximizeWindowAct = QtGui.QAction(self.tr("Maximize Window"), self)
        self.maximizeWindowAct.setStatusTip(self.tr("Maximize Current Window"))
        self.maximizeWindowCmd = Command("window.mdiArea.activeSubWindow().showMaximized()")
        self.connect(self.maximizeWindowAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.maximizeWindowCmd))


        self.minimizeWindowAct = QtGui.QAction(self.tr("Minimize Window"), self)
        self.minimizeWindowAct.setStatusTip(self.tr("Minimize Current Window"))
        self.minimizeWindowCmd = Command("window.mdiArea.activeSubWindow().showMinimized()")
        self.connect(self.minimizeWindowAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.minimizeWindowCmd))


        self.zoomInAct = QtGui.QAction(self.tr("Zoom In"), self)
        self.zoomInAct.setStatusTip(self.tr("Zoom In Mode"))
        self.zoomInAct.setShortcut(self.tr("Z"))
        self.zoomInCmd = Command("currentView().modeStack.pushZoomInMode()")
        self.connect(self.zoomInAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.zoomInCmd))


        self.moveAct = QtGui.QAction(self.tr("Move"), self)
        self.moveAct.setStatusTip(self.tr("Move Mode"))
        self.moveAct.setShortcut(self.tr("M"))
        self.moveCmd = Command("currentView().modeStack.pushMoveMode()")
        self.connect(self.moveAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.moveCmd))


        self.zoomPrevAct = QtGui.QAction(self.tr("Previews View"), self)
        self.zoomPrevAct.setStatusTip(self.tr("Previews View"))
        self.zoomPrevAct.setShortcut(self.tr("Shift+Z"))
        self.zoomPrevCmd = Command("currentView().undoViewStack.popView()")
        self.connect(self.zoomPrevAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.zoomPrevCmd))


        self.quitModeAct = QtGui.QAction(self.tr("Quit Mode"), self)
        self.quitModeAct.setStatusTip(self.tr("Return to Previous Editing Mode"))
        self.quitModeAct.setShortcut(self.tr("Esc"))
        self.quitModeCmd = Command("currentView().modeStack.popMode()")
        self.connect(self.quitModeAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.quitModeCmd))


        self.panLeftAct = QtGui.QAction(self.tr("Pan Left"), self)
        self.panLeftAct.setStatusTip(self.tr("Pan the current view left"))
        self.panLeftAct.setShortcut(self.tr("Left"))
        self.panLeftCmd = Command("currentView().move(-0.25, 0)")
        self.connect(self.panLeftAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.panLeftCmd))

        self.panRightAct = QtGui.QAction(self.tr("Pan Right"), self)
        self.panRightAct.setStatusTip(self.tr("Pan the current view right"))
        self.panRightAct.setShortcut(self.tr("Right"))
        self.panRightCmd = Command("currentView().move(0.25, 0)")
        self.connect(self.panRightAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.panRightCmd))

        self.panUpAct = QtGui.QAction(self.tr("Pan Up"), self)
        self.panUpAct.setStatusTip(self.tr("Pan the current view up"))
        self.panUpAct.setShortcut(self.tr("Up"))
        self.panUpCmd = Command("currentView().move(0, 0.25)")
        self.connect(self.panUpAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.panUpCmd))

        self.panDownAct = QtGui.QAction(self.tr("Pan Down"), self)
        self.panDownAct.setStatusTip(self.tr("Pan the current view down"))
        self.panDownAct.setShortcut(self.tr("Down"))
        self.panDownCmd = Command("currentView().move(0, -0.25)")
        self.connect(self.panDownAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.panDownCmd))

        self.zoomIn2Act = QtGui.QAction(self.tr("Zoom In"), self)
        self.zoomIn2Act.setStatusTip(self.tr("Zoom the current view in"))
        self.zoomIn2Act.setShortcut(self.tr(']'))
        self.zoomIn2Cmd = Command("currentView().zoom(2.0)")
        self.connect(self.zoomIn2Act, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.zoomIn2Cmd))
                    #lambda: self.controller.parse("window.currentView().scale(1.41421356237)"))

        self.zoomOut2Act = QtGui.QAction(self.tr("Zoom Out"), self)
        self.zoomOut2Act.setStatusTip(self.tr("Zoom the current view out"))
        self.zoomOut2Act.setShortcut(self.tr('['))
        self.zoomOut2Cmd = Command("currentView().zoom(0.5)")
        self.connect(self.zoomOut2Act, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.zoomOut2Cmd))

        self.fitAct = QtGui.QAction(self.tr("Fit"), self)
        self.fitAct.setStatusTip(self.tr("Fit contents to the current view"))
        self.fitAct.setShortcut(self.tr('f'))
        self.fitCmd = Command("currentView().fit()")
        self.connect(self.fitAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.fitCmd))

        self.newSchematicAct = QtGui.QAction(self.tr("&New Schematic"), self)
        self.newSchematicAct.setStatusTip(self.tr("&New Schematic"))
        self.newSchematicAct.setShortcut(self.tr('Ctrl+N'))
        self.newSchematicAct.setIcon(QtGui.QIcon(':/images/new.png'))
        self.newSchematicCmd = Command("window.newSchematic()")
        self.connect(self.newSchematicAct, QtCore.SIGNAL("triggered()"),
                    lambda: self.controller.execute(self.newSchematicCmd))

                    
#2\text=&New Schematic
#2\longText=&New Schematic
#2\icon=:/images/new.png
#2\shortcut=Ctrl+N
#2\command=window.newSchematic()
                    
        #self.actions.append({})
        #self.actions[0]['text'] = 'About &Qt'
        #self.actions[0]['longText'] = 'About &Qt'
        #self.actions[0]['command'] = 'QtGui.qApp.aboutQt()'
        #self.actions.append({})
        #self.actions[1]['text'] = '&New Schematic'
        #self.actions[1]['longText'] = '&New Schematic'
        #self.actions[1]['icon'] = ':/images/new.png'
        #self.actions[1]['shortcut'] = ':/images/new.png'
        #self.actions[1]['command'] = 'window.newSchematic()'

    def makeLambda(self, arg):
        "Workaround for Python's lack of decent closures"
        return lambda : self.controller.parse(arg)

    def createMenus(self):
        size = self.actions.beginReadArray('database')
        self.databaseMenu = self.menuBar().addMenu(self.tr("&Database"))
        self.databaseToolBar = self.addToolBar(self.tr("File"))
        self.databaseToolBar.setObjectName('fileToolbar')
        for i in range(size):
            self.actions.setArrayIndex(i)
            if (self.actions.contains('type') and
                self.actions.value('type').toString() == 'separator'):
                self.databaseMenu.addSeparator()
            else:
                if self.actions.contains('text'):
                    if self.actions.contains('icon'):
                        action = QtGui.QAction(
                            QtGui.QIcon(str(self.actions.value('icon').toString())),
                            str(self.actions.value('text').toString()),
                            self)
                    else:
                        action = QtGui.QAction(
                            str(self.actions.value('text').toString()),
                            self)
                    if self.actions.contains('shortcut'):
                        action.setShortcut(
                            str(self.actions.value('shortcut').toString()))
                    if self.actions.contains('longText'):
                        action.setStatusTip(
                            str(self.actions.value('longText').toString()))
                    if self.actions.contains('command'):
                        self.connect(
                            action, QtCore.SIGNAL('triggered()'),
                            self.makeLambda(str(self.actions.value('command').toString())))
                    self.databaseMenu.addAction(action)
                    if self.actions.contains('icon'):
                        self.databaseToolBar.addAction(action)
        self.actions.endArray()

        self.databaseMenu.addAction(self.openCellViewAct)
        self.databaseMenu.addAction(self.newSchematicAct)
        self.databaseMenu.addAction(self.toggleDocksAct)
        self.databaseMenu.addAction(self.zoomInAct)
        self.databaseMenu.addAction(self.zoomPrevAct)
        self.databaseMenu.addAction(self.moveAct)
        self.databaseMenu.addAction(self.quitModeAct)

        self.windowsMenu = QtGui.QMenu(self.tr("&Windows"))
        self.windowsAct = self.menuBar().addMenu(self.windowsMenu)
        self.menuBar().removeAction(self.windowsAct)
        self.windowsMenu.addAction(self.tileWindowsAct)
        self.windowsMenu.addAction(self.cascadeWindowsAct)
        self.windowsMenu.addSeparator();
        self.windowsMenu.addAction(self.closeWindowsAct)
        self.windowsMenu.addSeparator();
        self.windowsMenu.addAction(self.maximizeWindowAct)
        self.windowsMenu.addAction(self.minimizeWindowAct)
        self.windowsMenu.addSeparator();
        self.windowsMenu.addAction(self.closeWindowAct)


        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)


    def createToolBars(self):
        self.databaseToolBar = self.addToolBar(self.tr("File"))
        self.databaseToolBar.setObjectName('fileToolbar')
        self.databaseToolBar.addAction(self.newSchematicAct)
        #self.databaseToolBar.addAction(self.openAct)
        #self.databaseToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar(self.tr("Edit"))
        self.editToolBar.setObjectName('editToolbar')

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))


    def closeEvent(self, event):
        self.settings.setValue('window/geometry', self.saveGeometry())
        self.settings.setValue('window/state', self.saveState())
        QtGui.QWidget.closeEvent(self, event)
        
        
    def currentView(self):
        #return self._currentWindow
        return self._currentView

    def currentCellView(self):
        if self._currentView and self._currentView.scene():
            return self._currentView.scene().cellView()
            
            
    #def keyPressEvent(self, event):
        #key = event.key()
        #print key
        #if key == QtCore.Qt.Key_Up:
        #    self.currentWindow().moveView(0, -0.25)
            #self.centerNode.moveBy(0, -20)
            #BrushMatrix.translate(0,-20)
        #elif key == QtCore.Qt.Key_Down:
        #    self.currentWindow().moveView(0, 0.25)
            #self.centerNode.moveBy(0, 20)
            #BrushMatrix.translate(0,20)
        #elif key == QtCore.Qt.Key_Left:
        #    self.currentWindow().moveView(0.25, 0)
            #self.centerNode.moveBy(-20, 0)
            #BrushMatrix.translate(-20,0)
        #elif key == QtCore.Qt.Key_Right:
        #    self.currentWindow().moveView(-0.25, 0)
            #self.centerNode.moveBy(20, 0)
            #BrushMatrix.translate(20,0)
        #elif key == QtCore.Qt.Key_F:
        #    self.currentWindow().fitInView()
            #sr = self.scene.sceneRect()
            #self.middlePoint = QPointF(sr.x() + sr.width()/2, sr.y() + sr.height()/2)
            #self.moveView(0, 0, 1)
        #elif key == QtCore.Qt.Key_Plus or key == QtCore.Qt.Key_BracketRight:
        #    self.currentWindow().scaleView(2.0)
        #elif key == QtCore.Qt.Key_Minus or key == QtCore.Qt.Key_BracketLeft:
        #    self.currentWindow().scaleView(1 / 2.0)
        #else:
        #    QtGui.QMainWindow.keyPressEvent(self, event)
        #m = self.matrix()
        #print "matrix  ", m.dx(), m.dy(), m.m11()


    def toggleDocks(self):
        if len(self.hiddenDocks) > 0:
            for d in self.hiddenDocks:
                #print d
                d.show()
            self.hiddenDocks = set()
        else:
            for d in self.docks:
                #print d
                if d.isVisible():
                    d.hide()
                    self.hiddenDocks.add(d)

    def detachCurrentView(self):
        subwin = self.mdiArea.activeSubWindow()
        if subwin:
            widget = subwin.widget()
            widget.setWindowFlags(QtCore.Qt.Window)
            #subwin.hide()
            #widget.setParent(self)
            widget.show()
            #subwin.removeWidget(widget)
            #win = QtGui.QWidget(self, QtCore.Qt.Window)
            #layout = QtGui.QVBoxLayout()
            #layout.setSpacing(0)
            #layout.addWidget(subwin.widget())
            #win.setLayout(layout)
            #self.mdiArea.removeSubWindow(subwin)
            #print subwin, subwin.widget().getContentsMargins(), subwin.isWindow() 
            #widget.setWindowFlags(QtCore.Qt.Window)
            #win.show()
            #subwin.widget().setWindow

    def updateMdi(self):
        subwin = self.mdiArea.activeSubWindow()
        if subwin:
            self.setCurrentView(subwin.widget())
        #self.controller.parse("window.setCurrentWindow(window.currentWindow)")
        self.updateWindowsMenu()
        winNo = len(self.mdiArea.subWindowList())


    def updateWindowsMenu(self):
        subWins = self.mdiArea.subWindowList()
        if len(subWins) > 0:
            self.menuBar().addAction(self.windowsAct)
            #self.windowsMenu = self.menuBar().addMenu(self.tr("&Windows"))
            #self.addDatabaseMenu = self.databaseMenu.addMenu(self.tr("&Add Database"))
            #self.databaseMenu.addAction(self.relDAct)
            #self.databaseMenu.addSeparator();
            #self.databaseMenu.addAction(self.exitAct)
            
            #self.addDatabaseMenu.addAction(self.addGnucapDAct)
            
            
            #self.optionsMenu = self.menuBar().addMenu(self.tr("&Options"))
            #self.optionsMenu.addAction(self.openWWAct)
            
            #self.menuBar().addSeparator()
            
            #self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))
            #self.helpMenu.addAction(self.aboutAct)
            #self.helpMenu.addAction(self.aboutQtAct)
        else:
            self.menuBar().removeAction(self.windowsAct)


        
    def setCurrentView(self, view):
        if self._currentView:
            self._currentView.uninstallActions()
        self._currentView = view
        view.installActions()

        
    def newSchematic(self):
        #lib = self.database.makeLibrary('work')
        #self.database.addLibrary(lib)
        gEDA_Symbols = '../geda/symbols'
        gEDA_Examples = '../geda/examples'
        spnet = '../spNet'
        flicker = '../flicker'
        gsim = '../gsim'
        SXI = '../SXI'
        
        importer = Reader.GedaImporter(self.database.libraries)
        importer.importLibraryList(
            [
                ['spnet.latch', spnet + '/latch'],
                ['spnet.sym.analog', spnet + '/sym/analog'],
                ['spnet.sym.titleblock', spnet + '/sym/titleblock'],
                ['spnet.sym.spice', spnet + '/sym/spice'],
#                ['sym.4000', gEDA_Symbols + '/4000'],
#                ['sym.74', gEDA_Symbols + '/74'],
#                ['sym.allegro', gEDA_Symbols + '/allegro'],
#                ['sym.altera', gEDA_Symbols + '/altera'],
#                ['sym.amphenol', gEDA_Symbols + '/amphenol'],
                ['sym.analog', gEDA_Symbols + '/analog'],
#                ['sym.apex', gEDA_Symbols + '/apex'],
                ['sym.asic', gEDA_Symbols + '/asic'],
                ['sym.asicpads', gEDA_Symbols + '/asicpads'],
                ['sym.bus', gEDA_Symbols + '/bus'],
                ['sym.cascade', gEDA_Symbols + '/cascade'],
                ['sym.connector', gEDA_Symbols + '/connector'],
#                ['sym.dec', gEDA_Symbols + '/dec'],
                ['sym.diode', gEDA_Symbols + '/diode'],
#                ['sym.ecl', gEDA_Symbols + '/ecl'],
##                ['sym.gnetman', gEDA_Symbols + '/gnetman'],
#                ['sym.idt', gEDA_Symbols + '/idt'],
                ['sym.IEC417', gEDA_Symbols + '/IEC417'],
                ['sym.io', gEDA_Symbols + '/io'],
#                ['sym.irf', gEDA_Symbols + '/irf'],
#                ['sym.lattice', gEDA_Symbols + '/lattice'],
#                ['sym.linear', gEDA_Symbols + '/linear'],
#                ['sym.maxim', gEDA_Symbols + '/maxim'],
#                ['sym.memory', gEDA_Symbols + '/memory'],
#                ['sym.micro', gEDA_Symbols + '/micro'],
#                ['sym.minicircuits', gEDA_Symbols + '/minicircuits'],
                ['sym.misc', gEDA_Symbols + '/misc'],
#                ['sym.national', gEDA_Symbols + '/national'],
#                ['sym.opto', gEDA_Symbols + '/opto'],
#                ['sym.philips', gEDA_Symbols + '/philips'],
#                ['sym.pla', gEDA_Symbols + '/pla'],
                ['sym.power', gEDA_Symbols + '/power'],
#                ['sym.radio', gEDA_Symbols + '/radio'],
#                ['sym.relay', gEDA_Symbols + '/relay'],
#                ['sym.rf', gEDA_Symbols + '/rf'],
                ['sym.spice', gEDA_Symbols + '/spice'],
#                ['sym.st', gEDA_Symbols + '/st'],
#                ['sym.supervisor', gEDA_Symbols + '/supervisor'],
#                ['sym.switcap', gEDA_Symbols + '/switcap'],
                ['sym.switch', gEDA_Symbols + '/switch'],
                ['sym.titleblock', gEDA_Symbols + '/titleblock'],
#                ['sym.transistor', gEDA_Symbols + '/transistor'],
#                ['sym.tube', gEDA_Symbols + '/tube'],
#                ['sym.verilog', gEDA_Symbols + '/verilog'],
#                ['sym.vhdl', gEDA_Symbols + '/vhdl'],
#                ['sym.xilinx', gEDA_Symbols + '/xilinx'],
##                ['sym.font', gEDA_Symbols + '/font'],
                ['examples.lightning_detector', gEDA_Examples + '/lightning_detector/sym'],
                ['examples.gTAG', gEDA_Examples + '/gTAG'],
                ['flicker', flicker + '/ee/sym'],
                ['flicker.openIP', flicker + '/ee/openIP'],
                ['gsim.sym', gsim + '/sym/capacitor'],
                ['gsim.sym', gsim + '/sym/diode'],
                ['gsim.sym', gsim + '/sym/ic-analog'],
                ['gsim.sym', gsim + '/sym/inductor'],
                ['gsim.sym', gsim + '/sym/power'],
                ['gsim.sym', gsim + '/sym/resistor'],
                ['gsim.sym', gsim + '/sym/signal'],
                ['gsim.sym', gsim + '/sym/spice_commands'],
                ['gsim.sym', gsim + '/sym/spice_generic'],
                ['gsim.sym', gsim + '/sym/transformer'],
                ['gsim.sym', gsim + '/sym/transistor'],
                ['gsim.sym', gsim + '/sym/xspice_analog'],
                ['gsim.sym', gsim + '/sym/xspice_digital'],
                ['gsim.sym', gsim + '/sym/xspice_mixed'],
                ['gsim.sym', gsim + '/sym/xspice_model'],
                ['SXI.SXI-EM-DriverBoard', SXI + '/SXI-EM-DriverBoard/Symbols'],
            ],
            [
                ['spnet.latch', spnet + '/latch'],
                ['examples.lightning_detector', gEDA_Examples + '/lightning_detector'],
                ['examples.gTAG', gEDA_Examples + '/gTAG'],
                ['flicker', flicker + '/ee'],
                ['gsim.examples.0010_basic', gsim + '/examples/0010_basic'],
                ['gsim.examples.0020_rlc', gsim + '/examples/0020_rlc'],
                ['gsim.examples.0030_diode_bjt', gsim + '/examples/0030_diode_bjt'],
                ['gsim.examples.0040_digital', gsim + '/examples/0040_digital'],
                ['gsim.examples.0050_xspice', gsim + '/examples/0050_xspice'],
                ['gsim.examples.0060_adc', gsim + '/examples/0060_adc'],
                ['gsim.examples.0070_hybrid', gsim + '/examples/0070_hybrid'],
                ['gsim.examples.0080_filtre', gsim + '/examples/0080_filtre'],
                ['gsim.examples.0100_script', gsim + '/examples/0100_script'],
                ['SXI.SXI-EM-DriverBoard', SXI + '/SXI-EM-DriverBoard'],
            ])
        
    def openCellView(self, cellView, design = None):
        if cellView:
            if not design:
                design = Design(cellView, self.database.designs)
            scene = GraphicsScene(design)
            #self.database.addDesign(design)
            dView = DesignView(self, scene)
            subWin = SubWindow(self)
            subWin.setWidget(dView)
            subWin.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            subWin.setWindowFilePath(
                cellView.cell.name)
            subWin.setWindowModified(True)
            self.mdiArea.addSubWindow(subWin)
            #self.mdiArea.addTab(dView, cellView.cell.name)
            subWin.showMaximized()
            #subWin.setWindowState(subWin.windowState() | QtCore.Qt.WindowMaximized)
            #subWin.show()
            #dView.showMaximized()
            #subWin.show()
            #self.setCurrentView(dView)

    def openCellViewByName(self, libPath, cellName, viewName):
        cellView = self.database.cellViewByName(libPath, cellName, viewName)
        print self.__class__.__name__, cellView
        self.openCellView(cellView)

    def openDatabaseObjectByPathName(self, pathName):
        path = Path.createFromPathName(pathName)
        cellView = self.database.libraries.objectByPath(path)
        print self.__class__.__name__, cellView
        self.openCellView(cellView)

    def openDesignUnitByPathName(self, pathName):
        (cellViewPathName, sep, instancePathName) = pathName.partition(':')
        cellViewPath = Path.createFromPathName(cellViewPathName)
        cellView = self.database.libraries.objectByPath(cellViewPath)
        design = self.database.designs.designUnitByPath(cellViewPathName)
        print self.__class__.__name__, cellView, design
        self.openCellView(cellView, design)
        
    #def runDeferred(self):
    #    print self.thread()
    #    self.database.runDeferredProcesses()

    def deferredProcessingRequested(self):
        #print self.thread()
        if self._databaseTimer and self._databaseTimer.isActive():
            #self._databaseTimer.start(50)
            QtGui.qApp.processEvents()
        else:
            self._databaseTimer = QtCore.QTimer()
            self._databaseTimer.setSingleShot(True)
            self.connect(self._databaseTimer, QtCore.SIGNAL("timeout()"), self.database.runDeferredProcesses)
            self._databaseTimer.start(500)
            #.singleShot(5000, self.database.runDeferredProcesses)
        
    def leaveCPU(self):
        QtGui.qApp.processEvents()
        
