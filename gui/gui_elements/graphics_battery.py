from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu
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

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="VCC"),
            SelectablePin(55, 10, connection_manager, self, name="GND")
        ]

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("🗑️ Sil")
        selected_action = menu.exec_(event.screenPos())
        if selected_action == delete_action:
            if hasattr(self, "delete"):
                self.delete()
            else:
                self.scene().removeItem(self)

    def to_dict(self):
        return {
            "type": "battery",
            "x": self.pos().x(),
            "y": self.pos().y()
        }

    @staticmethod
    def from_dict(data, connection_manager):
        return GraphicsBattery(data["x"], data["y"], connection_manager)