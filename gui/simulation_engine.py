from typing import List, Set
from gui.gui_elements.selectable_pin import SelectablePin

class SimulationEngine:
    def __init__(self, scene):
        self.scene = scene
        self.running = False
        self.last_total_resistance = 0.0

    def run(self):
        self.running = True
        print("⚡ Simülasyon Motoru Başlatıldı")

        batteries = [item for item in self.scene.items() if hasattr(item, 'get_voltage') and item.get_voltage() > 0]

        for battery in batteries:
            vcc_pin = None
            gnd_pin = None

            for pin in battery.get_pins():
                if pin.name == "VCC":
                    vcc_pin = pin
                elif pin.name == "GND":
                    gnd_pin = pin

            if vcc_pin and gnd_pin:
                path = self.trace_complete_loop(vcc_pin, gnd_pin)
                if path:
                    print("[Engine] ✅ Kapalı devre bulundu, hesaplama yapılıyor.")
                    self.calculate_and_apply(path)
                else:
                    print("[Engine] ❌ Kapalı devre bulunamadı, simülasyon uygulanmayacak.")

    def trace_path(self, pin: SelectablePin, visited: Set[SelectablePin]) -> List:
        path = []
        stack = [pin]

        while stack:
            current_pin = stack.pop()
            if current_pin in visited:
                continue
            visited.add(current_pin)

            parent = current_pin.parentItem()
            if parent and parent not in path:
                path.append(parent)

            if not hasattr(parent, 'get_pins'):
                continue

            for p in parent.get_pins():
                if p.connected_pin:
                    stack.append(p.connected_pin)

        return path if len(path) > 1 else []

    def calculate_and_apply(self, path: List):
        total_resistance = sum(comp.get_resistance() for comp in path if hasattr(comp, 'get_resistance'))
        self.last_total_resistance = total_resistance

        batteries = [comp for comp in path if comp.__class__.__name__ == "GraphicsBattery"]

        if not batteries:
            print("[Engine] ⚠️ Voltaj kaynağı (batarya) bulunamadı.")
            return

        source_voltage = batteries[0].get_voltage()

        try:
            current = source_voltage / total_resistance if total_resistance > 0 else float('inf')
        except ZeroDivisionError:
            current = float('inf')

        for comp in path:
            comp.set_simulation_results(source_voltage, current)

    def trace_complete_loop(self, start_pin: SelectablePin, end_pin: SelectablePin) -> List:
        visited_pins = set()
        path_components = []

        def dfs(pin):
            if pin in visited_pins:
                return False
            visited_pins.add(pin)

            parent = pin.parentItem()
            if parent not in path_components:
                path_components.append(parent)

            if pin == end_pin:
                return True

            # 1. Kendi parent'ındaki diğer pinlere bak
            for sibling in parent.get_pins():
                if sibling is pin:
                    continue
                connected = sibling.connected_pin
                if connected and dfs(connected):
                    return True

            # 2. Kendi pininden bağlı olan pine doğrudan geç
            if pin.connected_pin:
                connected = pin.connected_pin
                if dfs(connected):
                    return True

            return False

        if dfs(start_pin):
            return path_components
        else:
            print("[trace] ❌ No loop found")
            return []