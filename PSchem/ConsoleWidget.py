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

import sys, traceback

import Globals
Qt = __import__(Globals.UI,  globals(),  locals(),  ['QtCore',  'QtGui'])
QtCore = Qt.QtCore
QtGui = Qt.QtGui

try:
    from Controller import *
except ImportError:
    pass

import os
import time
import re
from collections import deque


class Command():
    pstrip = re.compile(r'^(>>> |\.\.\. |--- )?')
    pfirst = re.compile(r'^\S+.*\:$')
    pempty = re.compile(r'^\s*$')
    pindented = re.compile(r'^\s+.*$')

    def __init__(self, commandStr = '', type = 'single'):
        self._text = commandStr
        self._type = type
        self._compiled = None
        
    def compiled(self):
        #print 'compile: ' + self.text()
        if (not self._compiled):
            self._compiled = compile(self._text, "console", self._type)
        return self._compiled
        
    def text(self):
        #text = Controller.pstrip.sub('', self._str)
        return self._text

    def lines(self):
        return self.text().splitlines(True)

    def setType(self, type):
        self._type = type
        
    def __repr__(self):
        lines = self.lines()
        if len(lines) == 0:
            return '>>> '
        txt='>>> '+lines[0]
        if len(lines) > 1:
            for l in lines[1:]:
                txt += ('... '+l)
            txt += '... \n'
        return txt
        
class StdinWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stdin

    def isatty(self):
        return True

    def readline(self):
        return self.console.readline()

    def read(self, n=1):
        return self.console.read(n)

class StdoutWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stdout

    def write(self, txt):
        self.console.write(txt)
        #if self.stream.fileno() >= 0: # for Windows (pythonw.exe) compatibility
        #    self.stream.write(txt)
        if txt.find('\n', -1) != -1:
            QtGui.qApp.processEvents() #interferes with deferred processing of Database notifications

    def writeSync(self, txt, markPos = False):
        self.console.setSynchronous(True, markPos)
        self.console.write(txt)
        self.console.setSynchronous(False)
        if self.stream.fileno() >= 0:
            self.stream.write(txt)
        if txt.find('\n', -1) != -1:
            QtGui.qApp.processEvents() #interferes with deferred processing of Database notifications

    def isatty(self):
        return True
        
    def pushSync(self, flag):
        self.console.pushSynchronous(flag)

    def popSync(self):
        self.console.popSynchronous()

class StderrWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stderr

    def write(self, txt):
        self.console.writeErr(txt)
        if self.stream.fileno() >= 0:
            self.stream.write(txt)
        QtGui.qApp.processEvents() #interferes with deferred processing of Database notifications

    def isatty(self):
        return True

class History(deque):
    pfirst = re.compile(r'^>>> ')
    prest =  re.compile(r'^\.\.\. ')
    pstart = re.compile(r'^\S+.*\:$')
    pempty = re.compile(r'^\s*$')

    def __init__(self):
        deque.__init__(self)
        self.pointer = 0
        #dir = os.path.expanduser('~')
        dir = os.getcwd()
        fileName = 'pschem.history'
        self.filePath = os.path.join(dir, fileName)
        self.restore()

    def __del__(self):
        self.save()

    def save(self):
        print 'Saving command history to ' + self.filePath
        f = open(self.filePath, 'w')
        try:
            for cmd in self:
                cmdText = unicode(cmd)
                f.write(cmdText)
                #write(cmdText)
        finally:
            f.close()

    def restore(self):
        first = True
        cmd = ''
        if os.path.exists(self.filePath) and os.path.isfile(self.filePath):
            print 'Restoring command history from ' + self.filePath
            f = open(self.filePath, 'r')
            try:
                for line in f:
                    if first and self.pfirst.search(line):
                        line = self.pfirst.sub('', line)
                        if not self.pstart.search(line):
                            self.push(Command(line, 'single'))
                        else:
                            cmd = line
                            first = False
                    elif not first and self.prest.search(line):
                        line = self.prest.sub('', line)
                        if self.pempty.search(line):
                            self.push(Command(cmd, 'exec'))
                            first = True
                        else:
                            cmd += line
                    else:
                        raise IOError
            except IOError:
                print traceback.format_exc()
            finally:
                f.close()
        else:
            print 'No history file found: ' + self.filePath

        
    def push(self, cmd):
        self._transient = None
        self.append(cmd)
        self.pointer = len(self)
        #self.pointer += 1

    def previous(self, searchTxt = None):
        if self.pointer > 0:
            self.pointer -= 1
            val = self[self.pointer]
            #print ">>" + str(searchTxt) + "<<"
            #if (not searchTxt or str(val).find(searchTxt) != -1):
            if (not searchTxt or val.find(searchTxt) != -1):
                return val
            else:
                return self.previous(searchTxt)

    def next(self, searchTxt = None):
        if (self.pointer < len(self) - 1):
            self.pointer += 1
            val = self[self.pointer]
            #print ">>" + str(searchTxt) + "<<"
            #if (not searchTxt or str(val).find(searchTxt) != -1):
            if (not searchTxt or val.find(searchTxt) != -1):
                return val
            else:
                return self.next(searchTxt)
            #return self[self.pointer]

    def __repr__(self):
        text = ''
        for cmd in self:
            text += cmd
        return text
    

            
