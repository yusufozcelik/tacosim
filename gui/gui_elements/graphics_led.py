from PyQt5.QtWidgets import QGraphicsTextItem, QMenu, QColorDialog
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin
from components.base_component import BaseComponent

class GraphicsLED(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 50, 30))

        self.setPos(x, y)
        self.setBrush(QBrush(QColor("gray")))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem("LED", self)
        self.label.setDefaultTextColor(Qt.white)
        self.label.setPos(10, 5)

        self.led_color = QColor("red")
        self.voltage = 0.0
        self.current = 0.0

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="VCC"),
            SelectablePin(45, 10, connection_manager, self, name="GND")
        ]

    def get_pins(self):
        return self.pins

    def get_resistance(self):
        return 0.0

    def get_voltage(self):
        return 0.0

    def set_simulation_results(self, voltage, current):
        self.voltage = voltage
        self.current = current

    def pins_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return pin
        return None

    def simulate(self, simulation_engine):
        if not simulation_engine.running:
            self.setBrush(QColor("gray"))
            self.current = 0.0  # simülasyon durduğunda sıfırla
            self.voltage = 0.0
            return

        # Eğer voltage veya current atanmadıysa devre tamamlanmamış demektir
        voltage = getattr(self, "voltage", 0.0)
        current = getattr(self, "current", 0.0)

        if voltage == 0.0 or current == 0.0:
            self.setBrush(QColor("gray"))
        elif current > 0.05:  # Patlama durumu
            self.setBrush(QColor("orange"))
        else:
            self.setBrush(QColor(self.led_color))

    def contextMenuEvent(self, event):
        menu = QMenu()
        delete_action = menu.addAction("🗑️Sil")
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
