# -*- coding: utf-8 -*-

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

import sys
from PyQt4 import QtCore, QtGui

try:
    from PSchem.Controller import Command
except ImportError:
    pass

import os
import time
import re

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
        self.stream.write(txt)

    def isatty(self):
        return True

class StderrWrap():
    def __init__(self, console):
        self.console = console
        self.stream = sys.stderr

    def write(self, txt):
        self.console.writeErr(txt)
        self.stream.write(txt)

    def isatty(self):
        return True

class History():    
    def __init__(self):
        self.pointer = 0
        self.history = []
        
    def push(self, cmd):
        self.history.append(cmd)
        self.pointer = -1

    def pop(self):
        self.pointer = -1
        if (len(self.history) > 0):
            return self.history.pop()
        else:
            return ''

    def isTop(self):
        return (self.pointer == -1)

    def back(self):
        if (self.pointer > -len(self.history)):
            self.pointer -= 1
        return self.history[self.pointer]

    def forward(self):
        if (self.pointer < -1):
            self.pointer += 1
        return self.history[self.pointer]

class ConsoleWidget(QtGui.QPlainTextEdit):
    pstrip = re.compile(r'^(>>> |\.\.\. |--- )?')

    NUL  = 000 # ignored
    ENQ  = 005 # trigger answerback message
    BEL  = 007 # beep
    BS   = 010 # backspace one column
    HT   = 011 # horizontal tab to next tab stop
    LF   = 012 # line feed
    VT   = 013 # line feed
    FF   = 014 # line feed
    CR   = 015 # carriage return
    S0   = 016 # activate G1 character set & newline
    SI   = 017 # activate G0 character set
    XON  = 021 # resume transmission
    XOFF = 023 # stop transmission, ignore characters
    CAN  = 030 # interrupt escape sequence
    SUB  = 032 # interrupt escape sequence
    ESC  = 033 # start escape sequence
    DEL  = 177 # ignored
    CSI  = 233 # equivalent to ESC [


    keyCtrlCodes = {
        QtCore.Qt.Key_A : '\x01',
        QtCore.Qt.Key_B : '\x02',
        QtCore.Qt.Key_E : '\x05',
        QtCore.Qt.Key_J : '\x0a',
        QtCore.Qt.Key_Enter : '\x0a',
        QtCore.Qt.Key_M : '\x0d',
        QtCore.Qt.Key_N : '\x0e',
        QtCore.Qt.Key_O : '\x0f',
        QtCore.Qt.Key_P : '\x10',
        QtCore.Qt.Key_Q : '\x11',
        QtCore.Qt.Key_R : '\x12',
        QtCore.Qt.Key_S : '\x13',
        QtCore.Qt.Key_Y : '\x15',
        QtCore.Qt.Key_V : '\x16',
        QtCore.Qt.Key_W : '\x17',
        QtCore.Qt.Key_X : '\x18',
        QtCore.Qt.Key_Z : '\x1a',
        QtCore.Qt.Key_BracketLeft : '\x1b',
        QtCore.Qt.Key_BracketRight : '\x1d',
        }

    def __init__(self, window=None):
        QtGui.QPlainTextEdit.__init__(self)

        self.inHistory = False
        self.history = History()
        #self.setReadOnly(True)
        #self.window = window
        self.window = None
        self.buffer = u''
        self._asynchCursor = None
        self._synchronous = False

        # font
        self.defaultFormat = self.currentCharFormat()
        self.defaultFormat.setFontFamily("Courier")
        self.defaultFormat.setFontFixedPitch(True)
        self.setCurrentCharFormat(self.defaultFormat)
        
        #p = self.palette();
        #p.setColor(QtGui.QPalette.Base, QtCore.Qt.black);
        #p.setColor(QtGui.QPalette.Text, QtCore.Qt.white);
        #self.setPalette(p);
        
        self.eofKey = QtCore.Qt.Key_D
        self.line = QtCore.QString()
        self.point = 0
        
        sys.stdout = StdoutWrap(self)
        #sys.stderr = StderrWrap(self)
        sys.stdin = StdinWrap(self)

        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.trUtf8('Copy'), self.copy)
        self.menu.addAction(self.trUtf8('Paste'), self.paste)
        #self.menu.addSeparator()

    def contextMenuEvent(self,ev):
        """
        Reimplemented to show our own context menu.
        
        @param ev context menu event (QContextMenuEvent)
        """
        self.menu.popup(ev.globalPos())
        ev.accept()

    def error(self, message):
        fmt = self.currentCharFormat()
        self.setFontWeight(QtGui.QFont.Bold)
        self.setTextColor(QtGui.QColor(255, 0, 0))
        self.append(message)
        self.setCurrentCharFormat(fmt)

    def command(self, message):
        fmt = self.currentCharFormat()
        self.setFontWeight(QtGui.QFont.Bold)
        self.append(">>> " + message)
        self.setCurrentCharFormat(fmt)

    def textParse(self):
        #text = str(self.edit.text())
        text = str(self.edit.toPlainText())
        #print dir(text)
        #print text
        command = Command(text)
        if self.window:
            self.window.controller.execute(command)
        self.history.push(command)
        #self.window.controller.parse(text)
        #self.history.push(text)
        #self.edit.clear()

    def setSynchronous(self, synchronous, markPos = False):
        if markPos:
            self._asynchCursor = self.textCursor().position()
        self._synchronous = synchronous

    def write(self, txt):
        #if (txt != "\n"):
        if self._synchronous or not self._asynchCursor:
            self.moveCursor(QtGui.QTextCursor.End)
            self.textCursor().insertText(txt, self.defaultFormat)
        else:
            cursor = self.textCursor()
            cursor.setPosition(self._asynchCursor)
            self.setTextCursor(cursor)
            self.textCursor().insertText(txt, self.defaultFormat)
            self._asynchCursor = self.textCursor().position()
        #self.console.append(txt)
        self.moveCursor(QtGui.QTextCursor.End)
        self.ensureCursorVisible()


    def writeErr(self, txt):
        #frmt = QtGui.QTextCharFormat()
        self.moveCursor(QtGui.QTextCursor.End)
        frmt = QtGui.QTextCharFormat(self.defaultFormat)
        frmt.setForeground(QtGui.QBrush(QtCore.Qt.red))
        self.textCursor().insertText(txt, frmt)
        self.ensureCursorVisible()

    #def resizeEvent(self, ev):
        #self.edit.setMaximumHeight(ev.size().height()-100)
        #QtGui.QWidget.resizeEvent(self, ev)
    def readline(self):
        #self.reading = 1
        #self.__clear_line()
        #self.moveCursor(QtGui.QTextCursor.End)
        #while self.reading:
        ##    #pass
        ##    #QtGui.qApp.processOneEvent()
        #    QtGui.qApp.processEvents() #QtCore.QEventLoop.ExcludeUserInputEvents)
        ##    #QtCore.QCoreApplication.processOneEvent()
        #if self.line.length() == 0:
        #    return '\n'
        text = u''
        while True:
            QtGui.qApp.processEvents()
            char = self.read(1)
            if len(char) > 0:
                self.setSynchronous(True)
                sys.stdout.write(char)
                self.setSynchronous(False)
                text = text + unicode(char)
                #print '\'' + text + '\'\n'
                if char == '\n':
                    break 
        return text
            

    def read(self, count=1, acc=''):
        if acc == '':
            self.buffer = self.pstrip.sub('', self.buffer)
        lenBuf = len(self.buffer)
        if lenBuf >= count:
            str = acc + self.buffer[0:count]
            self.buffer = self.buffer[count:lenBuf]
            return str
        else:
            str = acc + self.buffer
            self.buffer = u''
            time.sleep(0.01)
            return str
            #self.read(count - len(str), str)
            
    def parseInput(self, text):
        self.buffer = self.buffer + unicode(text)
        #self.write(str)
            
    def keyPressEvent(self, event):
        text  = event.text()
        key   = event.key()
        modifier = event.modifiers()
        #print modifier
        #print dir(modifier)

        if (key == QtCore.Qt.Key_Control and modifier & QtCore.Qt.ControlModifier):
            pass
        #if (modifier & QtCore.Qt.ControlModifier):
        #    if key in self.keyCtrlCodes:
        #        self.parseInput(self.keyCtrlCodes[key])
                

        if key == QtCore.Qt.Key_Backspace:
            if self.point:
                cursor = self.textCursor()
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter,
                                    QtGui.QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                self.color_line()
            
                self.point -= 1 
                self.line.remove(self.point, 1)

        elif key == QtCore.Qt.Key_Delete:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.NextCharacter,
                                QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self.color_line()
                        
            self.line.remove(self.point, 1)
            
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.parseInput('\n')
            #self.write('\n')
            #self.reading = 0
