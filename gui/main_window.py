from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QDockWidget,QAction, QLabel, QFileDialog, QMessageBox
from gui.widgets.palette import PaletteWidget
from gui.gui_elements.graphics_led import GraphicsLED
from gui.connection_manager import ConnectionManager
from gui.gui_elements.graphics_battery import GraphicsBattery
from gui.gui_elements.graphics_resistor import GraphicsResistor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import webbrowser
from gui.graphics_view import CustomGraphicsView
import json
from gui.gui_elements.dynamic_wire import DynamicWire

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tacosim - Devre Simülatörü")
        self.setGeometry(100, 100, 1000, 700)
        
        self.simulation_running = False

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QGraphicsView {
                border: 1px solid #444;
                background-color: #2c2c2c;
            }
        """)
        
        self.statusBar().showMessage("Hazır")

        self.history_stack = []
        self.redo_stack = []
        
        # Sahne
        self.scene = QGraphicsScene()
        self.view = CustomGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.watermark_label = QLabel("TACOSIM", self.view)
        self.watermark_label.setStyleSheet("color: rgba(255, 255, 255, 20);")
        self.watermark_label.setFont(QFont("Segoe UI", 60, QFont.Bold))
        self.watermark_label.adjustSize()
        self.watermark_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.watermark_label.setGeometry(
            (self.view.width() - self.watermark_label.width()) // 2,
            (self.view.height() - self.watermark_label.height()) // 2,
            self.watermark_label.width(),
            self.watermark_label.height()
        )
        
        self.connection_manager = ConnectionManager(self.scene)
        self.scene.connection_manager = self.connection_manager

        # Palet
        self.palette = PaletteWidget(
            on_led_add=self.add_led_to_scene,
            on_color_change=self.connection_manager.set_color,
            on_battery_add=self.add_battery_to_scene,
            on_resistor_add=self.add_resistor_to_scene,
            on_simulate=self.simulate_all,
            on_reset=self.reset_scene
        )
        self.dock = QDockWidget("Elemanlar")
        self.dock.setWidget(self.palette)
        self.addDockWidget(1, self.dock)
        self.dock.setFeatures(self.dock.DockWidgetClosable | self.dock.DockWidgetMovable)
        self.dock.visibilityChanged.connect(self.on_dock_visibility_changed)

        # Menü
        menu_bar = self.menuBar()

        # Dosya Menüsü
        file_menu = menu_bar.addMenu("Dosya")

        save_action = QAction("Devreyi Kaydet", self)
        save_action.triggered.connect(lambda: self.save_scene_to_json(
            QFileDialog.getSaveFileName(self, "Devreyi Kaydet", "", "JSON Dosyası (*.json)")[0]
        ))
        file_menu.addAction(save_action)

        load_action = QAction("Devre Yükle", self)
        load_action.triggered.connect(lambda: self.load_scene_from_json(
            QFileDialog.getOpenFileName(self, "Devre Yükle", "", "JSON Dosyası (*.json)")[0]
        ))
        file_menu.addAction(load_action)

        # Görünüm Menüsü
        view_menu = menu_bar.addMenu("Görünüm")
        self.show_dock_action = QAction("Eleman Panelini Göster", self, checkable=True)
        self.show_dock_action.setChecked(True)
        self.show_dock_action.triggered.connect(lambda: self.dock.setVisible(self.show_dock_action.isChecked()))
        view_menu.addAction(self.show_dock_action)

        # Yardım Menüsü
        help_menu = menu_bar.addMenu("Yardım")

        github_action = QAction("GitHub Sayfasını Aç", self)
        github_action.triggered.connect(lambda: webbrowser.open("https://github.com/yusufozcelik/tacosim"))
        help_menu.addAction(github_action)

    def on_dock_visibility_changed(self, visible):
        if hasattr(self, "show_dock_action"):
            self.show_dock_action.setChecked(visible)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self.undo_last_action()
            return

        if event.key() == Qt.Key_Delete:
            for item in self.scene.selectedItems():
                if hasattr(item, "delete"):
                    self.history_stack.append({"type": "remove", "item": item})
                    item.delete()
                else:
                    self.history_stack.append({"type": "remove", "item": item})
                    self.scene.removeItem(item)
            self.redo_stack.clear()

    def add_battery_to_scene(self):
        battery = GraphicsBattery(200, 100, self.connection_manager)
        self.scene.addItem(battery)
        self.history_stack.append({"type": "add", "item": battery})
        self.redo_stack.clear()

    def simulate_all(self):
        self.simulation_running = not self.simulation_running

        if self.simulation_running:
            print("🔁 Simülasyon başladı")
            self.palette.btn_simulate.setText("Simülasyonu Durdur")
            self.statusBar().showMessage("Simülasyon çalışıyor...")
        else:
            print("⛔ Simülasyon durdu")
            self.palette.btn_simulate.setText("Simülasyonu Başlat")
            self.statusBar().showMessage("Simülasyon durduruldu.")

        for item in self.scene.items():
            if hasattr(item, "simulate"):
                item.simulate(self.simulation_running)

    def add_resistor_to_scene(self):
        resistor = GraphicsResistor(150, 150, self.connection_manager)
        self.scene.addItem(resistor)
        self.history_stack.append({"type": "add", "item": resistor})
        self.redo_stack.clear()

    def reset_scene(self):
        for item in self.scene.items():
            if hasattr(item, "delete"):
                item.delete()
            else:
                self.scene.removeItem(item)

        self.simulation_running = False
        self.palette.btn_simulate.setText("Simülasyonu Başlat")
        self.statusBar().showMessage("Devre sıfırlandı.")

        self.history_stack = []
        self.redo_stack = []

    def add_led_to_scene(self):
        led = GraphicsLED(100, 100, self.connection_manager)
        self.scene.addItem(led)
        self.history_stack.append({"type": "add", "item": led})
        self.redo_stack.clear()

    def undo_last_action(self):
        if not self.history_stack:
            return

        last_action = self.history_stack.pop()
        self.redo_stack.append(last_action)

        if last_action["type"] == "add":
            self.scene.removeItem(last_action["item"])
        elif last_action["type"] == "remove":
            self.scene.addItem(last_action["item"])

    def redo_last_action(self):
        if not self.redo_stack:
            return

        next_action = self.redo_stack.pop()
        self.history_stack.append(next_action)

        if next_action["type"] == "add":
            self.scene.addItem(next_action["item"])
        elif next_action["type"] == "remove":
            self.scene.removeItem(next_action["item"])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "watermark_label"):
            self.watermark_label.setGeometry(
                (self.view.width() - self.watermark_label.width()) // 2,
                (self.view.height() - self.watermark_label.height()) // 2,
                self.watermark_label.width(),
                self.watermark_label.height()
            )

    def save_scene_to_json(self, file_path):
        if not file_path:
            return

        items_data = []

        id_counter = 1
        for item in self.scene.items():
            if hasattr(item, "to_dict") and not isinstance(item, DynamicWire):
                item_id = f"item{str(id_counter)}"
                item.setData(0, item_id)
                item_dict = item.to_dict()
                item_dict["id"] = item_id
                items_data.append(item_dict)
                id_counter += 1

        for item in self.scene.items():
            if isinstance(item, DynamicWire):
                wire_dict = item.to_dict()
                items_data.append(wire_dict)

        with open(file_path, "w") as f:
            json.dump(items_data, f, indent=4)

        QMessageBox.information(self, "Kayıt Başarılı", f"Devre başarıyla kaydedildi:\n{file_path}")

    def load_scene_from_json(self, file_path):
        if not file_path:
            return

        with open(file_path, "r") as f:
            items_data = json.load(f)

        self.reset_scene()

        id_map = {}

        for item_data in items_data:
            item_type = item_data.get("type")
            if item_type == "led":
                item = GraphicsLED.from_dict(item_data, self.connection_manager)
            elif item_type == "battery":
                item = GraphicsBattery.from_dict(item_data, self.connection_manager)
            elif item_type == "resistor":
                item = GraphicsResistor.from_dict(item_data, self.connection_manager)
            else:
                continue

            item.setData(0, item_data.get("id"))
            self.scene.addItem(item)
            id_map[item_data["id"]] = item

        for item_data in items_data:
            if item_data["type"] == "wire":
                from_obj = id_map[item_data["from"]["parent_id"]]
                to_obj = id_map[item_data["to"]["parent_id"]]

                pin1 = next(p for p in from_obj.pins if p.name == item_data["from"]["pin_name"])
                pin2 = next(p for p in to_obj.pins if p.name == item_data["to"]["pin_name"])

                wire = DynamicWire(pin1, pin2, QColor(item_data["color"]))
                self.scene.addItem(wire)
                pin1.connected_pin = pin2
                pin2.connected_pin = pin1