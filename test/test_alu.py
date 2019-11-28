import unittest

from circuit.kernel import Wire, Bus, Register, NAND, WireError
from circuit.alu import HalfAdder, FullAdder, Add8


class AdderTest(unittest.TestCase):
    def test_half_adder(self):
        a, b = inputs = Bus(2)
        s, c = outputs = Bus(2)

        HalfAdder(a=a, b=b, s=s, c=c)

        for x in [0, 1]:
            for y in [0, 1]:
                inputs.reset()
                a.value = bool(x)
                b.value = bool(y)

                total = int(s.value)
                carry = c.value

                # print("test_half_adder", x, "+", y, "=", total, "C", carry)
                self.assertEqual((x+y)%2, total)
                self.assertIs((x+y)>1, carry)

    def test_full_adder(self):
        a, b, cin = inputs = Bus(3)
        s, cout = outputs = Bus(2)

        adder = FullAdder(a=a, b=b, cin=cin, s=s, cout=cout)

        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    inputs.reset()
                    a.value = bool(x)
                    b.value = bool(y)
                    cin.value = bool(z)

                    total = int(s.value)
                    carry = cout.value

                    # print("test_full_adder", x, "+", y, "+", z, "=", total, "C", carry)
                    self.assertEqual((x+y+z)%2, total)
                    self.assertIs((x+y+z)>1, carry)


class Add8Test(unittest.TestCase):
    def test_add8(self):
        pass

