Circuit
=======

Circuit - a digital circuit simulator and simple computer.

About
-----

Digital circuits are comprised of `Component`s connected by `Wire`s. The point
of contact between a `Component` and a `Wire` is informally refered to as a
"pin", but there is no Pin class.

When many parallel `Wire`s are needed, they can be bundled together into a Bus. A
Bus does nothing helps with organization.

At any moment in time, a `Wire` has exactly one of three values: `True`, `False`, or
`None`, corresponding to high, low, or floating in an electronic digital circuit.

A `Component` has a number of input pins and output pins, which it treats
differently.  Each pin may either be a `Wire` or a `Bus` of a certain fixed size.
It is an error to pass a `Wire` where a `Bus` is expected, or vice versa, or to
pass a `Bus` of the wrong length. When a `Component` is instantiated, the correct
type of `Wire` or `Bus` MUST be passed for every input pin. `Wire`s or `Bus`es for
output pins MAY also be passed in (and will be wired up if they are) but are
optional and will be created as needed.

Unlike real-world wires, `Wire`s have a direction. When a `Wire` is connected to a
component, it knows whether its being connected to an input pin or an output
pin.  A Wire only keeps track of which components it is connected to via input
pins; these are its "downstream components."  

A single clock cycle consists of two phases: reset and propagate. In the reset
phase, `Wire`s will have their values returned to `None`; the only exceptions
are hardwired values permanently like `circuit.TRUE` and `circuit.FALSE`, and
`Register`s which retain their state from the previous clock cycle. 

Specifically, when `.reset()` or `.propagate()` is invoked on the `Wire`, the
same method is invokved on all downstream components. Similarly, when
`.reset()` or `.propagate()` is called on a primitive `Component`, the same
method will be invoked on all output pins. In this way, both types of signals
will propagate through the entire graph of the circuit, stopping only once
every reachable `Wire` and `Component` has been updated.

There are only two primitive `Component`s which "really" do anything: `NAND`
and `Register`. All other `Component`s are simply collections of simpler
components wired together in a particular way to the desired effect. These two
primitives, the base-class for user-defined Components, the Wire and Bus
classes, the hard-coded `circuit.TRUE` and `circuit.FALSE` constant `Wire`s,
and the package specific Exceptions which form the irreducable core of the
digital logic simulator are found in `circuit.kernel`. 

`circuit.logic_gates` provides basic implementations of common unary,
binary, and trinary logic gates, such as `NOT`, `XOR`, and `Mux`. 

`circuit.combinational` provdes more advanced combinational (stateless)
components implemented purely in terms of `NAND` - `Register` is not used.
These are mainly 8-bit arithmetic and bitwise logic operators.

`cicuit.sequential` provdes sequential (stateful) components which
use Registers, such as an 8-bit Register class, a 8-bit counter, `RAM`, etc.

`cicuit.cpu` provdes the controller and `CPU` for a simple 8-bit computer.

All components are imported into the top-level `circuit` namespace, so it is
not necessary to distinguish which submodule a particular `Component` lives in
when using the `circuit` package. This internal structure helps with code
organization and dependency management during development.


Running Tests
-------------

    pip install -e .
    cd circuit
    python -m unittest

