from myhdl import *

from cpu.TZR1_core import TZR1
from cpu.fibo import program

Lo = False
Hi = True

def test() :

    clk = Signal(Lo)
    rst = Signal(Lo)
    wr = Signal(Lo)
    rd = Signal(Lo)
    addr = Signal(intbv(0)[8:])
    data_i = Signal(intbv(0)[8:])
    data_o = Signal(intbv(0)[8:])


    micro = TZR1(clk_i = clk,
                 rst_i = rst,
                 addr_o = addr,        
                 data_i = data_i,
                 data_o = data_o,
                 write_o = wr,
                 read_o = rd,
                 program = program)

    @always(delay(10))
    def gen_clk() :
        clk.next = not clk

    return instances()

tb = traceSignals(test)  # Genera el archivo vcd con todas las senales involucradas
sim = Simulation(tb)
sim.run(1000)    


