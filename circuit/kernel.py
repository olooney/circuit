"""
Wire and Component, plus the magic NAND.
TODO: Register, Bus
"""

class CircuitError(Exception):
    pass

class WireError(CircuitError):
    pass


class Wire:
    def __init__(self, value=None):
        self.downstream_components = []
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value is not None:
            if value != self._value:
                raise WireError("Wire set to conflicting value.")
        if value is True or value is False:
            self._value = value
            self.propagate()
        else:
            raise WireError("Use reset() to clear wire.")

    def reset(self):
        if self.value is not None:
            self._value = None
            for component in self.downstream_components:
                component.reset()

    def propagate(self):
        for component in self.downstream_components:
            component.propagate()

    def connect(self, component):
        self.downstream_components.append(component)


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
            wires.connect(component)

    @property
    def value(self):
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

    def input(self, wire):
        self.inputs.append(wire)
        wire.connect(self)
        return wire

    def output(self, wire):
        if wire is None:
            out = Wire()
        else:
            out = wire
        self.outputs.append(out)
        return out

    def propagate(self):
        pass

    def reset(self):
        for wire in self.outputs:
            wire.reset()


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
        self.next_state = None

    def propagate(self):
        # capture the next state if enabled
        if self.enable.value is True and self.inp.value is not None:
            self.next_state = self.inp.value

        # always propogate the current value
        if self.out.value is None:
            self.out.value = self.state

    def reset(self):
        # update internal state if appropriate
        if self.next_state is not None:
            self.state = self.next_state
            self.next_state = None

        super().reset()

