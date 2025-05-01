from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QDockWidget,QAction
from gui.widgets.palette import PaletteWidget
from gui.gui_elements.graphics_led import GraphicsLED
from gui.connection_manager import ConnectionManager
from gui.gui_elements.graphics_battery import GraphicsBattery
from gui.gui_elements.graphics_resistor import GraphicsResistor
from PyQt5.QtCore import Qt
import webbrowser

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
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)
        
        self.connection_manager = ConnectionManager(self.scene)

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