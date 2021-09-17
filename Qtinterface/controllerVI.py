# GUI control of Numato 32-relay USB board
# using PyQt5 and Pyserial

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
pg.setConfigOption('background','w') # set background default to white
pg.setConfigOption('antialias',True)

import time
import traceback, sys

class WorkerSignals(QObject):
    '''defines signals from running worker thread
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Worker(QRunnable):
    '''worker thread
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        self.kwargs['results'] = self.signals.result

    @pyqtSlot()
    def run(self):
        '''initialise runner function with passed args, kwargs
        '''
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MainWindow(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        self.setWindowTitle("Numato relay board controller")
        self.setFixedSize(800,600)

        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        buttons = {'0': (0, 0),
                   '1': (0, 1),
                   '2': (0, 2),
                   '3': (0, 3),
                   '4': (0, 4),
                   '5': (0, 5),
                   '6': (0, 6),
                   '7': (0, 7),
                   '8': (1, 0),
                   '9': (1, 1),
                   'A': (1, 2),
                   'B': (1, 3),
                   'C': (1, 4),
                   'D': (1, 5),
                   'E': (1, 6),
                   'F': (1, 7),
                   'G': (2, 0),
                   'H': (2, 1),
                   'I': (2, 2),
                   'J': (2, 3),
                   'K': (2, 4),
                   'L': (2, 5),
                   'M': (2, 6),
                   'N': (2, 7),
                   'O': (3, 0),
                   'P': (3, 1),
                   'Q': (3, 2),
                   'R': (3, 3),
                   'S': (3, 4),
                   'T': (3, 5),
                   'U': (3, 6),
                   'V': (3, 7)
                  }

        INPUT = '0000'+'0000'+'0000'+'0000'+'0000'+'0000'+'0000'+'0000'
        inputhex = hex(int(INPUT,2))[2:].zfill(8)
        self.A = str(bin(int(inputhex, 16)))[2:].zfill(32)

        INPUT = '1111'+'1111'+'1111'+'1111'+'1111'+'1111'+'1111'+'1111'
        inputhex = hex(int(INPUT,2))[2:].zfill(8)
        self.B = str(bin(int(inputhex, 16)))[2:].zfill(32)

        self._createDisplayBin()
        self._createDisplayHex()
        self._createButtons(buttons)
        self._createStateButton()
        self._createInputField()
        self._createSelectorButtons()
        self._createStartButton()
        self._createStatusField()

        self.show()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.getButtonsState()

    # Auxilary functions

    def _createStateButton(self):
        self.l = QPushButton("Set state")
        self.l.pressed.connect(self.setButtonsState) # when button pressed, set state
        self.generalLayout.addWidget(self.l)   
    def _createStartButton(self):
        self.horizonLayout = QHBoxLayout()
        b1 = QPushButton("Start routine 1")
        b1.pressed.connect(self.runfunction1) # when button pressed, runfunction: this starts an asynchronous loop inside the main loop
        b2 = QPushButton("Start routine 2")
        b2.pressed.connect(self.runfunction2) # when button pressed, runfunction: this starts an asynchronous loop inside the main loop
        b3 = QPushButton("Start routine 3")
        b3.pressed.connect(self.runfunction3) # when button pressed, runfunction: this starts an asynchronous loop inside the main loop
        b4 = QPushButton("Start routine 4")
        b4.pressed.connect(self.runfunction4) # when button pressed, runfunction: this starts an asynchronous loop inside the main loop
        self.bc = QLabel("Command")
        self.horizonLayout.addWidget(b1)
        self.horizonLayout.addWidget(b2)
        self.horizonLayout.addWidget(b3)
        self.horizonLayout.addWidget(b4)
        self.horizonLayout.addWidget(self.bc)
        self.generalLayout.addLayout(self.horizonLayout)  
    def _createInputField(self):
        self.horizonLayout = QHBoxLayout()
        self.label = QLabel("Input:")
        self.label.setFixedWidth(120)        
        self.k = QLineEdit()
        self.k.setText(self.A)
        self.horizonLayout.addWidget(self.label)
        self.horizonLayout.addWidget(self.k)
        self.generalLayout.addLayout(self.horizonLayout)
    def _createStatusField(self):
        self.horizonLayout = QHBoxLayout()
        self.label = QLabel("Status:")
        self.label.setFixedWidth(120)   
        self.b4 = QLineEdit()
        self.b4.setText('OK')
        self.horizonLayout.addWidget(self.label)
        self.horizonLayout.addWidget(self.b4)
        self.generalLayout.addLayout(self.horizonLayout)
    def _createDisplayBin(self):
        self.horizonLayout = QHBoxLayout()
        self.label = QLabel("Binary command:")
        self.label.setFixedWidth(120)   
        self.displayBin = QLineEdit()
        self.displayBin.setFixedHeight(35)
        self.displayBin.setAlignment(Qt.AlignRight)
        self.displayBin.setReadOnly(True)
        self.horizonLayout.addWidget(self.label)
        self.horizonLayout.addWidget(self.displayBin)
        self.generalLayout.addLayout(self.horizonLayout)
    def _createDisplayHex(self):
        self.horizonLayout = QHBoxLayout()
        self.label = QLabel("Hex command:")
        self.label.setFixedWidth(120)   
        self.displayHex = QLineEdit()
        self.displayHex.setFixedHeight(35)
        self.displayHex.setAlignment(Qt.AlignRight)
        self.displayHex.setReadOnly(True)
        self.horizonLayout.addWidget(self.label)
        self.horizonLayout.addWidget(self.displayHex)
        self.generalLayout.addLayout(self.horizonLayout)
    def _createSelectorButtons(self):
        self.horizonLayout = QHBoxLayout()
        self.ll = QPushButton("All on")
        self.ll.pressed.connect(lambda: self.writeInputCommand(self.B)) # when button pressed, set state
        self.ll.pressed.connect(self.setButtonsState) # when button pressed, set state
        self.lll = QPushButton("All off")
        self.lll.pressed.connect(lambda: self.writeInputCommand(self.A)) # when button pressed, set state
        self.lll.pressed.connect(self.setButtonsState) # when button pressed, set state
        self.horizonLayout.addWidget(self.ll)
        self.horizonLayout.addWidget(self.lll)
        self.generalLayout.addLayout(self.horizonLayout) 
    def _createButtons(self,buttons):
        self.buttons = {}
        buttonsLayout = QGridLayout()

        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            self.buttons[btnText].setFixedSize(60,60)
            self.buttons[btnText].setCheckable(True)
            self.buttons[btnText].clicked.connect(self.getButtonsState) # when button clicked, get state
            buttonsLayout.addWidget(self.buttons[btnText], pos[0], pos[1])
        self.generalLayout.addLayout(buttonsLayout)

    # slots

# Must not let multiple routines start in parallel
    def runfunction1(self):
        worker = Worker(self.executefn1) # instantiate the Runnable subclass 
        worker.signals.result.connect(self.action) # print the output each time a result comes in
        worker.signals.finished.connect(self.thread_complete) # then run thread complete
        # Execute
        self.threadpool.start(worker) # start 
    def runfunction2(self):
        worker = Worker(self.executefn2) # instantiate the Runnable subclass 
        worker.signals.result.connect(self.action) # print the output each time a result comes in
        worker.signals.finished.connect(self.thread_complete) # then run thread complete
        # Execute
        self.threadpool.start(worker) # start 
    def runfunction3(self):
        worker = Worker(self.executefn3) # instantiate the Runnable subclass 
        worker.signals.result.connect(self.action) # print the output each time a result comes in
        worker.signals.finished.connect(self.thread_complete) # then run thread complete
        # Execute
        self.threadpool.start(worker) # start 
    def runfunction4(self):
        worker = Worker(self.executefn4) # instantiate the Runnable subclass 
        worker.signals.result.connect(self.action) # print the output each time a result comes in
        worker.signals.finished.connect(self.thread_complete) # then run thread complete
        # Execute
        self.threadpool.start(worker) # start 

    # Experimental routines programmed here
    def executefn1(self,results):
        for i in range(10):
            results.emit('A')
            time.sleep(1)
            results.emit('B')
            time.sleep(2)

    def executefn2(self,results):
        for i in range(10):
            results.emit('A')
            time.sleep(1)
            results.emit('B')
            time.sleep(2)

    def executefn3(self,results):
        for i in range(10):
            results.emit('A')
            time.sleep(1)
            results.emit('B')
            time.sleep(2)

    def executefn4(self,results):
        for i in range(10):
            results.emit('A')
            time.sleep(1)
            results.emit('B')
            time.sleep(2)

    def thread_complete(self):
        print("Thread complete!")

    # Commands programmed here
    def action(self,results):
        if results=='A':
            self.bc.setText(results) # update text box
            self.writeInputCommand(self.A)
            self.setButtonsState()
        elif results=='B':
            self.bc.setText(results) # update text box
            self.writeInputCommand(self.B)
            self.setButtonsState()

    def getButtonsState(self):
        # read state of buttons and display bin/Hex
        state = []
        for btnText, pos in self.buttons.items():
            state.append(int(self.buttons[btnText].isChecked()))
        binstring = ''.join(['1' if x else '0' for x in state])
        self.displayBin.setText(binstring)
        self.displayBin.setFocus()
        hexstring = hex(int(binstring,2))[2:].zfill(8)
        self.displayHex.setText(hexstring)
        self.displayHex.setFocus()
        self.b4.setText('OK')

# Must do proper error checking here
    def setButtonsState(self):
        # set buttons according to state specified in k 
        inputs = self.k.text()
        if len(inputs)!=32:
            self.b4.setText('Error! Require 32-bit binary input')
            self.k.setText(self.A)
        else:    
            j = 0
            for btnText, pos in self.buttons.items():
                self.buttons[btnText].setChecked(bool(int(inputs[j]))) 
                j+=1
            self.getButtonsState()
            self.b4.setText('OK')

    def writeInputCommand(self,inputs):
        # write programmatically defined inputs to k
        self.k.setText(inputs)


def main():
    # here is the app running
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__=='__main__':
    main()

