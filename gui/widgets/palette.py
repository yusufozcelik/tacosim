from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QColorDialog

class PaletteWidget(QWidget):
    def __init__(self, on_led_add, on_color_change=None, on_battery_add=None, on_simulate=None, on_resistor_add=None, on_reset=None, on_button_add=None):
        super().__init__()
        self.on_color_change = on_color_change

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-right: 2px solid #444;
            }
        """)

        common_button_style = """
            QPushButton {
                background-color: #ff6600;
                color: white;
                font-size: 14px;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e65c00;
            }
            QPushButton:pressed {
                background-color: #cc5200;
            }
            QPushButton:disabled {
                background-color: #aaaaaa;
                color: #333;
            }
        """

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.btn_led = QPushButton("💡 LED Ekle")
        self.btn_led.setStyleSheet(common_button_style)
        self.btn_led.clicked.connect(on_led_add)

        self.btn_color = QPushButton("🔵 Kablo Rengi Seç")
        self.btn_color.setStyleSheet(common_button_style)
        self.btn_color.clicked.connect(self.choose_color)

        self.btn_simulate = QPushButton("Simülasyonu Başlat")
        self.btn_simulate.clicked.connect(on_simulate)
        self.btn_simulate.setStyleSheet(common_button_style)
        layout.addWidget(self.btn_simulate)

        self.btn_reset = QPushButton("🗑️ Devreyi Sıfırla")
        self.btn_reset.clicked.connect(on_reset)
        self.btn_reset.setStyleSheet(common_button_style)
        layout.addWidget(self.btn_reset)

        self.btn_battery = QPushButton("🔋 Batarya Ekle")
        if on_battery_add:
            self.btn_battery.clicked.connect(on_battery_add)
        self.btn_battery.setStyleSheet(common_button_style)
        layout.addWidget(self.btn_battery)

        self.btn_resistor = QPushButton("🔸 Direnç Ekle")
        if on_resistor_add:
            self.btn_resistor.clicked.connect(on_resistor_add)
        self.btn_resistor.setStyleSheet(common_button_style)
        layout.addWidget(self.btn_resistor)

        self.btn_button = QPushButton("🔘︎ Buton Ekle")
        self.btn_button.setStyleSheet(common_button_style)
        self.btn_button.clicked.connect(on_button_add)
        layout.addWidget(self.btn_button)

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