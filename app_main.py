import sys
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtCore import QThreadPool, Signal
from queue import Queue
from ui_newCNC import Ui_MainWindow  # convert like this: pyside2-uic newCNC.ui > ui_newCNC.py
""" Custom imports """
from serial_thread import SerialWorker
from controller_thread import ControllerWorker
from style_manager import StyleManager
from visual_manager import VisualLayer
from ui_manager import UiManager


class MainWindow(QMainWindow, Ui_MainWindow):
    serialRxQu = Queue()                   # serial FIFO RX Queue
    serialTxQu = Queue()                   # serial FIFO TX Queue
    finish_thread = Signal()

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.connection_status = False
        self.last_open_dir = "."

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.vl = VisualLayer(self.ui.viewCanvasWidget)
        self.ui.refreshButton.clicked.connect(self.handle_refresh_button)
        self.ui.connectButton.clicked.connect(self.handle_connect_button)
        self.ui.unlockButton.clicked.connect(self.handle_unlock)
        self.ui.homingButton.clicked.connect(self.handle_homing)
        self.ui.xMinusButton.clicked.connect(self.handle_x_minus)
        self.ui.clearTerminalButton.clicked.connect(self.handle_clear_terminal)
        self.ui.send_text_edit.returnPressed.connect(self.send_input)
        self.ui.send_text_edit.setPlaceholderText('input here')
        self.ui.send_push_button.clicked.connect(self.send_input)
        self.ui.send_text_edit.hide()
        self.ui.send_push_button.hide()
        self.ui.actionHide_Show_Console.triggered.connect(self.hide_show_console)

        # Control Worker Thread, started as soon as the thread pool is started.
        self.controlWo = ControllerWorker(self.serialRxQu, self.serialTxQu, self.ui, self.vl)

        # Serial Worker Thread, started with the first connection to serial port.
        self.serialWo = SerialWorker(self.serialRxQu, self.serialTxQu, self.ui.textEdit)

        self.finish_thread.connect(self.controlWo.terminate_thread)
        self.finish_thread.connect(self.serialWo.terminate_thread)

        self.ui_manager = UiManager(self, self.ui, self.controlWo)
        self.threadpool = QThreadPool()
        self.threadpool.start(self.controlWo)
        # self.threadpool.start(self.viewWo)

    def closeEvent(self, event):
        """Before closing the application stop all threads and return ok code."""
        self.finish_thread.emit()
        app.exit(0)

    def handle_refresh_button(self):
        """Get list of serial ports available."""
        ls = self.serialWo.get_port_list()
        if ls:
            # print(ls)
            # self.ui.textEdit.append("Listing serial ports: ")
            # self.ui.textEdit.append(str(ls))
            self.ui.serialPortsComboBox.clear()
            self.ui.serialPortsComboBox.addItems(ls)
        else:
            # print('No serial ports available.')
            self.ui.textEdit.append('No serial ports available.')
            self.ui.serialPortsComboBox.clear()

    def handle_connect_button(self):
        """Connect/Disconnect button opens/closes the selected serial port and
           creates the serial worker thread. If the thread was
           already created previously and paused, it revives it."""
        if not self.connection_status:
            # print(self.serialPortsComboBox.currentText())
            if self.serialWo.open_port(self.ui.serialPortsComboBox.currentText()):
                if self.serialWo.no_serial_worker:
                    self.serialWo.revive_it()
                    self.threadpool.start(self.serialWo)
                    self.serialWo.thread_is_started()
                if self.serialWo.is_paused:
                    self.serialWo.revive_it()
                self.connection_status = True
                self.ui.connectButton.setText("Disconnect")
                self.ui.serialPortsComboBox.hide()
                self.ui.refreshButton.hide()
                self.ui.send_text_edit.show()
                self.ui.send_push_button.show()
        else:
            self.serialWo.close_port()
            self.connection_status = False
            self.ui.connectButton.setText("Connect")
            self.ui.serialPortsComboBox.show()
            self.ui.refreshButton.show()
            self.ui.send_text_edit.hide()
            self.ui.send_push_button.hide()
            self.ui.statusLabel.setText("Not Connected")

    def send_input(self):
        """Send input to the serial port."""
        self.serialTxQu.put(self.ui.send_text_edit.text() + "\n")
        self.ui.send_text_edit.clear()

    def handle_unlock(self):
        print("unlock")
        self.serialTxQu.put("$X\n")

    def handle_homing(self):
        print("homing")
        self.serialTxQu.put("$H\n")

    def handle_x_minus(self):
        print("x_minus")
        self.serialTxQu.put("$J=G91 X-10 F100000\n") #todo: change this, just for test

    def handle_clear_terminal(self):
        self.ui.textEdit.clear()

    def hide_show_console(self):
        if self.ui.actionHide_Show_Console.isChecked():
            self.ui.consoleTextEdit.show()
        else:
            self.ui.consoleTextEdit.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_man = StyleManager(app)
    window = MainWindow()

    style_man.change_style("Fusion")
    style_man.set_dark_palette()

    window.show()
    sys.exit(app.exec_())

