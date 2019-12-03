from .kernel import Wire, Bus, Component, TRUE, FALSE
from .logic_gates import *

# constant 8-bit zero (all bits 0)
ZERO = Bus([FALSE for i in range(8)])

class HalfAdder(Component):
    def __init__(self, a, b, out=None, c=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)
        self.c = self.output(c)

        XOR(a=self.a, b=self.b, out=self.out)
        AND(a=self.a, b=self.b, out=self.c)


class FullAdder(Component):
    def __init__(self, a, b, cin, out=None, cout=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.cin = self.input(cin)
        self.out = self.output(out)
        self.cout = self.output(cout)

        first_half = HalfAdder(a=self.a, b=self.b)
        second_half = HalfAdder(a=first_half.out, b=self.cin, out=self.out)
        OR(a=first_half.c, b=second_half.c, out=self.cout)


class Add8(Component):
    """
    Add two 8-bit unsigned integers. 

    Inputs `a` and `b` and output `c` must all be 8-bit busses. The first wire
    is the most significant bit and the 8th wire is the least. 
    
    If the result doesn't fit in 8 bits, the output carry flag `cout` will be
    set high, and the result in `out` will be the sum modulo 256. An input carry
    flag `cin` is also accepted, and the result in `out` is increased by 1 if the
    input carry flag is set. This allows for the addition of 16-bit or larger
    integers.

    This component can also be used for subtraction by first taking the two's
    complement of one of the inputs using the `Not8` component.
    """
    def __init__(self, a, b, cin, out=None, cout=None):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.cin = self.input(cin)
        self.out = self.output(out, 8)
        self.cout = self.output(cout)

        adder = FullAdder(
            a=self.a[7], 
            b=self.b[7], 
            cin=self.cin,
            out=self.out[7],
        )
        for i in range(6, -1, -1):
            adder = FullAdder(
                a=self.a[i], 
                b=self.b[i], 
                cin=adder.cout, 
                out=self.out[i], 
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


class LeftShift8(Component):
    """
    Implements `a << b`, shifting `a` by a number of bits controlled by `b`. 
    
    Since we are working with 8 bits, only the three least significant bits do
    "real" shifts, and if any of the 5 most significant bits are set then the
    entire number will be shifted away and we'll be left with zero.
    """
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.out = self.output(out, 8)

        # b's bottom 3 bits drive the barrel shifter.
        barrel = Mux8(
            a=self.a,
            b=Bus(self.a[1:8] + ZERO[0:1]),
            select=self.b[7] # ones place of b
        ).out

        barrel = Mux8(
            a=barrel,
            b=Bus(barrel[2:8] + ZERO[0:2]),
            select=self.b[6] # twos place of b
        ).out

        barrel = Mux8(
            a=barrel,
            b=Bus(barrel[4:8] + ZERO[0:4]),
            select=self.b[5] # fours place of b
        ).out

        # check if any of b's top five bits are set.
        any_high_bit = OR(
            OR(
                OR(self.b[0], self.b[1]).out,
                OR(self.b[2], self.b[3]).out
            ).out,
            self.b[4]
        ).out

        # return 0 if b >= 8, otherwise return
        # the result from the barrel shifter.
        Mux8(
            a=barrel,
            b=ZERO,
            select=any_high_bit,
            out=self.out
        )


class Mux8(Component):
    """
    8-bit Multiplexer.

    Selects one of two 8-bit inputs controlled by a single `select` pin.
    """
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
        cin,
        out,
        cout
    ):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.op = self.input(op, 8)
        self.cin = self.input(cin)

        self.na = self.op[0]   # negate A
        self.nb = self.op[1]   # negate B
        self.nout = self.op[2] # negate OUT
        self.za = self.op[3]   # zero A
        self.zb = self.op[4]   # zero B
        self.arithmetic = self.op[5]  # 0 for AND, 1 for ADD
        # last two bits reserved

        self.out = self.output(out, 8)
        self.cout = self.output(cout)
        
        # Optionally zero-out and/or negate input A
        a2 = Mux8(self.a, ZERO, self.za).out
        a3 = Mux8(a2, Not8(a2).out, self.na).out

        # Optionally zero-out and/or negate input B
        b2 = Mux8(self.b, ZERO, self.zb).out
        b3 = Mux8(b2, Not8(b2).out, self.nb).out

        # Do either Arithmetic or Logic
        a_and_b = And8(a=a3, b=b3).out
        a_plus_b = Add8(a=a3, b=b3, cin=self.cin, cout=self.cout).out

        result = Mux8(
            a=a_and_b,
            b=a_plus_b,
            select=self.arithmetic
        ).out

        # Optionally negate the output
        Mux8(
            a=result,
            b=Not8(inp=result).out,
            select=self.nout,
            out=self.out
        )


# TODO: left/right shift/rotate
