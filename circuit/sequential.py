"""
Sequential logic is based on the stateful Register primitive.
"""
from .kernel import Component, Register, Wire, Bus, TRUE, FALSE
from .combinational import Not8, Add8, Or8, Mux8, ZERO
from .logic_gates import AND

class Register8(Component):
    def __init__(self, inp, enable, out=None):
        super().__init__()
        self.inp = self.input(inp, 8)
        self.enable = self.input(enable)
        self.out = self.output(out, 8)

        self.bit_registers = [
            Register(
                inp=self.inp[i],
                enable=self.enable,
                out=self.out[i]
            )
            for i in range(8)
        ]

    @property
    def state(self):
        """
        For debugging purposes, this read-only
        property exposes the internal state of
        this register as an 8-bit unsigned integer.
        """
        value = 0
        for bit in self.bit_registers:
            value = (value << 1) + bit.state
        return value


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


class RAM(Component):
    """
    A very heavy component which implements an 8-bit addressable, 256 byte
    memory. This requires tens of thousands of NAND gates and 2048 registers.
    """
    def __init__(self, inp, addr, write, out=None):
        super().__init__()
        self.inp = self.input(inp, 8)
        self.addr = self.input(addr, 8)
        self.write = self.input(write)
        self.out = self.output(out, 8)

        self.not_addr = Not8(self.addr).out
        
        # 256 wires indicating if each register was selected. The same
        # wire controls both selection for both reading and writing. 
        self.selected = [
            self.matches_addr(i)
            for i in range(256)
        ]

        # 256 registers to hold the values in memory. 
        self.registers = [
            Register8(
                inp=self.inp,
                enable=AND(self.write, self.selected[i]).out
            )
            for i in range(256)
        ]

        # 255 of these outputs will be zero, and exactly one (the selected
        # register) may not be zero; that one contains the output value.
        outputs = [
            Mux8(
                a=ZERO,
                b=self.registers[i].out,
                select=self.selected[i]
            ).out
            for i in range(256)
        ]

        # Yikes, an inverse multiplexer sure needs a lot of transistors when
        # built out of binary gates... we need eight layers of 128, 64, 32, 16,
        # 8, 4, 2, and finally 1, for a total of 255 Or8 gates.
        while len(outputs) > 2:
            outputs = [
                Or8(left, right).out
                for left, right
                in zip(outputs[::2], outputs[1::2])
            ]
        # last layer is a special because we want to wire in the output gate.
        Or8(outputs[0], outputs[1], out=self.out)

    def matches_addr(self, index):
        """
        This implements a comparison between an 8-bit value `addr` known only
        at run time and a constant index known at compile time. We have both
        `addr` and its inverse `not_addr`. By choosing each bit either from
        `addr` or `not_addr`, we can build a single long AND expression
        requires all bits of `addr` to be exactly the same as the bits of
        index. This uses far fewer transistors than relying on the dynamic
        `Equal8(addr, index)` component.
        """
        a = [
            self.addr[j] if index & (128 >> j) else self.not_addr[j]
            for j in range(8)
        ]

        return AND(
            AND(
                AND(a[0], a[1]).out,
                AND(a[2], a[3]).out
            ).out,
            AND(
                AND(a[4], a[5]).out,
                AND(a[6], a[7]).out
            ).out,
        ).out

    def hex_dump(self):
        out = []
        for row in range(16):
            row_out = []
            for col in range(16):
                index = 16 * row + col
                state = self.registers[index].state
                hex_string = f"{state:02x}" if state is not None else "  "
                row_out.append(hex_string)
            out.append(" ".join(row_out))
        return "\n".join(out)
