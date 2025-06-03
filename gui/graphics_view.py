from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt

class CustomGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragMode(QGraphicsView.NoDrag)
        self.last_mouse_pos = None

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            factor = 1.2 if zoom_in else 1 / 1.2
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        if self.scene().connection_manager.first_pin:
            self.scene().connection_manager.update_temp_wire(self.mapToScene(event.pos()))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())

        if event.button() == Qt.LeftButton and self.scene().connection_manager.temp_wire:
            item = self.itemAt(event.pos())
            if item is None or not hasattr(item, "name"):
                self.scene().connection_manager.temp_wire.add_bend_point(scene_pos)
                return

        if event.button() == Qt.RightButton:
            self.scene().connection_manager.cancel_connection()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setCursor(Qt.ArrowCursor)
            self.last_mouse_pos = None
        else:
            super().mouseReleaseEvent(event)