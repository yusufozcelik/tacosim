from PyQt5.QtWidgets import QMenu, QGraphicsTextItem, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QGraphicsView
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import QRectF, Qt, QPointF
from components.base_component import BaseComponent
from gui.gui_elements.selectable_pin import SelectablePin
import math
import re

class GraphicsPotentiometer(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 60, 60))
        self.setPos(x, y)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)

        self.connection_manager = connection_manager

        self.pins = [
            SelectablePin(0, 30, connection_manager, self, name="A"),
            SelectablePin(50, 30, connection_manager, self, name="B")
        ]

        self.max_resistance = 300  # default 300Ω
        self.rotation_angle = 225
        self.value = 0.0
        self.simulation_running = False
        self.last_mouse_pos = None

        self.label = QGraphicsTextItem("300Ω", self)
        self.label.setFont(QFont("Arial", 8))
        self.label.setDefaultTextColor(Qt.white)
        self.label.setPos((60 - self.label.boundingRect().width()) / 2, 48)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#444"))
        painter.drawEllipse(10, 10, 40, 40)

        painter.setBrush(QColor("#777"))
        painter.drawEllipse(25, 25, 10, 10)

        cx, cy = 30, 30
        radius = 15
        angle_rad = math.radians(self.rotation_angle % 360)
        end_x = cx + radius * math.cos(angle_rad)
        end_y = cy - radius * math.sin(angle_rad)

        painter.setPen(QPen(Qt.white, 2))
        painter.drawLine(QPointF(cx, cy), QPointF(end_x, end_y))

    def get_pins(self):
        return self.pins

    def get_resistance(self):
        resistance = self.max_resistance * self.value
        print(f"[Potansiyometre] Aktif Direnç: {resistance:.2f} Ω")
        return resistance

    def get_voltage(self):
        return 0.0

    def simulate(self, simulation_engine):
        self.simulation_running = simulation_engine.running
        print(f"[Potansiyometre] Simülasyon aktif mi? {self.simulation_running}")
        self.update()

    def set_simulation_results(self, voltage, current):
        print(f"[Potansiyometre] V: {voltage:.2f}V | I: {current:.6f}A")

    def contextMenuEvent(self, event):
        if self.simulation_running:
            return  # Simülasyon sırasında kapalı
        menu = QMenu()

        delete_action = menu.addAction("🗑️ Sil")
        delete_action.triggered.connect(lambda: self.scene().removeItem(self))
        
        set_value_action = menu.addAction("⚙️ Pot Değerini Ayarla")
        set_value_action.triggered.connect(self.open_value_dialog)

        selected = menu.exec_(event.screenPos())

    def open_value_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("Potansiyometre Maksimum Değeri")

        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        input_label = QLabel("Değer:")
        input_field = QLineEdit()
        unit_combo = QComboBox()
        unit_combo.addItems(["Ω", "kΩ", "MΩ"])

        unit = "Ω"
        val = self.max_resistance
        if val >= 1_000_000:
            input_field.setText(str(val // 1_000_000))
            unit = "MΩ"
        elif val >= 1_000:
            input_field.setText(str(val // 1_000))
            unit = "kΩ"
        else:
            input_field.setText(str(val))

        unit_combo.setCurrentText(unit)

        form_layout.addWidget(input_label)
        form_layout.addWidget(input_field)
        form_layout.addWidget(unit_combo)

        layout.addLayout(form_layout)

        btn_ok = QPushButton("Tamam")
        btn_ok.clicked.connect(lambda: self.set_max_value(input_field.text(), unit_combo.currentText(), dialog))
        layout.addWidget(btn_ok)

        dialog.setLayout(layout)
        dialog.exec_()

    def set_max_value(self, value, unit, dialog):
        try:
            val = float(value)
            if unit == "kΩ":
                val *= 1_000
            elif unit == "MΩ":
                val *= 1_000_000

            self.max_resistance = val
            self.label.setPlainText(self.format_label(val))
            dialog.accept()
            print(f"[Pot] Yeni Max Değer: {self.max_resistance}")
            self.update()
        except ValueError:
            self.label.setPlainText("Hatalı")

    def mousePressEvent(self, event):
        if self.simulation_running:
            self.last_mouse_pos = event.scenePos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.simulation_running:
            center = self.sceneBoundingRect().center()
            current_pos = event.scenePos()
            dx = current_pos.x() - center.x()
            dy = current_pos.y() - center.y()

            angle = math.degrees(math.atan2(-dy, dx)) % 360

            # Açı 225°–360° veya 0°–135° arasında olmalı
            if angle >= 225:
                value = (angle - 225) / 90  # 225 → 0, 315 → 1
            elif angle <= 135:
                value = (angle + 135) / 90  # 0 → ~1.5, 135 → 3
            else:
                return  # 135–225 arası yasak bölge

            # Toplam geçerli aralık 225–135 = 270°
            clamped_angle = angle if angle >= 225 else angle + 360
            if clamped_angle > 495:
                clamped_angle = 495
            elif clamped_angle < 225:
                clamped_angle = 225

            self.rotation_angle = clamped_angle % 360
            self.value = (clamped_angle - 225) / 270  # 225 → 0.0, 495 → 1.0

            print(f"[Pot] Açı: {self.rotation_angle:.1f}°, Oran: {self.value:.3f}, R: {self.get_resistance():.1f}Ω")

            views = self.scene().views()
            if views:
                window = views[0].window()
                if hasattr(window, "rerun_simulation_and_update_status"):
                    print("Simülasyon tekrar başlatılıyor")
                    window.rerun_simulation_and_update_status()

            self.update()
        else:
            super().mouseMoveEvent(event)

    def to_dict(self):
        return {
            "type": "potentiometer",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "rotation_angle": self.rotation_angle,
            "max_resistance": self.max_resistance
        }

    @staticmethod
    def from_dict(data, connection_manager):
        pot = GraphicsPotentiometer(data["x"], data["y"], connection_manager)
        pot.rotation_angle = data.get("rotation_angle", 225)
        pot.max_resistance = data.get("max_resistance", 10000)
        pot.value = (pot.rotation_angle - 225) / 270
        pot.label.setPlainText(GraphicsPotentiometer.format_label(pot.max_resistance))
        return pot

    @staticmethod
    def format_label(value):
        if value >= 1_000_000:
            return f"{int(value // 1_000_000)}M"
        elif value >= 1_000:
            return f"{int(value // 1_000)}K"
        return str(int(value))