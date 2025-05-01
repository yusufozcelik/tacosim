from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin

class GraphicsLED(QGraphicsRectItem):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 50, 30))
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("red")))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem("LED", self)
        self.label.setDefaultTextColor(Qt.white)
        self.label.setPos(10, 5)

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="VCC"),
            SelectablePin(45, 10, connection_manager, self, name="GND")
        ]

    def simulate(self):
        pins = {p.name: p.connected_pin for p in self.pins}

        vcc = pins.get("VCC")
        gnd = pins.get("GND")

        if not vcc or not gnd:
            self.setBrush(QColor("gray"))
            return

        if vcc.name == "VCC" and gnd.name == "GND":
            self.setBrush(QColor("red"))  # doğru bağlantı
        elif vcc.name == "GND" and gnd.name == "VCC":
            self.setBrush(QColor("darkRed"))  # ters bağlantı
        else:
            self.setBrush(QColor("black"))  # bilinmeyen