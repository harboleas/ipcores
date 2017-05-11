"""
Program counter
===============

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""
from myhdl import *
from Contadores import CB_RLE
from Memorias import FILO

Hi = True
Lo = False

def pc(clk_i,
       rst_i,
       inc_pc_i,
       jmp_i,
       call_i,
       ret_i,
       pck_i,
       pc_o,
       stack_size) :

    """Program Counter
    ::

                
                                        .--------------------------------------.
                                        |                CB_RLE                |
                                        |                                      |
              pc_o <--------------------| q_o                             ce_i |<---- inc_pc_i
                             |          |                                      |
                             |          |      load_i               d_i        |
                             |          '--------------------------------------'
                             |                   ^                   ^
                             |                   |                   |
                             |                   |                   |
                             v                   '                 -----
                          .-----.     jmp_i | call_i | ret_i      /     \<----- ret_i
                          | +1  |                                /       \
                          '-----'                                ---------
                             |                                     ^   ^
                             |                         pck_i ------'   '----------
                             |                                                   |
                             |                                                   |
                             |              .------------------.                 |
                             |              |      stack       |                 |
                             |              |                  |                 |
                             '------------->| d_i         q_o  |-----------------'
                                            |                  |
                                            |                  |
                              call_i ------>| push_i           |
                                            |                  |
                               ret_i ------>| pop_i            |
                                            |                  |
                                            '------------------'

    """

    n = len(pck_i)

    # Senales

    mux_out = Signal(intbv(0)[n:])
    stack_in = Signal(intbv(0)[n:])
    stack_out = Signal(intbv(0)[n:])
    pc_q = Signal(intbv(0)[n:])

    j_c_r = Signal(Lo)    


    # Estructura

    contador = CB_RLE(clk_i = clk_i,
                      rst_i = rst_i,
                      load_i = j_c_r,
                      d_i = mux_out,
                      ce_i = inc_pc_i,
                      q_o = pc_q)


    @always_comb
    def OR() :
        j_c_r.next = jmp_i | call_i | ret_i

    
    @always_comb
    def suma_1() :
        stack_in.next = pc_q + 1   # Guarda la direccion de la instruccion siguiente para el retorno de un call

    @always_comb
    def conex() :
        pc_o.next = pc_q

    @always_comb
    def mux() :
        if ret_i :
            mux_out.next = stack_out
        else :
            mux_out.next = pck_i

    stack = FILO(clk_i = clk_i,
                 push_i = call_i,
                 pop_i = ret_i,
                 d_i = stack_in,
                 q_o = stack_out,
                 k = stack_size)       

    return instances()          
               
