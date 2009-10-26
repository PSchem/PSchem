from PyQt4 import QtCore, QtGui
import os, sys

class ConsoleWidget(QtGui.QPlainTextEdit):
    def __init__(self, window):
        QtGui.QPlainTextEdit.__init__(self)
        #self.viewport = ConsoleViewport()
        #self.setViewport(self._viewport)
        self.window = window
        #self.setFontFamily("Courier")
        self.eofKey = QtCore.Qt.Key_D
        self.line = QtCore.QString()
        self.point = 0

        self.document().installEventFilter(self)
        self.viewport().installEventFilter(self)
        self.installEventFilter(self)
        #self.setReadOnly(True)

        sys.stderr.write(str(self.textCursor()))
        self.consoleCursor = ConsoleCursor(self.document())
        self.setTextCursor(self.consoleCursor)
        #self.setTextCursor(self.textCursor())
        sys.stderr.write(str(self.textCursor()))



        # font
        if os.name == 'posix':
            font = QtGui.QFont("Monospace", 10)
        elif os.name == 'nt' or os.name == 'dos':
            font = QtGui.QFont("Courier New", 8)
        else:
            raise SystemExit, "FIXME for 'os2', 'mac', 'ce' or 'riscos'"
        font.setFixedPitch(1)
        self.setFont(font)
        #self.connect(self, QtCore.SIGNAL("textChanged()"), self.has_changed)


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
        text = str(self.edit.text())
        self.window.controller.parse(text)
        self.edit.clear()

    def write(self, text):

        cursor = self.textCursor()

        cursor.movePosition(QtGui.QTextCursor.End)

        pos1 = cursor.position()
        cursor.insertText(text)

        self.cursor_pos = cursor.position()
        self.setTextCursor(cursor)
        self.ensureCursorVisible ()

        # Set the format
        cursor.setPosition(pos1, QtGui.QTextCursor.KeepAnchor)
        format = cursor.charFormat()
        format.setForeground(QtGui.QBrush(QtCore.Qt.black))
        #format.setFont(self.font)
        cursor.setCharFormat(format)

    def writeErr(self, text):
        self.write(text)

    def writelines(self, text):
        map(self.write, text)


#    def write(self, txt):
#        if (txt != "\n"):
#            self.console.append(txt)


    def readline(self):
        self.reading = 1
        self.__clear_line()
        self.moveCursor(QtGui.QTextCursor.End)
        while self.reading:
        #    #pass
        #    #QtGui.qApp.processOneEvent()
            QtGui.qApp.processEvents() #QtCore.QEventLoop.ExcludeUserInputEvents)
        #    #QtCore.QCoreApplication.processOneEvent()
        if self.line.length() == 0:
            return '\n'
        else:
            return str(self.line)

    def keyPressEvent(self, event):
        text  = event.text()
        key   = event.key()
        modifier = event.modifiers()
        #print modifier
        #print dir(modifier)

        if (key == QtCore.Qt.Key_Control and modifier & QtCore.Qt.ControlModifier):
            pass
        elif key == QtCore.Qt.Key_Backspace:
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
            self.write('\n')
            self.reading = 0
#            if self.reading:
#                self.reading = 0
#            else:
            self.pointer = 0
            self.window.controller.parse(str(self.line))
            self.__clear_line()
                
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
            QtGui.QPlainTextEdit.keyPressEvent(self, event)
#            event.ignore()

    def __insert_text(self, text):
        """
        Insert text at the current cursor position.
        """

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

    def mousePressEvent(self, e):
        """
        Keep the cursor after the last prompt.
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.moveCursor(QtGui.QTextCursor.End)
        if e.button() == QtCore.Qt.MidButton:
            self.moveCursor(QtGui.QTextCursor.End)
        return

    def paste(self):
        sys.stderr.stream.write('paste\n')
        self.moveCursor(QtGui.QTextCursor.End)
        QtGui.QPlainTextEdit.keyPressEvent(self, event)
        

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

class ConsoleViewport(QtGui.QScrollArea):
    def __init__(self):
        QtGui.QScrollArea.__init__(self)

class ConsoleCursor(QtGui.QTextCursor):
    def __init__(self, document):
        QtGui.QTextCursor.__init__(self, document)
        print '+'

    def insertText(text):
        #print '+' + text + '+'
        QtGui.QTextCursor.insertText('+' + text + '+')
