from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QDockWidget,QAction, QLabel, QFileDialog, QMessageBox
from gui.widgets.palette import PaletteWidget
from gui.gui_elements.graphics_led import GraphicsLED
from gui.connection_manager import ConnectionManager
from gui.gui_elements.graphics_battery import GraphicsBattery
from gui.gui_elements.graphics_resistor import GraphicsResistor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
import webbrowser
from gui.graphics_view import CustomGraphicsView
import json
from gui.gui_elements.dynamic_wire import DynamicWire
from components.base_component import BaseComponent
from gui.simulation_engine import SimulationEngine
from gui.gui_elements.graphics_button import GraphicsButton
from gui.windows.serial_monitor import SerialMonitorWindow
from gui.gui_elements.graphics_potentiometer import GraphicsPotentiometer
from gui.gui_elements.graphics_arduino_uno import GraphicsArduinoUno

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tacosim - Devre Simülatörü")
        self.setGeometry(100, 100, 1000, 700)

        self.setWindowIcon(QIcon("assets/tacosim_logo.png"))
        
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

        self.info_label = QLabel(self.view)
        self.info_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px 10px;
            }
        """)
        self.info_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.info_label.move(10, 10)
        self.info_label.setText("V: -, R: -, I: -")
        self.info_label.setFixedWidth(250)
        self.info_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.info_label.show()

        self.status_label = QLabel("V: -, R: -, I: -")
        self.statusBar().addPermanentWidget(self.status_label)

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
            on_reset=self.reset_scene,
            on_button_add=self.add_button_to_scene,
            on_potentiometer_add=self.add_potentiometer_to_scene,
            on_arduino_uno_add=self.add_arduino_uno_to_scene
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

        # Seri Port
        serial_menu = menu_bar.addMenu("Seri Port")

        serial_action = QAction("Seri Port İzleyici", self)
        serial_action.triggered.connect(self.open_serial_monitor)
        serial_menu.addAction(serial_action)

        # Görünüm Menüsü
        view_menu = menu_bar.addMenu("Görünüm")
        self.show_dock_action = QAction("Eleman Panelini Göster", self, checkable=True)
        self.show_dock_action.setChecked(True)
        self.show_dock_action.triggered.connect(lambda: self.dock.setVisible(self.show_dock_action.isChecked()))
        view_menu.addAction(self.show_dock_action)

        # Yardım Menüsü
        help_menu = menu_bar.addMenu("Yardım")

        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        github_action = QAction("GitHub Sayfasını Aç", self)
        github_action.triggered.connect(lambda: webbrowser.open("https://github.com/yusufozcelik/tacosim"))
        help_menu.addAction(github_action)
    
    def open_serial_monitor(self):
        self.serial_window = SerialMonitorWindow(self)
        self.serial_window.show()

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
        existing_batteries = [item for item in self.scene.items() if isinstance(item, GraphicsBattery)]
        if existing_batteries:
            QMessageBox.warning(self, "Sınır Aşıldı", "Yalnızca 1 batarya ekleyebilirsiniz.")
            return

        battery = GraphicsBattery(200, 100, self.connection_manager)
        self.scene.addItem(battery)
        self.history_stack.append({"type": "add", "item": battery})
        self.redo_stack.clear()

    def simulate_all(self):
        self.simulation_running = not self.simulation_running

        self.simulation_engine = SimulationEngine(self.scene)
        self.simulation_engine.running = self.simulation_running

        if self.simulation_running:
            print("🔁 Simülasyon başladı")
            self.palette.btn_simulate.setText("Simülasyonu Durdur")
            self.statusBar().showMessage("Simülasyon çalışıyor...")

            self.simulation_engine.run()

            for item in self.scene.items():
                if hasattr(item, "simulate"):
                    item.simulate(self.simulation_engine)

            for item in self.scene.items():
                if isinstance(item, GraphicsLED):
                    voltage = getattr(item, "voltage", 0.0)
                    current = getattr(item, "current", 0.0)
                    resistance = self.simulation_engine.last_total_resistance

                    self.info_label.setText(
                        f"V: {voltage:.1f}V | R: {resistance:.1f}Ω | I: {current:.4f}A"
                    )
                    break
        else:
            print("⛔ Simülasyon durdu")
            self.palette.btn_simulate.setText("Simülasyonu Başlat")
            self.statusBar().showMessage("Simülasyon durduruldu.")
            self.info_label.setText("V: -, R: -, I: -")

            self.simulation_engine.stop()

            for item in self.scene.items():
                if hasattr(item, "simulate"):
                    item.simulate(self.simulation_engine)

    def rerun_simulation_and_update_status(self):
        if not hasattr(self, "simulation_engine") or not self.simulation_engine:
            return

        print("Simülasyon tekrar başlatılıyor")
        self.simulation_engine.run()

        for item in self.scene.items():
            if hasattr(item, "simulate"):
                item.simulate(self.simulation_engine)

        for item in self.scene.items():
            if isinstance(item, GraphicsLED):
                voltage = getattr(item, "voltage", 0.0)
                current = getattr(item, "current", 0.0)
                resistance = self.simulation_engine.last_total_resistance
                self.info_label.setText(f"V: {voltage:.1f}V | R: {resistance:.1f}Ω | I: {current:.4f}A")
                break

    def add_resistor_to_scene(self):
        resistor = GraphicsResistor(150, 150, self.connection_manager)
        self.scene.addItem(resistor)
        self.history_stack.append({"type": "add", "item": resistor})
        self.redo_stack.clear()
        
    def add_arduino_uno_to_scene(self):
        arduino = GraphicsArduinoUno(200, 200, self.connection_manager)
        self.scene.addItem(arduino)
        self.history_stack.append({"type": "add", "item": arduino})
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

    def add_potentiometer_to_scene(self):
        pot = GraphicsPotentiometer(150, 150, self.connection_manager)
        self.scene.addItem(pot)
        self.history_stack.append({"type": "add", "item": pot})
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
        if hasattr(self, "info_label"):
            self.info_label.move(10, 10)
    
    def add_button_to_scene(self):
        button = GraphicsButton(100, 100, self.connection_manager)
        self.scene.addItem(button)
        self.history_stack.append({"type": "add", "item": button})
        self.redo_stack.clear()

    def save_scene_to_json(self, file_path):
        if not file_path:
            return

        if not file_path.lower().endswith(".json"):
            file_path += ".json"

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
            elif item_type == "potentiometer":
                item = GraphicsPotentiometer.from_dict(item_data, self.connection_manager)
            elif item_type == "arduino_uno":
                item = GraphicsArduinoUno.from_dict(item_data, self.connection_manager)
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

    def show_about(self):
        QMessageBox.information(self, "Hakkında",
            "<h3>TACOSIM</h3>"
            "<p>Elektronik devre simülatörü</p>"
            "<img src='assets/tacosim_logo.png' width='100'>"
        )