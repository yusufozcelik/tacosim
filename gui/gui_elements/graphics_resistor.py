from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin

class GraphicsResistor(QGraphicsRectItem):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 60, 30))
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#b8860b"))) # açık kahverengi
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem("DIR", self)
        self.label.setDefaultTextColor(Qt.black)
        self.label.setPos(18, 5)

        self.resistance_value = "220Ω"
        self.value_label = QGraphicsTextItem(self.resistance_value, self)
        self.value_label.setDefaultTextColor(Qt.white)
        self.value_label.setPos(10, 20)

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="A"),
            SelectablePin(55, 10, connection_manager, self, name="B")
        ]

    def contextMenuEvent(self, event):
        menu = QMenu()
        set_value_action = QAction("⚙️ Direnç Değerini Ayarla", menu)
        set_value_action.triggered.connect(self.open_value_dialog)
        menu.addAction(set_value_action)

        delete_action = QAction("🗑️ Sil", menu)
        delete_action.triggered.connect(lambda: self.scene().removeItem(self))
        menu.addAction(delete_action)

        menu.exec_(event.screenPos())

    def set_resistor_value(self, value, unit, dialog):
        try:
            float(value)  # geçerli mi kontrol et
            self.resistance_value = f"{value}{unit}"
            self.value_label.setPlainText(self.resistance_value)
            dialog.accept()
        except ValueError:
            self.value_label.setPlainText("Geçersiz")

    def open_value_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("Direnç Değerini Ayarla")

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        input_label = QLabel("Değer:")
        input_field = QLineEdit()
        unit_combo = QComboBox()
        unit_combo.addItems(["Ω", "kΩ", "MΩ"])

        import re
        match = re.match(r"^(\d+(?:\.\d+)?)(Ω|kΩ|MΩ)$", self.resistance_value)
        if match:
            number, unit = match.groups()
            input_field.setText(number)
            index = unit_combo.findText(unit)
            if index != -1:
                unit_combo.setCurrentIndex(index)
        else:
            input_field.setText("1")
            unit_combo.setCurrentIndex(1)

        form_layout.addWidget(input_label)
        form_layout.addWidget(input_field)
        form_layout.addWidget(unit_combo)

        layout.addLayout(form_layout)

        btn_ok = QPushButton("Tamam")
        btn_ok.clicked.connect(lambda: self.set_resistor_value(input_field.text(), unit_combo.currentText(), dialog))
        layout.addWidget(btn_ok)

        dialog.setLayout(layout)
        dialog.exec_()

    def simulate(self, running):
        if running:
            self.setBrush(QColor("#f4a261")) # simülasyon sırasında hafif parlak
        else:
            self.setBrush(QColor("#b8860b")) # normal renk

    def to_dict(self):
        return {
            "type": "resistor",
            "x": self.pos().x(),
            "y": self.pos().y()
        }

    @staticmethod
    def from_dict(data, connection_manager):
        return GraphicsResistor(data["x"], data["y"], connection_manager)