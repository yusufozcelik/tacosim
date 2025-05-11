from PyQt5.QtWidgets import QGraphicsTextItem, QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtCore import QRectF, Qt
from gui.gui_elements.selectable_pin import SelectablePin
from components.base_component import BaseComponent
import re

class GraphicsResistor(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 60, 30))
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#b8860b")))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setTransformOriginPoint(self.boundingRect().center())


        self.resistance_value = "220Ω"
        self.value_label = QGraphicsTextItem(self.resistance_value, self)
        self.value_label.setDefaultTextColor(Qt.white)
        self.value_label.setPos(10, 20)

        self.pins = [
            SelectablePin(-5, 10, connection_manager, self, name="A"),
            SelectablePin(55, 10, connection_manager, self, name="B")
        ]

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the body
        painter.setBrush(QColor("#b8860b"))  # light brown body
        painter.setPen(Qt.black)
        painter.drawRoundedRect(10, 5, 40, 20, 5, 5)

        # Draw the leads
        painter.setBrush(QColor("#888888"))  # metal leads
        painter.drawRect(0, 12, 10, 6)
        painter.drawRect(50, 12, 10, 6)

        # Determine color bands based on resistance
        ohms = int(self.get_resistance())
        digits = list(str(ohms))
        colors = {
            '0': "black", '1': "brown", '2': "red", '3': "orange", '4': "yellow",
            '5': "green", '6': "blue", '7': "violet", '8': "gray", '9': "white"
        }

        if len(digits) >= 2:
            band_width = 5
            band_height = 20
            band_spacing = 8

            start_x = 14  # starting X position for first band

            color1 = QColor(colors.get(digits[0], "black"))
            color2 = QColor(colors.get(digits[1], "black"))
            multiplier_color = QColor(colors.get(str(len(digits)-2), "black"))

            painter.setBrush(color1)
            painter.drawRect(start_x, 5, band_width, band_height)
            painter.setBrush(color2)
            painter.drawRect(start_x + band_spacing, 5, band_width, band_height)
            painter.setBrush(multiplier_color)
            painter.drawRect(start_x + 2 * band_spacing, 5, band_width, band_height)

    def get_pins(self):
        return self.pins
    
    def set_simulation_results(self, voltage, current):
        self.voltage = voltage
        self.current = current

    def get_resistance(self):
        match = re.match(r"^(\d+(?:\.\d+)?)(Ω|kΩ|MΩ)$", self.resistance_value)
        if not match:
            return 0.0

        number, unit = match.groups()
        value = float(number)

        if unit == "kΩ":
            value *= 1_000
        elif unit == "MΩ":
            value *= 1_000_000

        return value

    def get_voltage(self):
        return 0.0

    def simulate(self, simulation_engine):
        if simulation_engine.running:
            self.setBrush(QColor("#f4a261"))
        else:
            self.setBrush(QColor("#b8860b"))

    def rotate_left(self):
        self.setRotation(self.rotation() - 90)

    def rotate_right(self):
        self.setRotation(self.rotation() + 90)

    def contextMenuEvent(self, event):
        menu = QMenu()

        delete_action = QAction("🗑️ Sil", menu)
        delete_action.triggered.connect(lambda: self.scene().removeItem(self))
        menu.addAction(delete_action)

        set_value_action = QAction("⚙️ Direnç Değerini Ayarla", menu)
        set_value_action.triggered.connect(self.open_value_dialog)
        menu.addAction(set_value_action)

        rotate_left_action = QAction("⟲ 90° Sola Döndür", menu)
        rotate_left_action.triggered.connect(self.rotate_left)
        menu.addAction(rotate_left_action)

        rotate_right_action = QAction("⟳ 90° Sağa Döndür", menu)
        rotate_right_action.triggered.connect(self.rotate_right)
        menu.addAction(rotate_right_action)

        menu.exec_(event.screenPos())

    def set_resistor_value(self, value, unit, dialog):
        try:
            float(value)
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

        match = re.match(r"^(\d+(?:\.\d+)?)(Ω|kΩ|MΩ)$", self.resistance_value)
        if match:
            number, unit = match.groups()
            input_field.setText(number)
            index = unit_combo.findText(unit)
            if index != -1:
                unit_combo.setCurrentIndex(index)
        else:
            input_field.setText("1")
            unit_combo.setCurrentIndex(0)

        form_layout.addWidget(input_label)
        form_layout.addWidget(input_field)
        form_layout.addWidget(unit_combo)

        layout.addLayout(form_layout)

        btn_ok = QPushButton("Tamam")
        btn_ok.clicked.connect(lambda: self.set_resistor_value(input_field.text(), unit_combo.currentText(), dialog))
        layout.addWidget(btn_ok)

        dialog.setLayout(layout)
        dialog.exec_()

    def to_dict(self):
        return {
            "type": "resistor",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "value": self.resistance_value
        }

    @staticmethod
    def from_dict(data, connection_manager):
        resistor = GraphicsResistor(data["x"], data["y"], connection_manager)
        resistor.resistance_value = data.get("value", "220Ω")
        resistor.value_label.setPlainText(resistor.resistance_value)
        return resistor