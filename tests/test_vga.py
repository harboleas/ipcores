#!/usr/bin/python
# Genera VCD para el vga sync generator

from myhdl import *
from vga_sync import vga_sync

def test() :

    # Signals
    clk = Signal(False)
    rst = Signal(False)
    hs = Signal(False)
    vs = Signal(False)
    act_vid = Signal(False)
    x = Signal(intbv(0, 0, 800))
    y = Signal(intbv(0, 0, 600))

    dut = vga_sync(clk50_i = clk,
                   rst_i = rst,
                   hs_o = hs,
                   vs_o = vs,
                   act_vid_o = act_vid,
                   x_o = x,
                   y_o = y)

    @always(delay(10))
    def clk_gen() :
        clk.next = not clk

    @instance
    def estimulos() :
        yield delay(50)
        rst.next = True
        yield delay(10)
        rst.next = False
        yield vs.negedge
        yield vs.negedge
        raise StopSimulation

    return instances()


Simulation(traceSignals(test)).run()

#  vim: set ts=8 sw=4 tw=0 et :
