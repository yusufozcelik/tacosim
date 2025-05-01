from PyQt5.QtGui import QColor
from gui.gui_elements.dynamic_wire import DynamicWire

class ConnectionManager:
    def __init__(self, scene):
        self.scene = scene
        self.first_pin = None
        self.current_color = QColor("green")

    def set_color(self, color):
        self.current_color = color

    def pin_clicked(self, pin):
        if pin.connected_pin is not None:
            return

        if self.first_pin is None:
            self.first_pin = pin
            print("👉 İlk pin seçildi:", pin)
        else:
            if self.first_pin.connected_pin or pin.connected_pin:
                print("⚠️ Bu pinlerden biri zaten bağlı.")
                self.first_pin = None
                return

            wire = DynamicWire(self.first_pin, pin, self.current_color)
            self.scene.addItem(wire)

            main_window = self.scene.views()[0].window()
            if hasattr(main_window, "history_stack"):
                main_window.history_stack.append({"type": "add", "item": wire})
                main_window.redo_stack.clear()

            self.first_pin.connected_pin = pin
            pin.connected_pin = self.first_pin

            print("✅ Bağlantı kuruldu:", self.first_pin, "<-->", pin)
            self.first_pin = None