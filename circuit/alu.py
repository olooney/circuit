from .kernel import Wire, Bus, Component
from .logic_gates import *

class HalfAdder(Component):
    def __init__(self, a, b, s=None, c=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.s = self.output(s)
        self.c = self.output(c)

        XOR(a=self.a, b=self.b, out=self.s)
        AND(a=self.a, b=self.b, out=self.c)


class FullAdder(Component):
    def __init__(self, a, b, cin, s=None, cout=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.cin = self.input(cin)
        self.s = self.output(s)
        self.cout = self.output(cout)

        first_half = HalfAdder(a=self.a, b=self.b)
        second_half = HalfAdder(a=first_half.s, b=self.cin, s=self.s)
        OR(a=first_half.c, b=second_half.c, out=self.cout)


class Add8(Component):
    """
    Add two 8-bit unsigned integers. 

    Inputs `a` and `b` and output `c` must all be 8-bit busses. The first wire
    is the most significant bit and the 8th wire is the least. 
    
    If the result doesn't fit in 8 bits, the output carry flag `cout` will be
    set high, and the result in `s` will be the sum modulo 256. An input carry
    flag `cin` is also accepted, and the result in `s` is increased by 1 if the
    input carry flag is set. This allows for the addition of 16-bit or larger
    integers.

    This component can also be used for subtraction by first taking the two's
    complement of one of the inputs using the `Not8` component.
    """
    def __init__(self, a, b, cin, s=None, cout=None):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.cin = self.input(cin)
        self.s = self.output(s, 8)
        self.cout = self.output(cout)

        adder = FullAdder(
            a=self.a[7], 
            b=self.b[7], 
            cin=self.cin,
            s=self.s[7],
        )
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
        super().__init__()
        self.inp = self.input(inp, 8)
        self.out = self.output(out, 8)

        for i in range(0, 8):
            NOT(inp=self.inp[i], out=self.out[i])


class And8(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.out = self.output(out, 8)

        for i in range(0, 8):
            AND(a=self.a[i], b=self.b[i], out=self.out[i])


class Mux8(Component):
    def __init__(self, a, b, select, out=None):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.select = self.input(select)
        self.out = self.output(out, 8)

        # TODO: could save some transistors by reusing NOT(select)...
        for i in range(8):
            Mux(
                a=self.a[i], 
                b=self.b[i],
                select=self.select,
                out=self.out[i]
            )
            

class ALU(Component):
    """
    Arithmetic/Logic Unit.

    It turns out we can cover a large number of cases with relatively few
    transisters by leveraging de Morgan's laws.
    """

    class OPCODE:
        AND = 0
        NAND = 32
        OR = 224
        NOR = 192
        ADD = 4
        A_MINUS_B = 68
        B_MINUS_A = 132
        NEGATIVE_A = 140
        NEGATIVE_B = 84
        INC_A = 236
        INC_B = 244

    def __init__(
        self,
        a,
        b,
        op,
        out
    ):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.op = self.input(op, 8)

        self.na = self.op[0]   # negate A
        self.nb = self.op[1]   # negate B
        self.nout = self.op[2] # negate OUT
        self.za = self.op[3]   # zero A
        self.zb = self.op[4]   # zero B
        self.arithmetic = self.op[5]  # 0 for AND, 1 for ADD
        # last two bits reserved

        self.out = self.output(out)
        
        zero = Bus([Wire(False, hard=True) for i in range(8)])

        # Optionally zero-out and/or negate input A
        a2 = Mux8(self.a, zero, self.za).out
        a3 = Mux8(a2, Not8(a2).out, self.na).out

        # Optionally zero-out and/or negate input B
        b2 = Mux8(self.b, zero, self.zb).out
        b3 = Mux8(b2, Not8(b2).out, self.nb).out

        # Do either Arithmetic or Logic
        out = Mux8(
            a=And8(a3, b3).out,
            b=Add8(a3, b3).out,
            select=self.arithmetic
        ).out

        # Optionally negate the output
        Mux8(
            a=out,
            b=Not8(out),
            select=self.nout,
            out=self.out
        )


# TODO: left/right shift/rotate
