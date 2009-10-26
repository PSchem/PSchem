# -*- coding: utf-8 -*-
import re
from ConsoleWidget import *

class Command():
    def __init__(self, commandStr):
        self._str = commandStr
        self._compiled = None
        
    def compiled(self):
        if (not self._compiled):
            self._compiled = compile(self._str, "console", "single")
        return self._compiled
        
    def str(self):
        return self._str

class Controller():
    pstrip = re.compile(r'^(>>> |\.\.\. )?')
    pfirst = re.compile(r'^\S+.*\:$')
    pindented = re.compile(r'^\s+.*$')

    def __init__(self, window):
        self.window = window
        self.locals = locals()
        self.globals = globals()
        self.oldStr = ''
        self.firstLine = True

        print self.pythonInfo()
        print self.prompt1()

    def pythonInfo(self):
        return 'Python %s on %s\n' % (sys.version, sys.platform) + \
            'Type "help", "copyright", "credits" or "license" for more information.\n'


    def execute(self, cmd):
        print self.prompt1() + cmd.str()
        exec (cmd.compiled(), self.globals, self.locals)

    def executeOld(self, cmd):
        exec (cmd, self.globals, self.locals)

    def prompt1(self):
        return '>>> '

    def prompt2(self):
        return '... '

    def parse(self, text, eval=True):
        text = Controller.pstrip.sub('', text)
        print ">>> " + text
        #sys.stderr.stream.write(text + '\n')
        first = Controller.pfirst.search(text)
        indented = Controller.pindented.search(text)
        if self.firstLine:
            #print ">>> " + text
            if first:
                self.firstLine = False
                self.oldStr = text + "\n"
                #print self.prompt2()
            elif (text != ''):
                if eval:
                    self.executeOld(compile(text, "console", "single"))
                #print self.prompt1()
            else:
                pass
                #print self.prompt1()
        else:
            #print "... " + text
            if indented:
                self.oldStr += text + "\n"
                print self.prompt2()
            else:
                self.firstLine = True
                #print self.oldStr
                if eval:
                    self.executeOld(compile(self.oldStr, "console", "exec"))
                if (text != ''):
                    self.parse(text)

