from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QInputDialog
from PyQt5.QtGui import QBrush, QColor, QFont
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

        self.voltage = 5.0

        self.value_label = QGraphicsTextItem(f"{self.voltage:.1f}V", self)
        self.value_label.setDefaultTextColor(Qt.white)
        self.value_label.setPos(10, 20)

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="VCC"),
            SelectablePin(55, 10, connection_manager, self, name="GND")
        ]

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("🗑️ Sil")
        voltage_action = menu.addAction("🔋 Gerilim Ayarla")
        selected_action = menu.exec_(event.screenPos())
        if selected_action == delete_action:
            if hasattr(self, "delete"):
                self.delete()
            else:
                self.scene().removeItem(self)
        elif selected_action == voltage_action:
            self.set_voltage_dialog()

    def set_voltage_dialog(self):
        value, ok = QInputDialog.getDouble(
            None,
            "Gerilim Ayarla",
            "Batarya gerilimi (V):",
            self.voltage,
            0.1, 24.0,
            1  # ondalık hassasiyet
        )
        if ok:
            self.voltage = value
            self.value_label.setPlainText(f"{self.voltage:.1f}V")

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
        battery.voltage_label.setPlainText(f"{battery.voltage:.1f}V")
        return battery