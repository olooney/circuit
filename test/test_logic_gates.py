import unittest

from circuit import Wire
from circuit.logic_gates import *


class LogicGateTest(unittest.TestCase):

    def test_binary_gates(self):
        # TODO be more assertive :)
        for GateClass in [NAND, AND, OR, NOR, XOR, XNOR]:
            x = Wire()
            y = Wire()
            gate = GateClass(a=x, b=y)
            z = gate.out

            for x_value in [True, False]:
                for y_value in [True, False]:
                    x.reset()
                    y.reset()
                    x.value = x_value
                    y.value = y_value
                    print(type(gate).__name__, x.value, y.value, " =>", z.value, sep="\t")
            print()
