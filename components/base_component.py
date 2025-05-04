from PyQt5.QtWidgets import QGraphicsRectItem

class BaseComponent(QGraphicsRectItem):
    def get_pins(self):
        raise NotImplementedError

    def get_voltage(self):
        return 0.0

    def get_resistance(self):
        return 0

    def simulate(self, running):
        pass