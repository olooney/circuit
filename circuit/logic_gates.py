from .kernel import Wire, Component, NAND


class NOT(Component):
    def __init__(self, inp, out=None):
        super().__init__()
        self.inp = self.input(inp)
        self.out = self.output(out)
        
        NAND(a=self.inp, b=self.inp, out=self.out)


class AND(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)
        
        nand = NAND(a=a, b=b)
        NOT(inp=nand.out, out=self.out)


class OR(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)
        
        nand = NAND(
            a=NOT(self.a).out, 
            b=NOT(self.b).out, 
            out=self.out
        )


class NOR(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)
        
        a_or_b = OR(a=self.a, b=self.b).out
        NOT(inp=a_or_b, out=self.out)
    

class XOR(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)
        
        c = NAND(a=self.a, b=self.b).out
        d = OR(a=self.a, b=self.b).out
        AND(a=c, b=d, out=self.out)
        

class XNOR(Component):
    def __init__(self, a, b, out=None):
        super().__init__()
        self.a = self.input(a)
        self.b = self.input(b)
        self.out = self.output(out)
        
        c = NAND(a=self.a, b=self.b).out
        d = OR(a=self.a, b=self.b).out
        NAND(a=c, b=d, out=self.out)
