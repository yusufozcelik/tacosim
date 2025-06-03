from PyQt5.QtWidgets import QMenu, QColorDialog
from PyQt5.QtGui import QBrush, QColor, QPainter, QFont
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin
from components.base_component import BaseComponent

class GraphicsLED(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 60, 100))

        self.setPos(x, y)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.led_color = QColor("red")
        self.voltage = 0.0
        self.current = 0.0
        self.connection_manager = connection_manager

        self.pins = [
            SelectablePin(20, 85, connection_manager, self, name="VCC"),
            SelectablePin(30, 70, connection_manager, self, name="GND")
        ]

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Parlaklık ayarı
        intensity = min(255, max(100, int(self.current * 4000)))
        color = QColor(self.led_color)
        color.setAlpha(intensity)

        # Gövde (oval köşeli dikdörtgen)
        painter.setBrush(color)
        painter.setPen(Qt.black)
        painter.drawRoundedRect(QRectF(10, 10, 40, 30), 8, 8)

        # Alt halka
        painter.setBrush(QColor(self.led_color))
        painter.drawRoundedRect(QRectF(10, 38, 40, 4), 2, 2)

        # Bacaklar
        leg_width = 4
        vcc_height = 45
        gnd_height = 30
        painter.setBrush(QColor("#808080"))
        painter.drawRect(23, 42, leg_width, vcc_height)  # VCC - uzun
        painter.drawRect(33, 42, leg_width, gnd_height)  # GND - kısa

        # + / - işaretleri
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(18, 98, "+")
        painter.drawText(33, 98, "-")

    def get_pins(self):
        return self.pins

    def get_resistance(self):
        return 0.0

    def get_voltage(self):
        return 0.0

    def set_simulation_results(self, voltage, current):
        self.voltage = voltage
        self.current = current
        self.update()

    def pins_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return pin
        return None

    def simulate(self, simulation_engine):
        if not simulation_engine.running:
            self.setBrush(QColor("gray"))
            self.current = 0.0
            self.voltage = 0.0
            return

        vcc_pin = self.pins_by_name("VCC")
        gnd_pin = self.pins_by_name("GND")

        vcc_connected = vcc_pin.connected_pin
        gnd_connected = gnd_pin.connected_pin

        if not vcc_connected or not gnd_connected:
            self.setBrush(QColor("gray"))
            return

        if not simulation_engine.is_pin_pair_directional(vcc_connected, gnd_connected):
            self.setBrush(QColor("gray"))
            return

        # yön doğruysa çalışmaya devam et
        voltage = getattr(self, "voltage", 0.0)
        current = getattr(self, "current", 0.0)

        if voltage == 0.0 or current == 0.0:
            self.setBrush(QColor("gray"))
        elif current > 0.05:
            self.setBrush(QColor("orange"))
        else:
            intensity = min(255, max(50, int(current * 4000)))
            color_with_alpha = QColor(self.led_color)
            color_with_alpha.setAlpha(intensity)
            self.setBrush(color_with_alpha)

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("🗑️ Sil")
        color_action = menu.addAction("🎨 Renk Seç")
        selected_action = menu.exec_(event.screenPos())
        if selected_action == delete_action:
            if hasattr(self, "delete"):
                self.delete()
            else:
                self.scene().removeItem(self)
        elif selected_action == color_action:
            self.select_color()

    def select_color(self):
        color = QColorDialog.getColor(initial=self.led_color)
        if color.isValid():
            self.led_color = color
            self.update()

    def to_dict(self):
        return {
            "type": "led",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "color": self.led_color.name()
        }

    @staticmethod
    def from_dict(data, connection_manager):
        led = GraphicsLED(data["x"], data["y"], connection_manager)
        led.led_color = QColor(data.get("color", "#ff0000"))
        return led