from PyQt5.QtGui import QColor
from gui.gui_elements.dynamic_wire import DynamicWire

class ConnectionManager:
    def __init__(self, scene):
        self.scene = scene
        self.first_pin = None
        self.current_color = QColor("green")
        self.temp_wire = None

    def set_color(self, color):
        self.current_color = color

    def pin_clicked(self, pin):
        if self.first_pin is None:
            self.first_pin = pin
            self.start_temp_wire(pin)
        else:
            if pin == self.first_pin:
                self.cancel_connection()
                return

            wire = DynamicWire(self.first_pin, pin, self.current_color)
            self.scene.addItem(wire)

            self.first_pin.connect_to(pin)
            pin.connect_to(self.first_pin)

            self.cancel_connection()

    def start_temp_wire(self, pin):
        self.temp_wire = DynamicWire(pin, None, self.current_color)
        self.scene.addItem(self.temp_wire)

    def update_temp_wire(self, pos):
        if self.temp_wire:
            self.temp_wire.update_position(endpoint_pos=pos)

    def cancel_connection(self):
        if self.temp_wire:
            self.scene.removeItem(self.temp_wire)
            self.temp_wire = None
        self.first_pin = None