"""
CircuitError, WireError, etc: exception classes for circuit simulation errors.

Wire and Bus: used to propagate Boolean values between components.

Component: Abstract Base Class for all components.

NAND: the primitive used to implement all other combinatorial logic.

Register: a 1-bit register that can store a single Boolean value across clock
cycles. This is the primitive used to implement all sequential logic.

"""

class CircuitError(Exception):
    pass


class WireError(CircuitError):
    pass


class Wire:
    def __init__(self, value=None, hard=False):
        self.downstream_components = []
        if value is not None:
            value = bool(value)
        self._value = value
        self.hard = bool(hard)
        if self.hard and self._value is None:
            raise WireError("a hardwired value must be True or False, not None.")
        self.already_reset = False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.hard:
            raise WireError("A hardwired value can never be set.")

        if self._value is not None:
            if value != self._value:
                raise WireError("Wire set to conflicting value.")
        if value is True or value is False:
            self._value = value
            self.propagate()
        else:
            raise WireError("Use reset() to clear wire.")

    def reset(self):
        if not self.already_reset:
            self.already_reset = True
            if self.value is not None and not self.hard:
                self._value = None
            for component in self.downstream_components:
                component.reset()

    def propagate(self):
        self.already_reset = False
        for component in self.downstream_components:
            component.propagate()

    def connect(self, component):
        self.downstream_components.append(component)


TRUE = Wire(value=True, hard=True)
FALSE = Wire(value=False, hard=True)

def reset_globals():
    TRUE.downstream_components = []
    FALSE.downstream_components = []


class Bus(Wire):
    """
    A bus is simply a bundle of parallel wires. It implements the
    Aggregate pattern with respect to Wire, and supports all the same
    reset(), propagate(), and connect() methods, delegating to each
    constituent wire in each case.
    
    It's value is an unsigned integer where each bit corresponds with one wire,
    with the most significant bit being the first wire, and the least
    significant bit being the last wire.
    """

    def __init__(self, wires):
        """
        Initialize either from an iterable of wires
        or from an integer representing the number
        of wires in the bus. If any of the elements
        of the iterable are None, they will be 
        initialized as new Wire objects.
        """
        try:
            def as_wire(wire):
                if wire is None:
                    return Wire()
                if type(wire) == bool:
                    return Wire(wire)
                return wire

            self.wires = tuple( as_wire(w) for w in wires )
        except TypeError:
            self.wires = tuple( Wire() for w in range(wires) )

    def __len__(self):
        return len(self.wires)

    def __getitem__(self, index):
        return self.wires[index]

    def __iter__(self):
        yield from self.wires

    def propagate(self):
        for wire in self.wires:
            wire.propagate()

    def reset(self):
        for wire in self.wires:
            wire.reset()

    def connect(self, component):
        for wire in self.wires:
            wire.connect(component)

    @property
    def value(self):
        if any(wire.value is None for wire in self.wires):
            return None

        value = 0
        for wire in self.wires:
            value <<= 1
            if wire.value is True:
                value += 1
        return value

    @value.setter
    def value(self, value):
        for wire in reversed(self.wires):
            wire.value = bool(value % 2)
            value >>= 1


class Component:
    """
    A component is simply a number of input and output
    pins (Wires) which internally are wired together
    from simplier constituent Components.
    """
    def __init__(self):
        self.inputs = []
        self.outputs = []

    def input(self, wire, bus_length=None):
        if bus_length is not None:
            if len(wire) != bus_length:
                raise CircuitError(f"input wire to {self} must be a Bus of length {bus_length}.")
        self.inputs.append(wire)
        wire.connect(self)
        return wire

    def output(self, wire, bus_length=None):
        if wire is None:
            if bus_length is None:
                out = Wire()
            else:
                out = Bus(bus_length)
        else:
            out = wire

        if bus_length is not None:
            if len(out) != bus_length:
                raise CircuitError(f"output wire from {self} must be a Bus of length {bus_length}.")

        self.outputs.append(out)
        return out

    def propagate(self):
        pass

    def reset(self):
        pass


class NAND(Component):
    """
    NAND is only "atomic" Component necessary to implement all of combinational
    logic. It has two input pins `a` and `b`, and an output pin `out`. The value
    of `out` will be set as soon as it can be determined from `a` and `b`. The
    output value will be False if and only if both inputs are True.
    """
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)

    def propagate(self):
        if self.out.value is not None:
            return

        if self.a.value is False:
            self.out.value = True
        elif self.b.value is False:
            self.out.value = True
        elif self.a.value is True and self.b.value is True:
            self.out.value = False

    def reset(self):
        super().reset()
        for wire in self.outputs:
            wire.reset()


class Register(Component):
    """
    The Register is the only "stateful" Component necessary to implement all
    of sequential logic. It's output is always determined from previous clock
    cycles.
    """
    def __init__(self, inp, enable, out=None):
        super().__init__()
        self.inp = self.input(inp)
        self.enable = self.input(enable)
        self.out = self.output(out)

        self.state = False
        self.next_state = False
        self.already_reset = False

    def propagate(self):
        self.already_reset = False

        # capture the next state if enabled
        if self.enable.value is True and self.inp.value is not None:
            self.next_state = self.inp.value
        else:
            self.next_state = self.state

        # always propogate the current value, but only once
        if self.out.value is None:
            self.out.value = self.state

    def reset(self):
        if not self.already_reset:
            # propagate the reset
            self.state = self.next_state
            self.already_reset = True
            for wire in self.outputs:
                wire.reset()