#            if self.reading:
#                self.reading = 0
#            else:
            #self.pointer = 0
            #if self.window:
            #    self.window.controller.parse(str(self.line))
            #self.__clear_line()
                
        elif True:
            self.parseInput(event.text())
        elif key == QtCore.Qt.Key_Tab:
            self.__insert_text(text)
        elif key == QtCore.Qt.Key_Left:
            if self.point : 
                self.moveCursor(QtGui.QTextCursor.Left)
                self.point -= 1 
        elif key == QtCore.Qt.Key_Right:
            if self.point < self.line.length():
                self.moveCursor(QtGui.QTextCursor.Right)
                self.point += 1 

        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor ()
            cursor.setPosition(self.cursor_pos)
            self.setTextCursor (cursor)
            self.point = 0

        elif key == QtCore.Qt.Key_End:
            self.moveCursor(QtGui.QTextCursor.EndOfLine)
            self.point = self.line.length()

#        elif key == QtCore.Qt.Key_Up:
#            if len(self.history):
#                if self.pointer == 0:
#                    self.pointer = len(self.history)
#                self.pointer -= 1
#                self.__recall()
#                
#        elif key == QtCore.Qt.Key_Down:
#            if len(self.history):
#                self.pointer += 1
#                if self.pointer == len(self.history):
#                    self.pointer = 0
#                self.__recall()

        elif text.length():
            self.__insert_text(text)
            return
        else:
            self.parseInput(event.text())
        #else:
        #    QtGui.QPlainTextEdit.keyPressEvent(self, event)
