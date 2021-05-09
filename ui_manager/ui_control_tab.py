from PySide2.QtCore import Signal, Slot, QObject
import logging

logger = logging.getLogger(__name__)


class UiControlTab(QObject):
    """Class dedicated to UI <--> Control interactions on Control Tab. """
    serial_send_s = Signal(str)

    def __init__(self, ui, control_worker, serial_worker):
        super(UiControlTab, self).__init__()
        self.ui = ui
        self.controlWo = control_worker
        self.serialWo = serial_worker

        self.ui.xy_jog_l.setText("XY [" + str(self.ui.xy_step_val_dsb.value()) + " mm]")
        self.ui.z_jog_l.setText("Z [" + str(self.ui.z_step_val_dsb.value()) + " mm]")

        self.serial_connection_status = False
        self.serial_send_s.connect(self.serialWo.send)
        self.controlWo.update_status_s.connect(self.update_status)
        self.controlWo.update_probe_s.connect(self.update_probe)
        self.controlWo.update_console_text_s.connect(self.update_console_text)

        # From Controller Manager to Serial Manager
        self.controlWo.serial_send_s.connect(self.serialWo.send)

        # From Serial Manager to UI Manager
        self.serialWo.update_console_text_s.connect(self.update_console_text)

        # From Serial Manager to Control Manager
        self.serialWo.rx_queue_not_empty_s.connect(self.controlWo.parse_rx_queue)

        self.ui.send_te.setPlaceholderText('input here')
        self.ui.send_te.hide()
        self.ui.send_pb.hide()

        self.ui.refresh_pb.clicked.connect(self.handle_refresh_button)
        self.ui.connect_pb.clicked.connect(self.handle_connect_button)
        self.ui.clear_terminal_pb.clicked.connect(self.handle_clear_terminal)
        self.ui.send_pb.clicked.connect(self.send_input)
        self.ui.send_te.returnPressed.connect(self.send_input)
        self.ui.unlock_pb.clicked.connect(self.handle_unlock)
        self.ui.homing_pb.clicked.connect(self.handle_homing)
        self.ui.xMinusButton.clicked.connect(self.handle_x_minus)
        self.ui.xPlusButton.clicked.connect(self.handle_x_plus)
        self.ui.yMinusButton.clicked.connect(self.handle_y_minus)
        self.ui.yPlusButton.clicked.connect(self.handle_y_plus)
        self.ui.xYPlusButton.clicked.connect(self.handle_xy_plus)
        self.ui.xYPlusMinuButton.clicked.connect(self.handle_x_plus_y_minus)
        self.ui.xYMinusButton.clicked.connect(self.handle_xy_minus)
        self.ui.xYMinusPlusButton.clicked.connect(self.handle_x_minus_y_plus)
        self.ui.z_minus_pb.clicked.connect(self.handle_z_minus)
        self.ui.z_plus_pb.clicked.connect(self.handle_z_plus)

        self.ui.xy_plus_1_pb.clicked.connect(self.handle_xy_plus_1)
        self.ui.xy_minus_1_pb.clicked.connect(self.handle_xy_minus_1)
        self.ui.xy_div_10_pb.clicked.connect(self.handle_xy_div_10)
        self.ui.xy_mul_10_pb.clicked.connect(self.handle_xy_mul_10)
        self.ui.z_plus_1_pb.clicked.connect(self.handle_z_plus_1)
        self.ui.z_minus_1_pb.clicked.connect(self.handle_z_minus_1)
        self.ui.z_div_10_pb.clicked.connect(self.handle_z_div_10)
        self.ui.z_mul_10_pb.clicked.connect(self.handle_z_mul_10)

        self.ui.probe_pb.clicked.connect(self.handle_probe_cmd)
        self.ui.ABL_pb.clicked.connect(self.handle_auto_bed_levelling)

    @Slot(list)
    def update_status(self, status_l):
        self.ui.status_l.setText(status_l[0])
        self.ui.mpos_x_label.setText(status_l[1][0])
        self.ui.mpos_y_label.setText(status_l[1][1])
        self.ui.mpos_z_label.setText(status_l[1][2])

    @Slot(list)
    def update_probe(self, probe_l):
        pass

    @Slot(str)
    def update_console_text(self, new_text):
        self.ui.serial_te.append(new_text)

    def send_input(self):
        """Send input to the serial port."""
        # self.serialTxQu.put(self.ui.send_te.text() + "\n")
        self.serial_send_s.emit(self.ui.send_te.text() + "\n")
        self.ui.send_te.clear()

    def handle_refresh_button(self):
        """Get list of serial ports available."""
        ls = self.serialWo.get_port_list()
        if ls:
            logger.debug("Available ports: " + str(ls))
            self.ui.serial_ports_cb.clear()
            self.ui.serial_ports_cb.addItems(ls)
        else:
            logger.info('No serial ports available.')
            self.ui.serial_te.append('No serial ports available.')
            self.ui.serial_ports_cb.clear()

    def handle_connect_button(self):
        """Connect/Disconnect button opens/closes the selected serial port and
           creates the serial worker thread. If the thread was
           already created previously and paused, it revives it."""
        if not self.serial_connection_status:
            if self.serialWo.open_port(self.ui.serial_ports_cb.currentText()):
                self.serial_connection_status = True
                self.ui.connect_pb.setText("Disconnect")
                self.ui.serial_ports_cb.hide()
                self.ui.serial_baud_cb.hide()
                self.ui.refresh_pb.hide()
                self.ui.send_te.show()
                self.ui.send_pb.show()
        else:
            self.serialWo.close_port()
            self.serial_connection_status = False
            self.ui.connect_pb.setText("Connect")
            self.ui.serial_ports_cb.show()
            self.ui.serial_baud_cb.show()
            self.ui.refresh_pb.show()
            self.ui.send_te.hide()
            self.ui.send_pb.hide()
            self.ui.status_l.setText("Not Connected")

    def handle_clear_terminal(self):
        self.ui.serial_te.clear()

    def hide_show_console(self):
        if self.ui.actionHide_Show_Console.isChecked():
            self.ui.logging_plain_te.show()
        else:
            self.ui.logging_plain_te.hide()

    def handle_unlock(self):
        logging.debug("Unlock Command")
        self.serial_send_s.emit("$X\n")

    def handle_homing(self):
        logging.debug("Homing Command")
        self.serial_send_s.emit("$H\n")

    def handle_x_minus(self):
        logging.debug("X_minus Command")
        x_min_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 X-" + str(x_min_val) + " F100000\n")

    def handle_x_plus(self):
        logging.debug("X_plus Command")
        x_plus_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 X" + str(x_plus_val) + " F100000\n")

    def handle_y_minus(self):
        logging.debug("Y_minus Command")
        y_min_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 Y-" + str(y_min_val) + " F100000\n")

    def handle_y_plus(self):
        logging.debug("Y_plus Command")
        y_plus_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 Y" + str(y_plus_val) + " F100000\n")

    def handle_xy_plus(self):
        logging.debug("XY_plus Command")
        xy_plus_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 X" + str(xy_plus_val) + "Y" + str(xy_plus_val) + " F100000\n")

    def handle_x_plus_y_minus(self):
        logging.debug("X_plus_Y_minus Command")
        x_p_y_m_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 X" + str(x_p_y_m_val) + "Y-" + str(x_p_y_m_val) + " F100000\n")

    def handle_xy_minus(self):
        logging.debug("XY_minus Command")
        xy_minus_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 X-" + str(xy_minus_val) + "Y-" + str(xy_minus_val) + " F100000\n")

    def handle_x_minus_y_plus(self):
        logging.debug("X_minus_y_plus Command")
        x_m_y_p_val = self.ui.xy_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 X-" + str(x_m_y_p_val) + "Y" + str(x_m_y_p_val) + " F100000\n")

    def handle_z_minus(self):
        logging.debug("Z_minus Command")
        z_minus_val = self.ui.z_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 Z-" + str(z_minus_val) + " F100000\n")

    def handle_z_plus(self):
        logging.debug("Z_plus Command")
        z_plus_val = self.ui.z_step_val_dsb.value()
        self.serial_send_s.emit("$J=G91 Z" + str(z_plus_val) + " F100000\n")

    def handle_xy_plus_1(self):
        xy_val = self.ui.xy_step_val_dsb.value() + self.ui.xy_step_val_dsb.singleStep()
        self.ui.xy_step_val_dsb.setValue(xy_val)

    def handle_xy_minus_1(self):
        xy_val = self.ui.xy_step_val_dsb.value() - self.ui.xy_step_val_dsb.singleStep()
        self.ui.xy_step_val_dsb.setValue(xy_val)

    def handle_xy_div_10(self):
        xy_step_val = self.ui.xy_step_val_dsb.singleStep()
        if not xy_step_val == 0.01:  # Minimum step is 0.01
            xy_step_val /= 10.0  # self.xy_step_val / 10.0
            self.ui.xy_step_val_dsb.setSingleStep(xy_step_val)
            self.ui.xy_jog_l.setText("XY [" + str(xy_step_val) + " mm]")

    def handle_xy_mul_10(self):
        xy_step_val = self.ui.xy_step_val_dsb.singleStep()
        if not xy_step_val == 100.0:  # Maximum step is 100.0
            xy_step_val = self.ui.xy_step_val_dsb.singleStep() * 10.0  # xy_step_val * 10.0
            self.ui.xy_step_val_dsb.setSingleStep(xy_step_val)
            self.ui.xy_jog_l.setText("XY [" + str(xy_step_val) + " mm]")

    def handle_z_plus_1(self):
        z_val = self.ui.z_step_val_dsb.value() + self.ui.z_step_val_dsb.singleStep()
        self.ui.z_step_val_dsb.setValue(z_val)

    def handle_z_minus_1(self):
        z_val = self.ui.z_step_val_dsb.value() - self.ui.z_step_val_dsb.singleStep()
        self.ui.z_step_val_dsb.setValue(z_val)

    def handle_z_div_10(self):
        z_step_val = self.ui.z_step_val_dsb.singleStep()
        if not z_step_val == 0.01:  # Minimum step is 0.01
            z_step_val /= 10.0
            self.ui.z_step_val_dsb.setSingleStep(z_step_val)
            self.ui.z_jog_l.setText("Z [" + str(z_step_val) + " mm]")

    def handle_z_mul_10(self):
        z_step_val = self.ui.z_step_val_dsb.singleStep()
        if not z_step_val == 100.0:  # Maximum step is 100.0
            z_step_val *= 10.0
            self.ui.z_step_val_dsb.setSingleStep(z_step_val)
            self.ui.z_jog_l.setText("Z [" + str(z_step_val) + " mm]")

    def handle_probe_cmd(self):
        logging.debug("Probe Command")
        # todo: fake parameters just to test probe
        probe_z_max = -11.0
        probe_feed_rate = 10.0
        self.controlWo.cmd_probe(probe_z_max, probe_feed_rate)

    def handle_auto_bed_levelling(self):
        logging.debug("Auto Bed Levelling Command")
        # todo: fake parameters just for testing ABL
        xy_coord_list = [(0.0, 0.0), (0.0, 10.0), (0.0, 20.0),
                         (10.0, 0.0), (10.0, 10.0), (10.0, 20.0),
                         (20.0, 0.0), (20.0, 10.0), (20.0, 20.0)]
        travel_z = 1.0
        probe_z_max = -11.0
        probe_feed_rate = 10.0
        self.controlWo.cmd_auto_bed_levelling(xy_coord_list, travel_z, probe_z_max, probe_feed_rate)

