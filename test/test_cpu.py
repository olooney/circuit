import unittest
from circuit import Wire, Bus, TRUE, FALSE, CPU

class CPUTest(unittest.TestCase):
    def test_cpu(self):
        inputs = Bus([TRUE, FALSE])
        cpu = CPU()
        cpu.ram.registers[42].bit_registers[7].next_state = True

        for i in range(10):
            inputs.reset()
            inputs.propagate()
            print(cpu.hex_dump())

