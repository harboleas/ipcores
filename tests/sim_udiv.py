# generacion del VCD 

from myhdl import *
from udiv import udiv


def sim_udiv() :
    
    clk = Signal(False)
    rst = Signal(False)
    start = Signal(False)
    done = Signal(False)
    div0 = Signal(False)
    
    a = Signal(intbv(24)[5:])
    b = Signal(intbv(5)[3:])

    q = Signal(intbv(0)[5:])
    r = Signal(intbv(0)[5:])

    dut = udiv(clk_i = clk, 
               rst_i = rst,
               start_i = start,
               a_i = a,
               b_i = b,
               q_o = q,
               r_o = r,
               done_o = done,
               div0_o = div0)

    @always(delay(10))
    def clk_gen() :
        clk.next = not clk

    @instance
    def stimulus() :
        yield delay(35)
        start.next = True
        yield clk.posedge
        start.next = False
        yield done.negedge
        yield clk.posedge
        raise StopSimulation

    return instances()

Simulation(traceSignals(sim_udiv)).run()

# vim: set ts=8 sw=4 tw=0 et :
