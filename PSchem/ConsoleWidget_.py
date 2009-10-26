from PyQt4 import QtCore, QtGui

class ConsoleWidget(QtGui.QWidget):
    def __init__(self, controller):
        QtGui.QWidget.__init__(self)
        self.layout = QtGui.QVBoxLayout()
        self.hlayout = QtGui.QHBoxLayout()
        self.console = QtGui.QTextEdit()
        self.console.setFontFamily("Courier")
        self.console.setReadOnly(True)
        self.edit = QtGui.QLineEdit()
        self.enter = QtGui.QPushButton("Enter")
        self.clear = QtGui.QPushButton("Clear")
        self.hlayout.addWidget(self.edit)
        self.hlayout.addWidget(self.enter)
        self.hlayout.addWidget(self.clear)
        self.layout.addWidget(self.console)
        self.layout.addLayout(self.hlayout)
        self.setLayout(self.layout)

        self.connect(self.edit, QtCore.SIGNAL("returnPressed()"),
                     self.textParse)
        self.connect(self.enter, QtCore.SIGNAL("released()"),
                     self.textParse)
        self.connect(self.clear, QtCore.SIGNAL("released()"),
                     self.edit.clear)
        self.controller = controller


    def error(self, message):
        fmt = self.console.currentCharFormat()
        self.console.setFontWeight(QtGui.QFont.Bold)
        self.console.setTextColor(QtGui.QColor(255, 0, 0))
        self.console.append(message)
        self.console.setCurrentCharFormat(fmt)


    def command(self, message):
        fmt = self.console.currentCharFormat()
        self.console.setFontWeight(QtGui.QFont.Bold)
        self.console.append(">>> " + message)
        self.console.setCurrentCharFormat(fmt)

    def textParse(self):
        text = str(self.edit.text())
        self.controller.parse(text)
        self.edit.clear()

    def write(self, text):
        """
        Simulate stdin, stdout, and stderr.
        """
        # The output of self.append(text) contains to many newline characters,
        # so work around QTextEdit's policy for handling newline characters.

        cursor = self.edit.textCursor()

        cursor.movePosition(QTextCursor.End)

        pos1 = cursor.position()
        cursor.insertText(text)

        self.cursor_pos = cursor.position()
        self.edit.setTextCursor(cursor)
        self.edit.ensureCursorVisible ()

        # Set the format
        cursor.setPosition(pos1, QtGui.QTextCursor.KeepAnchor)
        format = cursor.charFormat()
        format.setForeground(QtGui.QBrush(Qt.black))
        format.setFont(self.font)
        cursor.setCharFormat(format)

#    def write(self, txt):
#        if (txt != "\n"):
#            self.console.append(txt)


