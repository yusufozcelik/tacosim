from PyQt5.QtWidgets import QGraphicsTextItem, QMenu, QAction
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QFont
from PyQt5.QtCore import QRectF, Qt
from components.base_component import BaseComponent
from gui.gui_elements.selectable_pin import SelectablePin
import uuid
from gui.windows.arduino_code_editor import ArduinoCodeEditorWindow
from components.arduino_interpreter import ArduinoInterpreter

class GraphicsArduinoUno(BaseComponent):
    def __init__(self, x, y, connection_manager):
        super().__init__(QRectF(0, 0, 180, 220))
        self.setPos(x, y)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.setTransformOriginPoint(self.boundingRect().center())

        self.interpreter = ArduinoInterpreter(self)

        self.connection_manager = connection_manager
        self.pins = []
        self.unique_id = str(uuid.uuid4())
        self.code = ""
        self.pin_states = {}

        # Dijital pinler sol üst (D0-D13)
        for i in range(14):
            self.pins.append(SelectablePin(0, 40 + i * 10, connection_manager, self, name=f"D{i}"))

        # Analog pinler sağ orta (A0-A5)
        for i in range(6):
            self.pins.append(SelectablePin(170, 60 + i * 12, connection_manager, self, name=f"A{i}"))

        # Alt pinler (GND, 5V, 3.3V, VIN)
        self.pins += [
            SelectablePin(40, 205, connection_manager, self, name="GND"),
            SelectablePin(65, 205, connection_manager, self, name="5V"),
            SelectablePin(90, 205, connection_manager, self, name="3.3V"),
            SelectablePin(115, 205, connection_manager, self, name="VIN"),
        ]

        # Etiket
        self.label = QGraphicsTextItem("Arduino UNO", self)
        self.label.setDefaultTextColor(Qt.white)
        self.label.setFont(QFont("Arial", 10, QFont.Bold))
        self.label.setPos(45, 10)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # Gövde
        painter.setBrush(QColor("#004080"))
        painter.setPen(Qt.black)
        painter.drawRoundedRect(0, 0, 180, 220, 10, 10)

        # USB bölgesi
        painter.setBrush(QColor("#666"))
        painter.drawRoundedRect(5, 5, 25, 15, 3, 3)

        # Barrel jack bölgesi
        painter.setBrush(QColor("black"))
        painter.drawRect(5, 25, 20, 10)

        # Etiketler
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 7))

        for i in range(14):
            painter.drawText(15, 48 + i * 10, f"D{i}")

        for i in range(6):
            painter.drawText(145, 67 + i * 12, f"A{i}")

        painter.drawText(38, 215, "GND")
        painter.drawText(62, 215, "5V")
        painter.drawText(85, 215, "3.3V")
        painter.drawText(110, 215, "VIN")

    def get_pins(self):
        return self.pins

    def get_resistance(self):
        return 0.0

    def get_voltage(self):
        return 0.0

    def simulate(self, simulation_engine):
        if not simulation_engine.running:
            for p in self.pins:
                p.state, p.voltage = 0, 0.0
                for conn in p.connections:
                    conn.voltage = 0.0
                    owner = conn.parentItem()
                    if hasattr(owner, "on_pin_change"):
                        owner.on_pin_change(conn)
            self.pin_states.clear()
            return

        for p in self.pins:
            print(f"[DEBUG] {p.name}: bağlantı sayısı = {len(getattr(p, 'connections', []))}")

        if not hasattr(self, "interpreter_initialized"):
            self.interpreter.load_code(self.code)
            self.interpreter.run_setup()
            self.interpreter_initialized = True

        self.interpreter.run_loop()

    def set_simulation_results(self, voltage, current):
        pass

    def contextMenuEvent(self, event):
        menu = QMenu()

        code_action = QAction("💻 Kod Yaz", menu)
        code_action.triggered.connect(self.open_code_editor)
        menu.addAction(code_action)

        rotate_left = QAction("⟲ 90° Sola Döndür", menu)
        rotate_left.triggered.connect(lambda: self.setRotation(self.rotation() - 90))
        menu.addAction(rotate_left)

        rotate_right = QAction("⟳ 90° Sağa Döndür", menu)
        rotate_right.triggered.connect(lambda: self.setRotation(self.rotation() + 90))
        menu.addAction(rotate_right)

        delete_action = QAction("🗑️ Sil", menu)
        delete_action.triggered.connect(lambda: self.scene().removeItem(self))
        menu.addAction(delete_action)

        menu.exec_(event.screenPos())

    def open_code_editor(self):
        self.editor = ArduinoCodeEditorWindow(self)
        self.editor.show()

    def to_dict(self):
        return {
            "type": "arduino_uno",
            "x": self.pos().x(),
            "y": self.pos().y(),
            "rotation": self.rotation(),
            "unique_id": self.unique_id,
            "code": self.code
        }

    @staticmethod
    def from_dict(data, connection_manager):
        arduino = GraphicsArduinoUno(data["x"], data["y"], connection_manager)
        arduino.setRotation(data.get("rotation", 0))
        arduino.unique_id = data.get("unique_id", str(uuid.uuid4()))
        arduino.code = data.get("code", "")
        return arduino
    
    def set_pin_mode(self, name, mode):
        pin = self.find_pin(f"D{name}")
        if pin:
            pin.mode = mode

    def set_pin_value(self, pin_idx, value):
        pin_name = f"D{pin_idx}"
        pin_obj  = next((p for p in self.pins if p.name == pin_name), None)
        if not pin_obj:
            print(f"[UYARI] {pin_name} bulunamadı"); return

        self.pin_states[pin_idx] = value
        pin_obj.state   = value
        pin_obj.voltage = 5.0 if value else 0.0

        for conn in pin_obj.connections:
            conn.voltage = pin_obj.voltage           # ➍ 5 V LED-VCC’ye taşındı
            owner = conn.parentItem()                # LED, direnç, vs.
            if hasattr(owner, "on_pin_change"):
                owner.on_pin_change(conn)            # bileşen kendini günceller

    def read_analog(self, name):
        pin = self.find_pin(f"D{name}")
        if pin:
            return pin.get_voltage() * 1023 / 5  # örnek: 0–5V arası
        return 0

    def find_pin(self, name):
        return next((p for p in self.pins if p.name == name), None)