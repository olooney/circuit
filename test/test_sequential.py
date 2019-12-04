import unittest
from circuit import Wire, Bus, TRUE, FALSE
from circuit.sequential import Register8, Counter8


class Register8Test(unittest.TestCase):
    def test_register8(self):
        inp = Bus(8)
        enable = Wire()
        out = Bus(8)
        register = Register8(inp, enable, out)

        inp.reset(), enable.reset()
        inp.value = 13
        enable.value = False
        self.assertEqual(out.value, 0, "initialized to zero after not getting set")

        inp.reset(), enable.reset()
        inp.value = 42
        enable.value = True
        self.assertEqual(out.value, 0, "still zero after getting set!")

        inp.reset(), enable.reset()
        inp.value = 27
        enable.value = False
        self.assertEqual(out.value, 42, "Now 42 because was set on previous clock cycle.")

        inp.reset(), enable.reset()
        inp.value = 111
        enable.value = False
        self.assertEqual(out.value, 42, "Still 42 because was set earlier.")

        inp.reset(), enable.reset()
        inp.value = 255
        enable.value = True
        self.assertEqual(out.value, 42, "Still 42 but not for long.")

        inp.reset(), enable.reset()
        inp.value = 100
        enable.value = True
        self.assertEqual(out.value, 255, "Now 255, not 100")


@unittest.skip
class Counter8Test(unittest.TestCase):
    def test_counter8(self):
        enable = Wire()
        counter = Counter8(
            enable=enable,
            reset=FALSE
        )
        enable.reset()
        enable.value = True

        for i in range(260):
            enable.reset()
            enable.value = True
            self.assertEqual(counter.out.value, i)

    def test_enable(self):
        pass # TODO

    def test_reset(self):
        pass # TODO
