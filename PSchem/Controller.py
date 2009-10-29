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

import re
from PSchem.ConsoleWidget import *
import sys, traceback

class Command():
    #pstrip = re.compile(r'\n$')
    def __init__(self, commandStr, type = 'single'):
        self._text = commandStr
        self._type = type
        self._compiled = None
        
    def compiled(self):
        if (not self._compiled):
            self._compiled = compile(self._text, "console", self._type)
        return self._compiled
        
    def text(self):
        #text = Controller.pstrip.sub('', self._str)
        return self._text

class Controller():
    pstrip = re.compile(r'^(>>> |\.\.\. |--- )?')
    pfirst = re.compile(r'^\S+.*\:$')
    pempty = re.compile(r'^\s*$')
    pindented = re.compile(r'^\s+.*$')

    def __init__(self, window):
        self.window = window
        self.locals = locals()
        self.globals = globals()
        self.oldStr = ''
        self.firstLine = True
        
        self._indent = False
        self._cmd = u''

        print self.pythonInfo()
        #print self.prompt1()
        
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '

        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '

        sys.stdout.writeSync(sys.ps1, True)

    def pythonInfo(self):
        return 'Python %s on %s\n' % (sys.version, sys.platform) + \
            'Type "help", "copyright", "credits" or "license" for more information.\n'


    def execute(self, cmd, echo = True):
        if echo:
            sys.stdout.write('--- ' + cmd.text() + '\n')
        exec (cmd.compiled(), self.globals, self.locals)

    def parse(self, cmd):
        #sys.stdout.writeSync(sys.ps1, True)
        line = cmd.text()
        line = self.pstrip.sub('', line)
        empty = self.pempty.search(line)
        #self._indent = self.pfirst.search(line)
        if self._indent:
            if line == '\n':
                self._indent = False
                self.window.consoleWidget.setSynchronous(True)
                try:
                    self.execute(Command(self._cmd, 'exec'), False)
                except (StandardError) as err:
                    print traceback.format_exc()
                self.window.consoleWidget.setSynchronous(False)
                sys.stdout.writeSync(sys.ps1, True)
            else:
                sys.stdout.writeSync(sys.ps2)
                self._cmd = self._cmd + line
        else:
            first = self.pfirst.search(line)
            self._cmd = line
            if first:
                sys.stdout.writeSync(sys.ps2)
                self._indent = True
            else:
                if not empty:
                    self.window.consoleWidget.setSynchronous(True)
                    try:
                        self.execute(Command(self._cmd), False)
                    except (StandardError) as err:
                        print traceback.format_exc()
                        #print err
                    self.window.consoleWidget.setSynchronous(False)
                sys.stdout.writeSync(sys.ps1, True)
                
