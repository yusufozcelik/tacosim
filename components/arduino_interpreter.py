import re
import time

class ArduinoInterpreter:
    def __init__(self, component):
        self.component = component
        self.variables = {}
        self.setup_lines = []
        self.loop_lines = []
        self._should_execute = True

    def load_code(self, code_str):
        self.setup_lines = []
        self.loop_lines = []

        current = None
        for line in code_str.splitlines():
            line = line.strip()
            if line.startswith("void setup()"):
                current = self.setup_lines
                continue
            elif line.startswith("void loop()"):
                current = self.loop_lines
                continue
            elif "{" in line or "}" in line:
                continue
            if current is not None and line:
                current.append(line)

    def run_setup(self):
        for line in self.setup_lines:
            self.execute(line)

    def run_loop(self):
        for line in self.loop_lines:
            self.execute(line)

    def execute(self, line):
        # ---- if kontrolü ----
        if line.startswith("if"):
            m = re.match(r"if\s*\((.+)\)", line)
            if m:
                condition = m.group(1)
                result = self.eval_expr(condition)
                self._should_execute = result
                print(f"[YORUMLAYICI] if ({condition}) → {result}")
            return

        elif line.startswith("else"):
            self._should_execute = not self._should_execute
            print(f"[YORUMLAYICI] else → {self._should_execute}")
            return

        # ---- if sonucu false ise bir satır atla ----
        if not self._should_execute:
            print(f"[YORUMLAYICI] satır atlandı: {line}")
            self._should_execute = True
            return

        # ---- pinMode ----
        if line.startswith("pinMode"):
            m = re.match(r"pinMode\((\d+),\s*(INPUT|OUTPUT)\)", line)
            if m:
                pin, mode = m.groups()
                print(f"[YORUMLAYICI] pinMode({pin}, {mode})")
                self.component.set_pin_mode(pin, mode)

        # ---- digitalWrite ----
        elif line.startswith("digitalWrite"):
            m = re.match(r"digitalWrite\((\d+),\s*(HIGH|LOW)\)", line)
            if m:
                pin, value = m.groups()
                print(f"[YORUMLAYICI] digitalWrite({pin}, {value})")
                self.component.set_pin_value(pin, value)

        # ---- delay ----
        elif line.startswith("delay"):
            m = re.match(r"delay\((\d+)\)", line)
            if m:
                delay_time = int(m.group(1))
                print(f"[YORUMLAYICI] delay({delay_time}ms)")
                time.sleep(delay_time / 1000.0)

        # ---- analogRead ----
        elif "analogRead" in line:
            m = re.match(r"(int\s+)?(\w+)\s*=\s*analogRead\(A(\d+)\);?", line)
            if m:
                _, var, ain = m.groups()
                val = self.component.read_analog(f"A{ain}")
                self.variables[var] = val
                print(f"[YORUMLAYICI] {var} = analogRead(A{ain}) → {val}")

        # ---- int val = 123; ----
        elif line.startswith("int "):
            m = re.match(r"int (\w+)\s*=\s*(.+);?", line)
            if m:
                var, val_expr = m.groups()
                val = self.eval_expr(val_expr)
                self.variables[var] = val
                print(f"[YORUMLAYICI] int {var} = {val}")

        # ---- val = 456; ----
        elif re.match(r"^\w+\s*=\s*[^=]+;?", line):
            m = re.match(r"(\w+)\s*=\s*(.+);?", line)
            if m:
                var, val_expr = m.groups()
                val = self.eval_expr(val_expr)
                self.variables[var] = val
                print(f"[YORUMLAYICI] {var} = {val}")

    def eval_expr(self, expr):
        """
        Basit aritmetik ve karşılaştırma ifadelerini değerlendir.
        """
        try:
            for var, val in self.variables.items():
                expr = expr.replace(var, str(val))
            result = eval(expr, {"__builtins__": None}, {})
            return result
        except Exception as e:
            print(f"[YORUMLAYICI] eval hatası: {expr} → {e}")
            return 0