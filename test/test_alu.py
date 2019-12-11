import unittest

from circuit import Wire, Bus, Register, NAND, WireError, reset_globals
from circuit.alu import *


class AdderTest(unittest.TestCase):
    def setUp(self):
        reset_globals()

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
    def setUp(self):
        reset_globals()

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
        reset_globals()

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

    def assert_op(self, opcode, op, cin=False):
        nums = [0, 1, 2, 42, 77, 100, 127, 128, 196, 254, 255]

        for x in nums:
            for y in nums:
                self.inputs.reset()
                self.a.value = x
                self.b.value = y
                self.op.value = opcode
                self.cin.value = cin

                correct = op(x, y)
                # print(opcode, ":", x, y, "=", self.out.value, "/", correct)
                self.assertEqual(self.out.value, correct)

    def test_zero(self):
        self.assert_op(self.alu.OPCODE.ZERO, lambda a, b: 0)

    def test_one(self):
        self.assert_op(self.alu.OPCODE.ONE, lambda a, b: 1)

    def test_mone(self):
        self.assert_op(self.alu.OPCODE.MONE, lambda a, b: 255)
                
    def test_a(self):
        self.assert_op(self.alu.OPCODE.A, lambda a, b: a)

    def test_b(self):
        self.assert_op(self.alu.OPCODE.B, lambda a, b: b)

    def test_na(self):
        self.assert_op(self.alu.OPCODE.NA, lambda a, b: ~a % 256)

    def test_nb(self):
        self.assert_op(self.alu.OPCODE.NB, lambda a, b: ~b % 256)

    def test_and(self):
        self.assert_op(self.alu.OPCODE.AND, lambda a, b: a & b)

    def test_nand(self):
        self.assert_op(self.alu.OPCODE.NAND, lambda a, b: ~(a & b) % 256)

    def test_or(self):
        self.assert_op(self.alu.OPCODE.OR, lambda a, b: a | b)

    def test_nor(self):
        self.assert_op(self.alu.OPCODE.NOR, lambda a, b: ~(a | b) % 256)

    def test_ma(self):
        self.assert_op(self.alu.OPCODE.MA, lambda a, b: -a % 256)

    def test_mb(self):
        self.assert_op(self.alu.OPCODE.MB, lambda a, b: -b % 256)

    def test_add(self):
        self.assert_op(self.alu.OPCODE.ADD, lambda a, b: (a + b) % 256)

    def test_sub(self):
        self.assert_op(self.alu.OPCODE.SUB, lambda a, b: (a - b) % 256)

    def test_msub(self):
        self.assert_op(self.alu.OPCODE.MSUB, lambda a, b: (b - a) % 256)

    def test_inca(self):
        self.assert_op(self.alu.OPCODE.INCA, lambda a, b: (a +1) % 256)

    def test_deca(self):
        self.assert_op(self.alu.OPCODE.DECA, lambda a, b: (a - 1) % 256)

    def test_incb(self):
        self.assert_op(self.alu.OPCODE.INCB, lambda a, b: (b +1) % 256)

    def test_decb(self):
        self.assert_op(self.alu.OPCODE.DECB, lambda a, b: (b - 1) % 256)
