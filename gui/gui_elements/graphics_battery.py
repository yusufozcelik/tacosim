from PyQt5.QtWidgets import QMenu, QInputDialog
from PyQt5.QtGui import QPainter, QFont, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin
from components.base_component import BaseComponent

class GraphicsBattery(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 80, 110))
        self.setPos(x, y)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.voltage = 5.0
        self.current = 0.0
        self.connection_manager = connection_manager
        
        self.setTransformOriginPoint(self.boundingRect().center())

        # Pinler: Üstte VCC, altta GND
        self.pins = [
            SelectablePin(35, 10, connection_manager, self, name="VCC"),
            SelectablePin(35, 95, connection_manager, self, name="GND")
        ]

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Batarya gövdesi
        body_rect = QRectF(10, 20, 60, 80)
        painter.setBrush(QColor("#FFA500"))
        painter.setPen(Qt.black)
        painter.drawRoundedRect(body_rect, 10, 10)

        # Üst terminal
        painter.setBrush(Qt.black)
        painter.drawRect(30, 10, 20, 10)

        # + ve - işaretleri
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(QRectF(10, 20, 60, 20), Qt.AlignCenter, "+")
        painter.drawText(QRectF(10, 80, 60, 20), Qt.AlignCenter, "-")

        # BATARYA ve 5V metni ortalanmış
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(QRectF(10, 40, 60, 20), Qt.AlignCenter, "BATARYA")
        painter.drawText(QRectF(10, 60, 60, 20), Qt.AlignCenter, f"{self.voltage:.1f}V")

    def get_pins(self):
        return self.pins

    def get_resistance(self):
        return 0.0001

    def get_voltage(self):
        return self.voltage

    def set_simulation_results(self, voltage, current):
        self.voltage = voltage
        self.current = current
        self.update()

    def simulate(self, running: bool):
        pass

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("🗑️ Sil")
        voltage_action = menu.addAction("🔋 Gerilim Ayarla")
        rotate_left_action = menu.addAction("⟲ 90° Sola Döndür")
        rotate_right_action = menu.addAction("⟳ 90° Sağa Döndür")
        selected_action = menu.exec_(event.screenPos())
        if selected_action == delete_action:
            if hasattr(self, "delete"):
                self.delete()
            else:
                self.scene().removeItem(self)
        elif selected_action == voltage_action:
            self.set_voltage_dialog()
        elif selected_action == rotate_left_action:
            self.rotate_left()
        elif selected_action == rotate_right_action:
            self.rotate_right()

    def set_voltage_dialog(self):
        value, ok = QInputDialog.getDouble(
            None,
            "Gerilim Ayarla",
            "Batarya gerilimi (V):",
            self.voltage,
            0.1, 24.0,
            1
        )
        if ok:
            self.voltage = value
            self.update()

    def rotate_left(self):
        self.setRotation(self.rotation() - 90)

    def rotate_right(self):
        self.setRotation(self.rotation() + 90)

    def to_dict(self):
        return {
            "type": "battery",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "voltage": self.voltage
        }

    @staticmethod
    def from_dict(data, connection_manager):
        battery = GraphicsBattery(data["x"], data["y"], connection_manager)
        battery.voltage = data.get("voltage", 5.0)
        return battery
