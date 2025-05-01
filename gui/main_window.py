from PyQt5.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QDockWidget
from gui.widgets.palette import PaletteWidget
from gui.gui_elements.graphics_led import GraphicsLED
from gui.connection_manager import ConnectionManager
from gui.gui_elements.graphics_battery import GraphicsBattery
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tacosim - Devre Simülatörü")
        self.setGeometry(100, 100, 1000, 700)

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
        for item in self.scene.items():
            if isinstance(item, GraphicsLED):
                item.simulate()