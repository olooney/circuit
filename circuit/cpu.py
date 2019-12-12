from circuit.kernel import Wire, Bus, Component, Register
from circuit.combinational import ALU
from circuit.sequential import Register8, Counter8, RAM

__all__ = [
    "CPU",
]

class Controller(Component):
    def __init__(self):
        super().__init__()


class CPU(Component):
    def __init__(self):
        super().__init__()

