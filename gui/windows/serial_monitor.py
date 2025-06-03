from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt
import serial.tools.list_ports

class SerialMonitorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seri Port İzleyici")
        self.resize(500, 400)

        layout = QVBoxLayout()

        # PORT ve Baudrate seçimi
        connection_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.port_combo.addItems([p.device for p in serial.tools.list_ports.comports()])
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "57600", "115200"])
        self.connect_button = QPushButton("Bağlan")

        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_combo)
        connection_layout.addWidget(QLabel("Baud:"))
        connection_layout.addWidget(self.baud_combo)
        connection_layout.addWidget(self.connect_button)

        layout.addLayout(connection_layout)

        # Veri görüntüleme
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Otomatik kaydetme seçeneği
        self.autosave_checkbox = QCheckBox("Veriyi dosyaya kaydet")
        layout.addWidget(self.autosave_checkbox)

        # Kapat
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)