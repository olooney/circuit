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


class Counter8Test(unittest.TestCase):
    def test_counter8(self):
        counter = Counter8(
            enable=TRUE,
            zero=FALSE
        )
        rails = Bus([TRUE, FALSE])

        for i in range(260):
            rails.reset()
            rails.propagate()

            # print("test_counter8", , counter.out.value)
            self.assertEqual(counter.out.value, i % 256)

    def test_enable(self):
        fizz_buzz = Wire()
        counter = Counter8(
            enable=fizz_buzz,
            zero=FALSE
        )
        rails = Bus([TRUE, FALSE])

        correct = 0
        for i in range(25):
            rails.reset()
            fizz_buzz.reset()
            rails.propagate()
            fizz_buzz.value = (i % 3 != 0) and (i % 5 != 0)

            # print("test_enable", i, counter.out.value, correct)
            self.assertEqual(counter.out.value, correct)

            if fizz_buzz.value is True:
                correct += 1

    def test_reset(self):
        reset_to_zero = Wire()
        counter = Counter8(
            enable=TRUE,
            zero=reset_to_zero
        )
        rails = Bus([TRUE, FALSE])

        for i in range(25):
            rails.reset()
            reset_to_zero.reset()
            reset_to_zero.value = (i == 9) or (i == 19)
            rails.propagate()

            # print("test_reset", i, counter.out.value, i % 10)
            self.assertEqual(counter.out.value, i % 10)
