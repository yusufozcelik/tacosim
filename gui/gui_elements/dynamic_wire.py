from PyQt5.QtWidgets import QGraphicsPathItem, QMenu, QAction, QColorDialog
from PyQt5.QtGui import QPen, QPainterPath, QColor
from PyQt5.QtCore import QTimer, Qt, QPointF

class DynamicWire(QGraphicsPathItem):
    def __init__(self, pin1, pin2, color, bend_points=None):
        super().__init__()
        self.pin1 = pin1
        self.pin2 = pin2
        self.color = color
        self.pen = QPen(self.color, 2)
        self.setPen(self.pen)

        self.bend_points = bend_points if bend_points else []

        self.setFlag(self.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(30)

        self.update_position()

    def add_bend_point(self, point: QPointF):
        self.bend_points.append(point)
        self.update_position()

    def update_position(self, endpoint_pos=None):
        p1 = self.pin1.sceneBoundingRect().center()
        if self.pin2:
            p2 = self.pin2.sceneBoundingRect().center()
        elif endpoint_pos:
            p2 = endpoint_pos
        else:
            return

        path = QPainterPath(p1)
        for bp in self.bend_points:
            path.lineTo(bp)
        path.lineTo(p2)
        self.setPath(path)

    def hoverEnterEvent(self, event):
        self.setPen(QPen(Qt.yellow, 2, Qt.DashLine))

    def hoverLeaveEvent(self, event):
        self.setPen(QPen(self.color, 2))

    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("🗑️ Sil", menu)
        delete_action.triggered.connect(self.delete)
        menu.addAction(delete_action)

        color_action = QAction("🎨 Rengini Değiştir", menu)
        color_action.triggered.connect(self.change_color)
        menu.addAction(color_action)

        menu.exec_(event.screenPos())

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color
            self.pen = QPen(self.color, 2)
            self.setPen(self.pen)

    def delete(self):
        if self.pin1.connected_pin == self.pin2:
            self.pin1.connected_pin = None
        if self.pin2 and self.pin2.connected_pin == self.pin1:
            self.pin2.connected_pin = None

        main_window = self.scene().views()[0].window()
        if hasattr(main_window, "history_stack"):
            main_window.history_stack.append({"type": "remove", "item": self})
            main_window.redo_stack.clear()

        self.scene().removeItem(self)

    def to_dict(self):
        return {
            "type": "wire",
            "from": {
                "parent_id": self.pin1.parentItem().data(0),
                "pin_name": self.pin1.name
            },
            "to": {
                "parent_id": self.pin2.parentItem().data(0),
                "pin_name": self.pin2.name
            },
            "color": self.color.name(),
            "bend_points": [(point.x(), point.y()) for point in self.bend_points]
        }

    @staticmethod
    def from_dict(data, pin_lookup, scene):
        pin1 = pin_lookup[data["from"]["parent_id"]][data["from"]["pin_name"]]
        pin2 = pin_lookup[data["to"]["parent_id"]][data["to"]["pin_name"]]
        color = QColor(data.get("color", "#00FF00"))  # default: green

        wire = DynamicWire(pin1, pin2, color)
        for x, y in data.get("bend_points", []):
            wire.add_bend_point(QPointF(x, y))
        scene.addItem(wire)
        return wire