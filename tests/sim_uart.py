#!/usr/bin/python
from myhdl import *
from uart import uart_tx, uart_rx

def sim_uart() :

    clk = Signal(False)
    rst = Signal(False)
    par = Signal(intbv(0)[2:])
    data = Signal(intbv(0)[8:])
    data_rx = Signal(intbv(0)[8:])
    done = Signal(False)
    ready = Signal(False)
    start = Signal(False)
    tx = Signal(False)
    rx = Signal(False)
    frame_err = Signal(False)
    par_err = Signal(False)

    sim_tx = uart_tx(clk_i = clk,
                     rst_i = rst,
                     par_i = par,
                     data_i = data,
                     start_i = start,
                     tx_o = tx,
                     done_o = done)

    @always_comb
    def tx_rx() :
        rx.next = tx

    sim_rx = uart_rx(clk_i = clk,
                     rst_i = rst,
                     par_i = par,
                     rx_i = rx,
                     ready_o = ready,
                     data_o = data_rx,
                     frame_err_o = frame_err,
                     par_err_o = par_err)


    @always(delay(10))
    def clk_gen() :
        clk.next = not clk

    @instance
    def stimulus() :
        rst.next = True
        par.next = 2
        yield delay(30)
        rst.next = False
        data.next = 10
        yield clk.posedge
        start.next = True
        yield clk.posedge
        start.next = False
        yield ready.negedge
        yield done.negedge
        raise StopSimulation

    return instances()

Simulation(traceSignals(sim_uart)).run()

# vim: set ts=8 sw=4 tw=0 et :
