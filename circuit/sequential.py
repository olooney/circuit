"""
Sequential logic is based on the stateful Register primitive.
"""
from .kernel import Component, Register, Wire, Bus, TRUE, FALSE
from .alu import Add8, Mux8, ZERO

class Register8(Component):
    def __init__(self, inp, enable, out=None):
        super().__init__()
        self.inp = self.input(inp, 8)
        self.enable = self.input(enable)
        self.out = self.output(out, 8)

        for i in range(8):
            Register(
                inp=self.inp[i],
                enable=self.enable,
                out=self.out[i]
            )


class Counter8(Component):
    def __init__(self, enable, zero, out=None):
        super().__init__()
        self.enable = self.input(enable)
        self.zero = self.input(zero)
        self.out = self.output(out, 8)

        # this will feed back into the register
        # after the increment/reset logic.
        loopback = Bus(8)

        Register8(
            inp=loopback,
            enable=TRUE,
            out=self.out
        )

        # setting the carry bit is an easy way to pass a single bit
        # into Add8. Much easier than having b=Mux8(ZERO, ONE).
        incremented = Add8(
            a=self.out,
            b=ZERO,
            cin=self.enable
        ).out

        # cycle all the way back to zero if reset is high.
        Mux8(
            a=incremented,
            b=ZERO,
            select=self.zero,
            out=loopback
        )


