import unittest
from circuit import Wire, Bus, TRUE, FALSE, reset_globals
from circuit.sequential import Register8, Counter8, RAM


class Register8Test(unittest.TestCase):
    def setUp(self):
        reset_globals()

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
    def setUp(self):
        reset_globals()

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


class RAMTest(unittest.TestCase):
    def setUp(self):
        reset_globals()

        self.addr = Bus(8)
        self.din = Bus(8)
        self.dout = Bus(8)
        self.write_pin = Wire()
        self.ram = RAM(
            inp=self.din, 
            out=self.dout, 
            addr=self.addr, 
            write=self.write_pin
        )

    def reset(self):
        self.addr.reset()
        self.din.reset()
        self.write_pin.reset()

    def write(self, address, value):
        self.reset()
        self.din.value = value
        self.addr.value = address
        self.write_pin.value = True

    def read(self, address):
        self.reset()
        self.din.value = 0
        self.addr.value = address
        self.write_pin.value = False

        return self.dout.value

    def test_ram(self):
        self.assertEqual(self.read(0), 0)
        self.write(0, 42)
        self.assertEqual(self.read(0), 42)
        self.write(1, 17)
        self.write(2, 255)
        self.assertEqual(self.read(0), 42)
        self.assertEqual(self.read(1), 17)
        self.assertEqual(self.read(2), 255)

        self.write(255, 128)
        self.write(16, 10)
        self.assertEqual(self.read(255), 128)
        self.assertEqual(self.read(1), 17)
        self.assertEqual(self.read(2), 255)
        self.assertEqual(self.read(16), 10)

        # print(self.ram.hex_dump())


    @unittest.skip
    def test_ram_heavy(self):
        for i in range(256):
            self.write(i, i)

        for i in range(256):
            self.assertEqual(self.read(i), i)

        # print()
        # print(self.ram.hex_dump())



