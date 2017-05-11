#!/usr/bin/python

from myhdl import *
from pal import pal_sync

def test() :

    clk = Signal(False)
    rst = Signal(False)
    mix_sync = Signal(False)
    vs = Signal(False)
    hs = Signal(False)
    odd_even = Signal(False)

    dut = pal_sync(clk27_i = clk,
                   rst_i = rst,
                   mix_sync_o = mix_sync,
                   odd_even_o = odd_even,
                   vs_o = vs,
                   hs_o = hs)

    @always(delay(10))
    def gen_clk() :
        clk.next = not clk

    @instance
    def estim() :
        rst.next = True
        yield delay(20)
        rst.next = False
        yield vs.posedge
        yield vs.posedge
        yield vs.posedge
        raise StopSimulation

    return instances()

tb = traceSignals(test)
sim = Simulation(tb)
sim.run()

    
