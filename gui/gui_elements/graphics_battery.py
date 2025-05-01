from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin

class GraphicsBattery(QGraphicsRectItem):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 60, 30))
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("orange")))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem("BATARYA", self)
        self.label.setDefaultTextColor(Qt.black)
        self.label.setPos(3, 5)

        self.vcc = SelectablePin(-5, 10, connection_manager, self, name="VCC")
        self.gnd = SelectablePin(55, 10, connection_manager, self, name="GND")