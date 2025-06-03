from typing import List, Set
from gui.gui_elements.selectable_pin import SelectablePin
from components.simulation_logger import SimulationLogger

class SimulationEngine:
    def __init__(self, scene, logger=None):
        self.scene = scene
        self.running = False
        self.last_total_resistance = 0.0
        self.logger = logger or SimulationLogger()

    def run(self):
        self.running = True
        self.logger.log("⚡ Simülasyon Motoru Başlatıldı")

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
                if path and self.is_pin_pair_directional(vcc_pin, gnd_pin):
                    self.logger.log("[Engine] ✅ Kapalı devre bulundu, hesaplama yapılıyor.")
                    self.calculate_and_apply(path)
                else:
                    self.logger.log("[Engine] ❌ Kapalı devre bulunamadı, simülasyon uygulanmayacak.")
    
    def stop(self):
        self.running = False
        self.logger.log("🛑 Simülasyon Motoru Durduruldu")

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
            self.logger.log("[Engine] ⚠️ Voltaj kaynağı (batarya) bulunamadı.")
            return

        source_voltage = batteries[0].get_voltage()

        try:
            current = source_voltage / total_resistance if total_resistance > 0 else float('inf')
        except ZeroDivisionError:
            current = float('inf')

        for comp in path:
            if hasattr(comp, "pins_by_name"):
                vcc_pin = comp.pins_by_name("VCC")
                gnd_pin = comp.pins_by_name("GND")
                if vcc_pin and gnd_pin:
                    if not self.is_pin_pair_directional(vcc_pin, gnd_pin):
                        comp.set_simulation_results(0.0, 0.0)
                        continue

            comp.set_simulation_results(source_voltage, current)

    def trace_complete_loop(self, start_pin: SelectablePin, end_pin: SelectablePin) -> List:
        visited_pins = set()
        visited_components = set()
        path = []

        def dfs(pin):
            if pin in visited_pins:
                return False
            visited_pins.add(pin)

            component = pin.parentItem()
            added_to_path = False
            if component not in visited_components:
                visited_components.add(component)
                path.append(component)
                added_to_path = True

            if pin == end_pin:
                return True

            if hasattr(component, "get_pins"):
                for sibling in component.get_pins():
                    if sibling is pin or not sibling.connected_pin:
                        continue
                    next_pin = sibling.connected_pin
                    if self.is_direction_valid(sibling, next_pin):
                        if dfs(next_pin):
                            return True

            if pin.connected_pin and self.is_direction_valid(pin, pin.connected_pin):
                if dfs(pin.connected_pin):
                    return True

            if added_to_path:
                path.pop()
            return False

        if dfs(start_pin):
            return path
        else:
            self.logger.log("[trace] ❌ No loop found")
            return []
        
    def is_pin_pair_directional(self, vcc_pin, gnd_pin):
        if not vcc_pin or not gnd_pin:
            return False

        visited = set()

        def dfs(pin):
            if pin == gnd_pin:
                return True
            visited.add(pin)

            parent = pin.parentItem()
            if not hasattr(parent, "get_pins"):
                return False

            for p in parent.get_pins():
                if p is not pin and p.connected_pin and p.connected_pin not in visited:
                    if not self.is_direction_valid(p, p.connected_pin):
                        continue
                    if dfs(p.connected_pin):
                        return True

            if pin.connected_pin and pin.connected_pin not in visited:
                if not self.is_direction_valid(pin, pin.connected_pin):
                    return False
                return dfs(pin.connected_pin)

            return False

        return dfs(vcc_pin)

    def is_direction_valid(self, from_pin, to_pin):
        parent = from_pin.parentItem()
        if hasattr(parent, "pins_by_name"):
            if parent.__class__.__name__ == "GraphicsLED":
                return from_pin.name == to_pin.name
        return True