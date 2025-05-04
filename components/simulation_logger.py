class SimulationLogger:
    def __init__(self):
        self.logs = []

    def log(self, message: str):
        print(message)
        self.logs.append(message)

    def clear(self):
        self.logs = []

    def get_all_logs(self) -> str:
        return "\n".join(self.logs)