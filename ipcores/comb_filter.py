"""
Filtro peine
============

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from Memorias import FIFO

Hi = True      # Niveles logicos
Lo = False

def comb_filter(clk_i, 
                ce_i, 
                dato_i, 
                dato_filtrado_o, 
                RETARDO) :
    """Filtro peine (comb filter)

    ::

                       ___________
               _______|           |_______
       dato_i  __   __|   Delay   |_____  |
                 | |  |___________|     | |
                 | |                   _|_|_     _____
                 | |__________________|     |___|     |__
                 |____________________|  +  |___| / 2 |__ dato_filtrado_o                        
                                      |_____|   |_____|


    """

    n = len(dato_i)
    dato_delay = Signal(intbv(0)[n:])
    dato_aux_x2 = Signal(intbv(0)[n+1:])

    retardo = FIFO(clk_i = clk_i, 
                   ce_i = ce_i, 
                   d_i = dato_i, 
                   q_o = dato_delay, 
                   k = RETARDO)

    @always_comb
    def sumador() :
        dato_aux_x2.next = dato_i + dato_delay

    @always_comb
    def divisor_x2() :
        dato_filtrado_o.next = dato_aux_x2 >> 1

    return instances()

