import unittest

from circuit.kernel import Wire, Bus, Register, NAND, WireError
from circuit.alu import *


class AdderTest(unittest.TestCase):
    def test_half_adder(self):
        a, b = inputs = Bus(2)
        out, c = outputs = Bus(2)

        HalfAdder(a=a, b=b, out=out, c=c)

        for x in [0, 1]:
            for y in [0, 1]:
                inputs.reset()
                a.value = bool(x)
                b.value = bool(y)

                total = int(out.value)
                carry = c.value

                # print("test_half_adder", x, "+", y, "=", total, "C", carry)
                self.assertEqual((x+y)%2, total)
                self.assertIs((x+y)>1, carry)

    def test_full_adder(self):
        a, b, cin = inputs = Bus(3)
        out, cout = outputs = Bus(2)

        adder = FullAdder(a=a, b=b, cin=cin, out=out, cout=cout)

        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    inputs.reset()
                    a.value = bool(x)
                    b.value = bool(y)
                    cin.value = bool(z)

                    total = int(out.value)
                    carry = cout.value

                    # print("test_full_adder", x, "+", y, "+", z, "=", total, "C", carry)
                    self.assertEqual((x + y + z) % 2, total)
                    self.assertIs(x + y + z > 1, carry)


class EightBitTest(unittest.TestCase):
    """
    Test the various 8-bit components found in `circuit.alu`.
    """
    def test_and8(self):
        a = Bus(8)
        b = Bus(8)
        out = Bus(8)

        And8(a=a, b=b, out=out)

        a.value = 3
        b.value = 6
        self.assertEqual(out.value, 2)

    def test_not8(self):
        inp = Bus(8)
        out = Bus(8)

        Not8(inp=inp, out=out)

        inp.value = 42
        self.assertEqual(out.value, 213)

    def test_mux8(self):
        a = Bus(8)
        b = Bus(8)
        select = Wire()
        out = Bus(8)
        inputs = Bus([a, b, select])

        Mux8(a=a, b=b, select=select, out=out)

        for x in [0, 1, 2, 10, 42, 64, 77, 99, 100, 127, 128, 196, 254, 255]:
            for y in [0, 1, 2, 3, 5, 20, 25, 33, 50, 101, 127, 128, 250, 254, 255]:
                inputs.reset()
                a.value = x
                b.value = y
                select.value = False
                # print("test_mux8 SELECT = 0 A =", a.value, "B =", b.value, "OUT =", out.value)
                self.assertEqual(a.value, out.value, "OUT == A")

                inputs.reset()
                a.value = x
                b.value = y
                select.value = True
                # print("test_mux8 SELECT = 1 A =", a.value, "B =", b.value, "OUT =", out.value)
                self.assertEqual(b.value, out.value, "OUT == B")

    def test_add8(self):
        a = Bus(8)
        b = Bus(8)
        out = Bus(8)

        cin = Wire()
        cout = Wire()

        inputs = Bus([a, b, cin])

        Add8(a=a, b=b, cin=cin, out=out, cout=cout)

        a.value = 2
        b.value = 3
        cin.value = False

        self.assertEqual(out.value, 5)

        for x in [0, 1, 2, 10, 42, 64, 77, 99, 100, 127, 128, 196, 254, 255]:
            for y in [0, 1, 2, 3, 5, 20, 25, 33, 50, 101, 127, 128, 250, 254, 255]:
                for z in [0, 1]:
                    inputs.reset()
                    a.value = x
                    b.value = y
                    cin.value = bool(z)

                    # print("test_add8", x, "+", y, "+", z, "=", out.value)
                    self.assertEqual(out.value, (x + y + z) % 256)
                    self.assertIs(cout.value, x + y + z >= 256)

    def test_left_shift8(self):
        a, b = inputs = Bus([ Bus(8), Bus(8) ])
        out = Bus(8)
        LeftShift8(a=a, b=b, out=out)

        for x in [0, 1, 2, 10, 42, 64, 77, 99, 100, 127, 128, 196, 254, 255]:
            for y in range(20):
                inputs.reset()
                a.value = x
                b.value = y
                # print("test_left_shift8", a.value, "<<", b.value, "=", out.value)
                self.assertEqual(out.value, (x << y) % 256)


class ALUTest(unittest.TestCase):
    def setUp(self):
        self.inputs = Bus([Bus(8), Bus(8), Bus(8), Wire()])
        self.a, self.b, self.op, self.cin = self.inputs

        self.out = Bus(8)
        self.cout = Wire()

        self.alu = ALU(
            a=self.a,
            b=self.b,
            op=self.op,
            cin=self.cin,
            out=self.out,
            cout=self.cout,
        )

    def test_and(self):
        self.inputs.reset()
        self.a.value = 3
        self.b.value = 6
        self.op.value = self.alu.OPCODE.AND
        self.cin.value = False

        self.assertEqual(self.out.value, 2)

    def test_add(self):
        self.inputs.reset()
        self.a.value = 42
        self.b.value = 17
        self.op.value = self.alu.OPCODE.ADD
        self.cin.value = False

        self.assertEqual(self.out.value, 59)

    def test_sub(self):
        self.inputs.reset()
        self.a.value = 42
        self.b.value = 17
        self.op.value = self.alu.OPCODE.A_MINUS_B
        self.cin.value = True # TODO: HOW TO ENFORCE THIS?

        self.assertEqual(self.out.value, 25)

    # TODO: many other opcodes...
