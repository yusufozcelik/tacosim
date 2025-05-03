from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QColorDialog
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin
from gui.gui_elements.graphics_battery import GraphicsBattery

class GraphicsLED(QGraphicsRectItem):
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

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="VCC"),
            SelectablePin(45, 10, connection_manager, self, name="GND")
        ]

    def pins_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return pin
        return None

    def find_connected_source(self, pin, expected_name, visited=None):
        if pin is None:
            return None

        if visited is None:
            visited = set()
        if pin in visited:
            return None
        visited.add(pin)

        if pin.name == expected_name and isinstance(pin.parentItem(), GraphicsBattery):
            return pin

        connected = pin.connected_pin
        if connected is None:
            return None

        parent = connected.parentItem()
        if not hasattr(parent, "pins"):
            return None

        for next_pin in parent.pins:
            result = self.find_connected_source(next_pin, expected_name, visited)
            if result:
                return result

        return None

    def simulate(self, running):
        if not running:
            self.setBrush(QColor("gray"))
            return

        vcc_pin = self.pins_by_name("VCC")
        gnd_pin = self.pins_by_name("GND")

        vcc_source = self.find_connected_source(vcc_pin, "VCC")
        gnd_source = self.find_connected_source(gnd_pin, "GND")

        if vcc_source and gnd_source:
            self.setBrush(self.led_color)  # doğru bağlandı
        else:
            self.setBrush(QColor("gray"))  # eksik ya da ters bağlantı

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
    