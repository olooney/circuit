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
                raise("Wire set to conflicting value.")
        if value is True or value is False:
            self._value = value
            self.propogate()
        else:
            raise WireError("Use reset() to clear wire.")

    def reset(self):
        if self.value is not None:
            self._value = None
            for component in self.downstream_components:
                component.reset()

    def propogate(self):
        for component in self.downstream_components:
            component.propogate()

    def connect(self, component):
        self.downstream_components.append(component)


class Component:
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

    def propogate(self):
        pass

    def reset(self):
        for wire in self.outputs:
            wire.reset()


class NAND(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)

    def propogate(self):
        if self.out.value is not None:
            return

        if self.a.value is False:
            self.out.value = True
        elif self.b.value is False:
            self.out.value = True
        elif self.a.value is True and self.b.value is True:
            self.out.value = False
