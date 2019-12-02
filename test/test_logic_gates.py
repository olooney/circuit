import unittest

from circuit import Wire, Bus
from circuit.logic_gates import *


class LogicGateTest(unittest.TestCase):

    def test_not_gate(self):
        inp = Wire()
        out = Wire()
        NOT(inp, out)
        inp.value = True
        self.assertIs(out.value, False)
        inp.reset()
        inp.value = False
        self.assertIs(out.value, True)

    def print_binary_gates(self):
        """
        Print truth tables for each gate without assertions.
        """
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

    def assert_gate(self, GateClass, binary_operation):
        """
        Utility for testing a generic binary (two input) gate.
        """
        a, b = inputs = Bus(2)
        gate = GateClass(a=a, b=b)
        z = gate.out

        for x in [True, False]:
            for y in [True, False]:
                inputs.reset()
                a.value = x
                b.value = y
                self.assertIs(binary_operation(x, y), gate.out.value)

    def test_NAND(self):
        self.assert_gate(NAND, lambda x, y: not (x & y))

    def test_AND(self):
        self.assert_gate(AND, lambda x, y: x & y)

    def test_OR(self):
        self.assert_gate(OR, lambda x, y: x | y)

    def test_NOR(self):
        self.assert_gate(NOR, lambda x, y: not (x | y))

    def test_XOR(self):
        self.assert_gate(XOR, lambda x, y: x ^ y)

    def test_XNOR(self):
        self.assert_gate(XNOR, lambda x, y: not (x ^ y))


class MuxTest(unittest.TestCase):
    def test_mux(self):
        a, b, sel = inputs = Bus(3)
        out = Wire()
        mux = Mux(a=a, b=b, select=sel, out=out)

        for x in [0, 1]:
            for y in [0, 1]:
                inputs.reset()
                a.value = bool(x)
                b.value = bool(y)
                sel.value = False
                self.assertIs(out.value, a.value, "OUT == A")

                inputs.reset()
                a.value = bool(x)
                b.value = bool(y)
                sel.value = True 
                self.assertIs(out.value, b.value, "OUT == B")

                    
