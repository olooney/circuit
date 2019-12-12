"""
An 8-bit computer.
"""
from circuit.kernel import Wire, Bus, Component, Register, TRUE, FALSE
from circuit.logic_gates import NOT
from circuit.combinational import ALU, Mux8, ZERO
from circuit.sequential import Register8, Counter8, RAM

__all__ = [
    "Controller",
    "CPU",
]


def constant(value, bits=8):
    wires = []
    for i in range(bits):
        wire = TRUE if (value & 1) else FALSE
        value = (value >> 1)
        wires.insert(0, wire)
    
    return Bus(wires)


class Mux8X4(Component):
    def __init__(
        self,
        a,
        b,
        c,
        d,
        select,
        out = None
    ):
        super().__init__()
        self.a = self.input(a, 8)
        self.b = self.input(b, 8)
        self.c = self.input(c, 8)
        self.d = self.input(d, 8)
        self.select = self.input(select, 2)
        self.out = self.output(out, 8)

        Mux8(
            Mux8(self.a, self.b, select=self.select[1]).out,
            Mux8(self.c, self.d, select=self.select[1]).out,
            select=self.select[0],
            out=self.out,
        )



class Controller(Component):
    def __init__(
        self, 
        fetch_execute, 
        pc_enable=None,
        pc_data=None,
        alu_op=None,
        alu_a_select=None,
        alu_b_select=None
    ):
        super().__init__()
        self.fetch_execute = self.input(fetch_execute)

        self.alu_op = self.output(constant(ALU.OPCODE.INCA), 8) # increment "A"
        self.alu_a_select = self.output(constant(2, bits=2), 2) # select PC 
        self.alu_b_select = self.output(constant(2, bits=2), 2) # select PC



class CPU(Component):
    def __init__(self):
        super().__init__()

        # Clock drives the fetch/execute tic-toc
        self.clock = Counter8(enable=TRUE, zero=FALSE)
        self.execute_flag = self.clock.out[7]
        self.fetch_flag = NOT(self.execute_flag).out

        # 8-bit data bus with 8-bit addressing
        self.addr = Bus(8)
        self.din = Bus(8)
        self.dout = Bus(8)

        # 256 bytes of RAM on the bus
        self.ram = RAM(
            inp=self.dout,
            addr=self.addr,
            write=FALSE,
            out=self.din,
        )

        # Registers
        self.x = self.register(FALSE, FALSE)
        self.y = self.register(FALSE, FALSE)
        self.pc = self.register(FALSE, self.fetch_flag)
        self.op = self.register(TRUE, self.fetch_flag)

        # Addressing Mode
        self.addr_mode = self.register_select(
            select=constant(2, 2), # PC
            out=self.addr,
        )

        # ALU
        self.a = self.register_select(constant(2, 2)) # PC
        self.b = self.register_select(constant(0, 2)) # Not used
        self.alu = ALU(
            a=self.a.out,
            b=self.b.out,
            cin=FALSE,
            op=constant(ALU.OPCODE.INCA),
            out=self.dout
        )

    def register(self, data, enable):
        return Register8(
            inp=Mux8(
                #a=self.dout,
                a=constant(42),
                b=self.din,
                select=data
            ).out,
            enable=enable,
        )

    def register_select(self, select, out=None):
        return Mux8X4(
            a=self.x.out,
            b=self.y.out,
            c=self.pc.out,
            d=self.din,
            select=select,
            out=out
        )

    def hex_dump(self):
        x = int(self.x.state or 0)
        y = int(self.y.state or 0)
        pc = int(self.pc.state or 0)
        op = int(self.op.state or 0)
        clock = int(self.clock.out.value or 0)

        return "\n".join([
            f"CLOCK: {clock:02x}",
            f"X: {x:02x}         Y: {y:02x}        PC: {pc:02x}        OP: {op:02x}",
            "",
            self.ram.hex_dump(),
            ""
        ])
        
    


