from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QColorDialog

class PaletteWidget(QWidget):
    def __init__(self, on_led_add, on_color_change=None, on_battery_add=None, on_simulate=None):
        super().__init__()
        self.on_color_change = on_color_change

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.btn_led = QPushButton("💡 LED Ekle")
        self.btn_led.clicked.connect(on_led_add)

        self.btn_color = QPushButton("🔵 Kablo Rengi Seç")
        self.btn_color.clicked.connect(self.choose_color)

        self.btn_simulate = QPushButton("▶️ Simülasyonu Başlat")
        self.btn_simulate.clicked.connect(on_simulate)
        layout.addWidget(self.btn_simulate)

        self.btn_battery = QPushButton("🔋 Batarya Ekle")
        if on_battery_add:
            self.btn_battery.clicked.connect(on_battery_add)
        layout.addWidget(self.btn_battery)

        layout.addWidget(self.btn_led)
        layout.addWidget(self.btn_color)
        layout.addStretch()
        self.setLayout(layout)

    def choose_color(self):
        if not self.on_color_change:
            print("Renk değiştirme fonksiyonu atanmadı.")
            return

        color = QColorDialog.getColor()
        if color.isValid():
            self.on_color_change(color)