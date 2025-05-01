from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import Qt

class SelectablePin(QGraphicsEllipseItem):
    def __init__(self, x, y, connection_manager, parent=None, name=""):
        super().__init__(x, y, 10, 10, parent)
        self.connection_manager = connection_manager
        self.connected_pin = None
        self.name = name

        self.setBrush(QBrush(QColor("white")))
        self.setFlag(self.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor("cyan")))

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor("white")))

    def mousePressEvent(self, event):
        self.connection_manager.pin_clicked(self)