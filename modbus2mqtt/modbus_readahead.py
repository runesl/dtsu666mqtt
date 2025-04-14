import minimalmodbus
import struct

class ModbusReadahead():
    cache = {}

    def __init__(self, instrument):
        self.instrument = instrument

    def read_float(self, address):
        if address in self.cache:
            return self.cache[address]
        return self.instrument.read_float(address, 3)

    def read_float_ahead(self, address, regs):
        registers = self.instrument.read_registers(address, number_of_registers=regs*2, functioncode=3)
        floats = [
            struct.unpack('>f', struct.pack('>HH', registers[i], registers[i+1]))[0]
            for i in range(0, regs*2, 2)
        ]
        # return the first and cache the rest
#        print(f"read ahead {address} {regs} {registers} {floats}")
        for i in range(1, regs):
            self.cache[address+2*i] = floats[i]
 #           print(f"cache {self.cache}")
