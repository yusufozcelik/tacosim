from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QDockWidget
from gui.widgets.palette import PaletteWidget
from gui.gui_elements.graphics_led import GraphicsLED
from gui.connection_manager import ConnectionManager
from gui.gui_elements.graphics_battery import GraphicsBattery
from gui.gui_elements.graphics_resistor import GraphicsResistor
from PyQt5.QtCore import Qt

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
            on_simulate=self.simulate_all
        )
        self.dock = QDockWidget("Elemanlar")
        self.dock.setWidget(self.palette)
        self.addDockWidget(1, self.dock)
        self.dock.setFeatures(self.dock.DockWidgetClosable | self.dock.DockWidgetMovable)
        self.dock.visibilityChanged.connect(self.on_dock_visibility_changed)

    def add_led_to_scene(self):
        led = GraphicsLED(100, 100, self.connection_manager)
        self.scene.addItem(led)

    def on_dock_visibility_changed(self, visible):
        if not visible:
            self.menuBar().clear()
            view_menu = self.menuBar().addMenu("Görünüm")
            show_dock_action = view_menu.addAction("Eleman Panelini Göster")
            show_dock_action.triggered.connect(lambda: self.dock.show())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)

    def add_battery_to_scene(self):
        battery = GraphicsBattery(200, 100, self.connection_manager)
        self.scene.addItem(battery)

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