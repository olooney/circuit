from .kernel import Wire, Bus, Component
from .logic_gates import NOT, AND, OR, XOR, NAND, NOR, XNOR

class HalfAdder(Component):
    def __init__(self, a, b, s=None, c=None):
        self.a = self.input(a)
        self.b = self.input(b)
        self.s = self.output(s)
        self.c = self.output(c)

        XOR(a=a, b=b, out=s)
        AND(a=a, b=b, out=c)


class FullAdder(Component):
    def __init__(self, a, b, cin, s=None, cout=None):
        self.a = self.input(a)
        self.b = self.input(b)
        self.cin = self.input(cin)
        self.s = self.output(s)
        self.cout = self.output(cout)

        first_half = HalfAdder(a=self.a, b=self.b)
        second_half = HalfAdder(a=first_half.out, b=self.cin, s=self.s)
        OR(a=first_half.c, b=second_half.c, out=self.cout)


class Add8(Component):
    def __init__(self, a, b, cin, s=None, cout=None):
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.cin = self.input(cin)
        self.s = self.output(s, 8)
        self.cout = self.output(cout)

        adder = FullAdder(a=self.a[7], b=self.b[7], cin=self.cin)
        for i in range(6, -1, -1):
            adder = FullAdder(
                a=self.a[i], 
                b=self.b[i], 
                cin=adder.cout, 
                s=self.s[i], 
                cout=self.cout if i == 0 else None,
            )


class Not8(Component):
    def __init__(self, inp, out=None):
        self.inp = self.input(inp, 8)
        self.out = self.output(out, 8)

        for i in range(0, 8):
            NOT(inp=self.inp[i], out=self.out[i])


class And8(Component):
    def __init__(self, a, b, out=None):
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.out = self.output(out, 8)

        for i in range(0, 8):
            AND(a=self.a[i], b=self.b[i], out=self.out[i])

# TODO: left/right shift/rotate
