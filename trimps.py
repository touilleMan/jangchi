#! /usr/bin/env python

import sys, os
from PyQt4 import QtCore, QtGui, uic
from program import Program
import tempfile

COMPILER="ressources/gopiler"
DEFAULT_SRC="ressources/linetracer.asm"

class Ui(QtGui.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.ui = uic.loadUi('mainwindow.ui', self)
        self.ui.button_run.clicked.connect(self.run)
        self.ui.button_clear.clicked.connect(self.ui.widget_world.clear)
        self.ui.show()
        with open(DEFAULT_SRC) as fd:
            self.ui.textEdit_source.setPlainText(fd.read())
        # Compilation stuff
        self.compile_out_bin = None
        self.compile_out_vhdl = ""
        self.ui.button_compile.clicked.connect(self.update_compile)
        # Program is not started at the beginning
        self.program = Program(self.ui.widget_world.image)
        self.program_timer = QtCore.QTimer(self)
        self.program_timer.timeout.connect(self.program.update)
        self.program_running = False
        # Don't forget to connect the robot to the Qt world
        self.ui.widget_world.robot = self.program.robot

    def update_compile(self):
        self.compile('binary')
        self.compile('vhdl')

    def compile(self, out_type="binary"):
        """Compile the input and set the vhdl and binary
           out_type : compilation type (vhdl, binary)
        """
        err_file = tempfile.mktemp()
        output_file = tempfile.mktemp()
        input_file = tempfile.mktemp()
        # Create the compilation line with the input files
        cmd_line = COMPILER + " -type=" + out_type + " -b=0x0 -o " + output_file + " " + input_file + "\n"
        self.ui.textEdit_console.appendPlainText(cmd_line)

        with open(input_file, "w") as ifd:
            ifd.write(self.ui.textEdit_source.toPlainText())
        # Compilation line
        out = os.system("2>" + err_file + " " + cmd_line)
        # Check return code
        if out == 0:
            self.ui.textEdit_console.appendPlainText("\nCompilation done !\n")
            if out_type is "vhdl":
                # Update the vhdl output window
                with open(output_file, "rb") as ofd:
                    self.ui.textEdit_vhdl.setPlainText(ofd.read())
            else:
                # Load the binary in the robot
                self.program.cpu.load(output_file)
        else:
            with open(err_file, "r") as efd:
                self.ui.textEdit_console.appendPlainText(efd.read())

    def run(self):
        """Create the program and connect a timer to run it
           If the program is already started, stop it
        """
        if not self.program_running:
            self.program_timer.start(self.program.synchronise_step * 1000)
        else:
            self.program_timer.stop()
        self.program_running = not self.program_running


if __name__ == '__main__':
    # Create the Ui
    app = QtGui.QApplication(sys.argv)
    w = Ui()
    sys.exit(app.exec_())