class ConsoleWidget(QtGui.QPlainTextEdit):
    pstrip = re.compile(r'^(>>> |\.\.\. |--- )?')
    pfirst = re.compile(r'^\S+.*\:$')
    pempty = re.compile(r'^\s*$')
    pindented = re.compile(r'^\s+.*$')
    penter = re.compile(r'\n$')

    def __init__(self, window=None):
        QtGui.QPlainTextEdit.__init__(self)
        #QtGui.QTextEdit.__init__(self)

        self._lastCursorPos = 0
        self._commandCursorPos = 0
        self._printCursorPos = 0

        self._inReadline = False
        #self.setReadOnly(True)
        self.window = window
        #self.window = None
        self._buffer = None
        self._rawBuffer = None
        
        self._synchronous = True
        self._syncFlag = False
                
        self.defaultFormat = self.currentCharFormat()
        fontFamilies = QtGui.QFontDatabase().families()
        if "Consolas" in fontFamilies:
            self.defaultFormat.setFontFamily("Consolas")
        elif "Monospace" in fontFamilies:
            self.defaultFormat.setFontFamily("Monospace")
        elif "Courier New" in fontFamilies:
            self.defaultFormat.setFontFamily("Courier New")
        else:
            self.defaultFormat.setFontFamily("Courier")
        self.defaultFormat.setFontFixedPitch(True)
        self.defaultFormat.setFontItalic(False)
        self.defaultFormat.setFontWeight(QtGui.QFont.Normal)
        self.setCurrentCharFormat(self.defaultFormat)

        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        
        self.setMaximumBlockCount(10000) #arbitrary limit on number of lines
        self.setUndoRedoEnabled(False)
        
        sys.stdout = StdoutWrap(self)
        #sys.stderr = StderrWrap(self)  ### comment out if the program hangs at start-up
        sys.stdin = StdinWrap(self)

        self.menu = QtGui.QMenu(self)
        self._copyAct = QtGui.QAction(self.tr("Copy"), self)
        self._copyAct.setShortcut(self.tr("Ctrl+C"))
        self.connect(self._copyAct, QtCore.SIGNAL("triggered()"),
                    self.copy)
        self._pasteAct = QtGui.QAction(self.tr("Paste"), self)
        self._pasteAct.setShortcut(self.tr("Ctrl+V"))
        self.connect(self._pasteAct, QtCore.SIGNAL("triggered()"),
                    self.paste)

        self.menu.addAction(self._copyAct)
        self.menu.addAction(self._pasteAct)

        #self.menu.addAction(self.trUtf8('Copy'), self.copy)
        #self.menu.addAction(self.trUtf8('Paste'), self.paste)
        #self.menu.addSeparator()

        self._indent = False
        self._cmd = ''

        print self._pythonInfo()
        
        self._history = History()

        #try:
        #    sys.ps1
        #except AttributeError:
        #    sys.ps1 = '>>> '

        #try:
        #    sys.ps2
        #except AttributeError:
        #    sys.ps2 = '... '

        self._commandCursorPos = self.textCursor().position()
        self.textCursor().insertText('>>> ')
        self.setLastCursorPos()
        
    def setLastCursorPos(self):
        #sys.stdout.stream.write(str(self.textCursor().position())+'\n')
        self._lastCursorPos = self.textCursor().position()
        
    def controller(self):
        if self.window:
            return self.window.controller
        
    def history(self):
        return self._history

    def _pythonInfo(self):
        return
        return 'Python %s on %s\n' % (sys.version, sys.platform) + \
            'PyQt4 v.%s, Qt4 v.%s\n' % (QtCore.PY_VERSION_STR, QtCore.QT_VERSION_STR) + \
            'Type "help", "copyright", "credits" or "license" for more information.\n'
        
        
    def inReadline(self):
        return self._inReadline
        
    def contextMenuEvent(self,ev):
        """
        Reimplemented to show our own context menu.
        
        @param ev context menu event (QContextMenuEvent)
        """
        self.menu.popup(ev.globalPos())
        ev.accept()

    def execute(self, cmd, echo = True):
        self._history.push(cmd)
        self._buffer = None
        self.controller().execute(cmd, echo)

    def setSynchronous(self, synchronous, markPos = False):
        if markPos:
            self._asyncCursorPos = self.textCursor().position()
            #sys.stdout.stream.write(str(self._asyncCursorPos))
        self._synchronous = synchronous

    def pushSynchronous(self, synchronous, markPos = False):
        self._syncFlag = self._synchronous
        self.setSynchronous(synchronous, markPos)
        
    def popSynchronous(self):
        self.setSynchronous(self._syncFlag)

    def refCursorPos(self):
        ref = max(self._commandCursorPos, self._printCursorPos)
        return ref
        
    def write(self, txt):
        if self._synchronous:
            #cursor = self.textCursor()
            #cursor.setPosition(self._lastCursorPos)
            #self.setTextCursor(cursor)
            self.textCursor().insertText(txt, self.defaultFormat)
            self._printCursorPos = self.textCursor().position()
        else:
            frmt = QtGui.QTextCharFormat(self.defaultFormat)
            frmt.setForeground(QtGui.QBrush(QtCore.Qt.gray))
            cursor = QtGui.QTextCursor(self.document())
            cursor.setPosition(self._commandCursorPos)
            cursor.insertText(txt, frmt)
            self._commandCursorPos = cursor.position()
        self.setLastCursorPos()
        self.ensureCursorVisible()

    def writeErr(self, txt):
        self.write(txt)

    def readline(self):
        self._inReadline = True
        while True:
            #val = self.verticalScrollBar().value()
            lines = self.commandLines()
            #self.verticalScrollBar().setValue(val)
            if len(lines) > 0 and self.penter.search(lines[0]):
                break
            QtGui.qApp.processEvents()
            time.sleep(0.01)
        self._inReadline = False
        #sys.stdout.stream.write(str(lines))
        ##sys.stdout.stream.write(lines[0])
        return lines[0]

    #def readChar(self):
    #    while len(self._buffer) == 0:
    #        QtGui.qApp.processEvents()
    #        time.sleep(0.01)
    #    char = self._buffer[0]
    #    self._buffer = self._buffer[1:]
    #    return char
            
    def keyPressEvent(self, event):
        text  = event.text()
        key   = event.key()
        if self._inReadline:
            offset = 0
        else:
            offset = 4
        modifier = event.modifiers()
        if modifier & QtCore.Qt.ShiftModifier:
            mode = QtGui.QTextCursor.KeepAnchor
        else:
            mode = QtGui.QTextCursor.MoveAnchor

        cursor = self.textCursor()
        if cursor.columnNumber <= offset or cursor.position() <= self._commandCursorPos:
            cursor.setPosition(self._lastCursorPos, QtGui.QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
            
        if key == QtCore.Qt.Key_Backspace:
            cursor = self.textCursor()
            if cursor.position() == cursor.anchor():
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
                if cursor.columnNumber() < 4:
                    cursor.setPosition(cursor.position()-4, QtGui.QTextCursor.KeepAnchor)
                if cursor.position() < self.refCursorPos():
                    cursor.setPosition(self.refCursorPos()+4, QtGui.QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
            else:
                cursor.removeSelectedText()
            self.setTextCursor(cursor)
            self.setLastCursorPos()

        elif key == QtCore.Qt.Key_Delete:
            cursor = self.textCursor()
            if cursor.position() == cursor.anchor():
                cursor.deleteChar()
            else:
                cursor.removeSelectedText()
            self.setLastCursorPos()
            
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
            cursor.insertText('\n')
            self.setTextCursor(cursor)
            if not self._inReadline:
                self.commandParse()
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            self.setLastCursorPos()
        #elif key == QtCore.Qt.Key_Tab:
        #    pass
        elif key == QtCore.Qt.Key_Left:
            cursor = self.textCursor()
            if modifier & QtCore.Qt.ControlModifier:
                cursor.movePosition(QtGui.QTextCursor.PreviousWord, mode)
                if cursor.columnNumber() < offset:
                    cursor.movePosition(QtGui.QTextCursor.PreviousWord, mode)
            else:
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, mode)
                if cursor.columnNumber() < offset:
                    cursor.setPosition(cursor.position()-offset, mode)
            if cursor.position() < self.refCursorPos():
                cursor.setPosition(self.refCursorPos()+offset, mode)
            self.setTextCursor(cursor)
            self.setLastCursorPos()

        elif key == QtCore.Qt.Key_Right:
            cursor = self.textCursor()
            if modifier & QtCore.Qt.ControlModifier:
                cursor.movePosition(QtGui.QTextCursor.NextWord, mode)
            else:
                cursor.movePosition(QtGui.QTextCursor.NextCharacter, mode)
            if cursor.columnNumber() < offset:
                cursor.setPosition(cursor.position()+offset-cursor.columnNumber(), mode)
            #if cursor.position() > QtGui.QTextCursor.EndOfLine:
            #    cursor.setPosition(QtGui.QTextCursor.EndOfLine, mode)
            self.setTextCursor(cursor)
            self.setLastCursorPos()

        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor ()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine, mode)
            cursor.setPosition(cursor.position()+offset, mode)
            self.setTextCursor(cursor)
            self.setLastCursorPos()

        elif key == QtCore.Qt.Key_End:
            cursor = self.textCursor ()
            cursor.movePosition(QtGui.QTextCursor.EndOfLine, mode)
            self.setTextCursor(cursor)
            self.setLastCursorPos()

        elif key == QtCore.Qt.Key_Up and not self._inReadline:
            if not self._buffer:
                self._buffer = self.commandText()
                self._rawBuffer = self.commandRawText()
                #self.history().setTransient(Command(self.commandRawText()+'\n', 'exec'))
            cmd = self.history().previous(self._rawBuffer)
            if cmd:
                text = unicode(cmd)
                text = text[0:len(text)-1]
                self.commandClear()
                self.textCursor().insertText(text)
                self.ensureCursorVisible()
            self.setLastCursorPos()
                
        elif key == QtCore.Qt.Key_Down and not self._inReadline:
            cmd = self.history().next(self._rawBuffer)
            if cmd:
                text = unicode(cmd)
                text = text[0:len(text)-1]
                self.commandClear()
                self.textCursor().insertText(text)
                self.ensureCursorVisible()
            elif self._buffer:
                self.commandClear()
                self.textCursor().insertText(self._buffer)
                self._buffer = None
                self._rawBuffer = None
                self.ensureCursorVisible()
            self.setLastCursorPos()
        elif key == QtCore.Qt.Key_PageUp:
            event.accept()
            self.verticalScrollBar().triggerAction(QtGui.QAbstractSlider.SliderPageStepSub)
        elif key == QtCore.Qt.Key_PageDown:
            event.accept()
            self.verticalScrollBar().triggerAction(QtGui.QAbstractSlider.SliderPageStepAdd)

        elif key == QtCore.Qt.Key_C and (modifier & QtCore.Qt.ControlModifier):
            self.copy()
            return
        elif key == QtCore.Qt.Key_V and (modifier & QtCore.Qt.ControlModifier):
            self.paste()
            return
        elif len(text) > 0 and not (modifier & QtCore.Qt.ControlModifier):
            cursor = self.textCursor()
            cursor.setPosition(self._lastCursorPos)
            cursor.insertText(event.text())
            self.setTextCursor(cursor)
            self.setLastCursorPos()
            self.ensureCursorVisible()
        else:
            event.ignore()

    #
    # Command editing buffer
    #
    
    def commandParse(self):
        lines = self.commandLines()
        #print lines
        if len(lines) == 0:
            return
        line = lines[len(lines)-1]
        empty = self.pempty.search(line)
        indented = self.pindented.search(line)
        first = self.pfirst.search(line)
        if len(lines) == 1:
            if not first and not empty:
                cmd = Command(line, 'single')
                ##sys.stdout.stream.write(self.commandText())
                try:
                    self.execute(cmd, False)
                except (StandardError) as err:
                    print traceback.format_exc()
                self._commandCursorPos = self.textCursor().position()
                self.textCursor().insertText('>>> ')
            elif empty:
                self._commandCursorPos = self.textCursor().position()
                self.textCursor().insertText('>>> ')
            else:
                self.textCursor().insertText('... ')
        elif empty or not indented:
            txt = ''
            for l in lines[:-1]:
                txt += l
            cmd = Command(txt, 'exec')
            ##sys.stdout.stream.write(self.commandText())
            try:
                self.execute(cmd, False)
            except (StandardError) as err:
                print traceback.format_exc()
            if not indented:
                cursor = self.textCursor()
                cursor.movePosition(QtGui.QTextCursor.Up, QtGui.QTextCursor.KeepAnchor)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                self._commandCursorPos = cursor.position()
                cursor.insertText('>>> '+line)
                self.setTextCursor(cursor)
                self.commandParse()  # recursive call
            else:
                self._commandCursorPos = self.textCursor().position()
                self.textCursor().insertText('>>> ')
        else:
            self.textCursor().insertText('... ')
        self.setLastCursorPos()

    def commandClear(self):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        cursor.setPosition(self.refCursorPos(), QtGui.QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        #self.setTextCursor(cursor)
        
    def commandRemoveLastLine(self):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Up, QtGui.QTextCursor.KeepAnchor)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
        txt = cursor.selectedText()
        cursor.removeSelectedText()
        #self.setTextCursor(cursor)
        #txt.replace(u"\u2029", '\n')
        txt = txt.replace(u"\u2029", '\n')
        txt = unicode(txt)
        return txt
    
    def commandText(self):
        cursor = self.textCursor()
        pos = cursor.position()
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        cursor.setPosition(self.refCursorPos(), QtGui.QTextCursor.KeepAnchor)
        txt = cursor.selectedText()
        cursor.setPosition(pos, QtGui.QTextCursor.MoveAnchor)
        #self.setTextCursor(cursor)
        txt = unicode(txt)
        txt = txt.replace(u"\u2029", '\n')
        return txt

    def commandLines(self):
        txt = self.commandText()
        lines = txt.splitlines(True)
        lines2 = []
        for l in lines:
            lines2.append(self.pstrip.sub('', l))
        return lines2
        
    def commandRawText(self):
        txt = ''
        lines = self.commandLines()
        for l in lines:
            txt += l
        return txt

    def resizeEvent(self, e):
        QtGui.QPlainTextEdit.resizeEvent(self, e)
        #self.ensureCursorVisible()
        return
        
    def mousePressEvent(self, e):
        QtGui.QPlainTextEdit.mousePressEvent(self, e)

    def mouseReleaseEvent(self, e):
        QtGui.QPlainTextEdit.mouseReleaseEvent(self, e)
        cursor = self.textCursor()
        if cursor.columnNumber > 4 and cursor.position() > self._commandCursorPos:
            self.setLastCursorPos()
        if e.button() == QtCore.Qt.LeftButton:
            self.copy()
        elif e.button() == QtCore.Qt.MidButton:
            self.paste()
        #if self.textCursor().position() < self._editCursorPos: #.position():
        #    cursor = self.textCursor()
        #    if self._lastCursorPos:
        #        cursor.setPosition(self._lastCursorPos) #.position())
        #    self.setTextCursor(cursor)
        e.accept()

    def paste(self):
        if self._inReadline:
            return
        cursor = self.textCursor()
        cursor.setPosition(self._lastCursorPos)
        self.setTextCursor(cursor)
        lines = unicode(QtGui.qApp.clipboard().text())
        for line in lines.splitlines(True):
            line = self.pstrip.sub('', line)
            enter = self.penter.search(line)
            self.textCursor().insertText(line)
            self.setLastCursorPos()
            if enter and not self._inReadline:
                self.commandParse()
            self.ensureCursorVisible()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    console = ConsoleWidget()
    console.show()
    sys.exit(app.exec_())

        
#keywords
#topics
