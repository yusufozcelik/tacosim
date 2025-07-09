from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt, QEvent

class SelectablePin(QGraphicsEllipseItem):
    def __init__(self, x, y, connection_manager, parent=None, name=""):
        super().__init__(x, y, 10, 10, parent)
        self.connection_manager = connection_manager
        self.connected_pin = None
        self.name = name

        self.connections = []
        self.voltage = 0.0

        if name == "VCC":
            self.default_color = QColor("red")
        elif name == "GND":
            self.default_color = QColor("black")
        else:
            self.default_color = QColor("white")

        self.setBrush(QBrush(self.default_color))
        self.setFlag(self.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)

        self.setAcceptHoverEvents(True)

        if self.scene():
            self.scene().installEventFilter(self)

    def connect_to(self, other_pin):
        self.connected_pin = other_pin
        other_pin.connected_pin = self

        self.other_component = other_pin.parentItem()
        other_pin.other_component = self.parentItem()

        if other_pin not in self.connections:
            self.connections.append(other_pin)
        if self not in other_pin.connections:
            other_pin.connections.append(self)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("cyan")))

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(self.default_color))

    def mousePressEvent(self, event):
        self.connection_manager.pin_clicked(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.GraphicsSceneMouseMove:
            self.connection_manager.update_temp_wire(event.scenePos())
        return False