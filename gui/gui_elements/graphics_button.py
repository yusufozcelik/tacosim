from PyQt5.QtWidgets import QGraphicsItem, QMenu
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin
from components.base_component import BaseComponent

class GraphicsButton(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 60, 30))
        self.setPos(x, y)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.connection_manager = connection_manager
        self.closed = False  # Başlangıçta açık devre

        self.pins = [
            SelectablePin(0, 10, connection_manager, self, name="A"),
            SelectablePin(50, 10, connection_manager, self, name="B")
        ]

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Gövde
        painter.setBrush(QColor("#cccccc"))
        painter.drawRoundedRect(10, 5, 40, 20, 5, 5)

        # Durum çizgisi
        painter.setBrush(QColor("green" if self.closed else "red"))
        painter.drawRect(25, 10, 10, 10)

    def get_pins(self):
        return self.pins

    def get_resistance(self):
        return 0.0 if self.closed else float('inf')

    def get_voltage(self):
        return 0.0

    def set_simulation_results(self, voltage, current):
        self.voltage = voltage
        self.current = current
        self.update()

    def simulate(self, running: bool):
        self.update()

    def contextMenuEvent(self, event):
        menu = QMenu()
        toggle_action = menu.addAction("🔀 Durumu Değiştir")
        delete_action = menu.addAction("🗑️ Sil")
        selected = menu.exec_(event.screenPos())
        if selected == toggle_action:
            self.closed = not self.closed
            self.update()
        elif selected == delete_action:
            if hasattr(self, "delete"):
                self.delete()
            else:
                self.scene().removeItem(self)

    def to_dict(self):
        return {
            "type": "button",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "closed": self.closed
        }

    @staticmethod
    def from_dict(data, connection_manager):
        btn = GraphicsButton(data["x"], data["y"], connection_manager)
        btn.closed = data.get("closed", False)
        return btn

    def mousePressEvent(self, event):
        self._drag_start_pos = event.screenPos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # Only toggle state if there was no drag
        try:
            distance = (event.screenPos() - self._drag_start_pos).manhattanLength()
        except AttributeError:
            distance = 0
        if distance < 5:  # Sürükleme yoksa tıklama say
            self.closed = not self.closed
            self.update()

            scene = self.scene()
            if scene and scene.views():
                main_window = scene.views()[0].window()
                if getattr(main_window, "simulation_running", False):
                    main_window.rerun_simulation_and_update_status()

        super().mouseReleaseEvent(event)