#            event.ignore()

    def __insert_text(self, text):
        """
        Insert text at the current cursor position.
        """

        self.moveCursor(QtGui.QTextCursor.End)
        self.line.insert(self.point, text)
        self.point += text.length()

        cursor = self.textCursor()
        cursor.insertText(text)
        self.color_line()

    def color_line(self):
        pass

    def __clear_line(self):
        """
        Clear input line buffer
        """
        self.line.truncate(0)
        self.point = 0

    def mouseReleaseEvent(self, e):
        """
        Keep the cursor after the last prompt.
        """
        QtGui.QPlainTextEdit.mousePressEvent(self, e)
        if e.button() == QtCore.Qt.LeftButton:
            self.copy()
    #        self.moveCursor(QtGui.QTextCursor.End)
        if e.button() == QtCore.Qt.MidButton:
            self.paste()
    #        self.moveCursor(QtGui.QTextCursor.End)
        e.accept()

    def paste(self):
        lines = unicode(QtGui.qApp.clipboard().text())
        self.parseInput(lines)
        #self.write(lines)

    def eventFilter(self, obj, ev):
        #sys.stderr.stream.write(str(obj)+ ' '+ str(ev) + '\n')
        if isinstance(ev, QtGui.QMouseEvent):
            if (int(ev.buttons()) & QtCore.Qt.MidButton):
                sys.stderr.stream.write(str(int(ev.buttons())) + '\n')
                self.midButtonPressed = True
                return False
            if (int(ev.buttons()) == 0 and self.midButtonPressed):
                self.midButtonPressed = False
                #self.moveCursor(QtGui.QTextCursor.End)
                #self.paste()
                return False
        #print obj
        #print ev
        return False

        
    def historyPrev(self):
        if (not self.inHistory):
            command = Command(str(self.edit.toPlainText()))
            self.history.push(command)
        self.inHistory = True
        cmd = self.history.back()
        #self.edit.setPlainText(cmd.str())

    def historyNext(self):
        if (self.inHistory):
            if (self.history.isTop()):
                self.inHistory = False
                cmd = self.history.pop()
            else:
                cmd = self.history.forward()
            #self.edit.setPlainText(cmd.str())


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    console = ConsoleWidget()
    console.show()
    sys.exit(app.exec_())

        