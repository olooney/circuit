import unittest 
from circuit.kernel import Wire, Bus, Register, NAND, WireError

class TestWire(unittest.TestCase):
    def test_wire(self):
        wire = Wire()
        self.assertIs(wire.value, None)
        wire.value = True
        self.assertIs(wire.value, True)
        with self.assertRaises(WireError):
            wire.value = False
        wire.reset()
        self.assertIs(wire.value, None)
        wire.value = False
        self.assertIs(wire.value, False)


class TestBus(unittest.TestCase):
    def test_init_from_wires(self):
        ones = Wire(True)
        twos = Wire(False)
        fours = Wire(False)
        eights = Wire(True)
        bus = Bus([ones, twos, fours, eights])
        self.assertEqual(len(bus), 4)
        self.assertEqual(bus.value, 9)

    def test_init_from_bool(self):
        bus = Bus([False, True, False, True])
        self.assertEqual(len(bus), 4)
        self.assertEqual(bus.value, 5)

        bus = Bus([True, False, True, False])
        self.assertEqual(len(bus), 4)
        self.assertEqual(bus.value, 10)

        bus = Bus([True, False, False, False, False])
        self.assertEqual(len(bus), 5)
        self.assertEqual(bus.value, 16)

        bus = Bus([False, False, True])
        self.assertEqual(len(bus), 3)
        self.assertEqual(bus.value, 1)

    def test_init_from_length(self):
        bus = Bus(4)
        self.assertEqual(len(bus), 4)
        self.assertEqual(bus.value, 0)
        for wire in bus:
            wire.value = True
        self.assertEqual(bus.value, 15)

    def test_set_value(self):
        bus = Bus(4)
        bus.value = 5
        self.assertEqual(bus[0].value, False)
        self.assertEqual(bus[1].value, True)
        self.assertEqual(bus[2].value, False)
        self.assertEqual(bus[3].value, True)

        bus.reset()

        bus.value = 14
        self.assertEqual(bus[0].value, True)
        self.assertEqual(bus[1].value, True)
        self.assertEqual(bus[2].value, True)
        self.assertEqual(bus[3].value, False)


class TestRegister(unittest.TestCase):
    def test_stateful(self):

        inp, enable = Wire(), Wire()
        register = Register(inp=inp, enable=enable)
        out = register.out
        
        self.assertIs(out.value, None)
        register.propagate()
        self.assertIs(out.value, False)
        
        inp.value = True
        enable.value = True
        self.assertIs(out.value, False)

        inp.reset()
        enable.reset()

        self.assertIs(out.value, None)

        inp.value = False
        enable.value = False

        self.assertIs(out.value, True)

        inp.reset()
        enable.reset()

        self.assertIs(out.value, None)

        inp.value = False
        enable.value = True

        self.assertIs(out.value, True)

        inp.reset()
        enable.reset()
        register.propagate()

        self.assertIs(out.value, False)

# TODO: TestNAND
