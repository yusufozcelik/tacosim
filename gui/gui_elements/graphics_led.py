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

        self.vcc = SelectablePin(-5, 10, connection_manager, self, name="VCC")
        self.gnd = SelectablePin(45, 10, connection_manager, self, name="GND")

    def simulate(self):
        vcc_source = self.vcc.connected_pin
        gnd_source = self.gnd.connected_pin

        if not vcc_source or not gnd_source:
            self.setBrush(QColor("gray"))
            return

        if vcc_source.name == "VCC" and gnd_source.name == "GND":
            self.setBrush(QColor("red"))
        elif vcc_source.name == "GND" and gnd_source.name == "VCC":
            self.setBrush(QColor("darkRed"))
        else:
            self.setBrush(QColor("black"))