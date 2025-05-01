from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin

class GraphicsLED(QGraphicsRectItem):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 50, 30))
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("gray")))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem("LED", self)
        self.label.setDefaultTextColor(Qt.white)
        self.label.setPos(10, 5)

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="VCC"),
            SelectablePin(45, 10, connection_manager, self, name="GND")
        ]

    def pins_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return pin
        return None

    def find_connected_source(self, pin, expected_name, visited=None):
        if visited is None:
            visited = set()
        if pin in visited:
            return None
        visited.add(pin)

        if pin.name == expected_name:
            return pin

        connected = pin.connected_pin
        if connected is None:
            return None

        parent = connected.parentItem()
        if not hasattr(parent, "pins"):
            return None

        for p in parent.pins:
            if p is not connected:
                result = self.find_connected_source(p, expected_name, visited)
                if result:
                    return result
        return None

    def simulate(self, running):
        if not running:
            self.setBrush(QColor("gray"))
            return

        vcc_pin = self.pins_by_name("VCC")
        gnd_pin = self.pins_by_name("GND")

        vcc_source = self.find_connected_source(vcc_pin, "VCC")
        gnd_source = self.find_connected_source(gnd_pin, "GND")

        if vcc_source and gnd_source:
            self.setBrush(QColor("red"))
        elif vcc_source or gnd_source:
            self.setBrush(QColor("darkRed"))  # ters bağlantı
        else:
            self.setBrush(QColor("black"))  # bağlantı yok