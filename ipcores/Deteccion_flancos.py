"""
Deteccion de flancos
====================

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from FlipFlops import FD

Hi = True     # Niveles logicos
Lo = False

def detecta_flanco_bajada(clk_i, 
                          a_i, 
                          flanco_o) :
    """Este modulo genera un pulso sincronico, cuando detecta un flanco de bajada en a_i 

    :Parametros:            
        - `clk_i`    : entrada de clock
        - `a_i`      : senal de entrada
        - `flanco_o` : pulso de salida

    Funcionamiento::

                    _   _   _   _   _   _       _   _   _   _   _   _
        clk_i      | |_| |_| |_| |_| |_| | ... | |_| |_| |_| |_| |_| |
                 __________                             _____________
        a_i                |______________ ... ________|
                 ______________                             _________
        a_q                    |__________ ... ____________|
                            ___         
        flanco_o __________|   |__________ ... _______________________


    :Nota: a_i debe estar sincronica con el clk
                                     
    """

    a_q = Signal(Lo) 

    reg_a = FD(clk_i = clk_i, 
               d_i = a_i, 
               q_o = a_q)

    @always_comb
    def detecta_bajada() :
        flanco_o.next =  a_q & (not a_i)

    return instances()

##########################################################

def detecta_flanco_subida(clk_i, 
                          a_i, 
                          flanco_o) :
    """Este modulo genera un pulso sincronico, cuando detecta un flanco de subida en a_i 

    :Parametros:
        - `clk_i`    : entrada de clock
        - `a_i`      : senal de entrada
        - `flanco_o` : pulso de salida

    Funcionamiento::

                    _   _   _   _   _   _       _   _   _   _   _   _
        clk_i      | |_| |_| |_| |_| |_| | ... | |_| |_| |_| |_| |_| |
                 __________                             _____________
        a_i                |______________ ... ________|
                 ______________                             _________
        a_q                    |__________ ... ____________|
                                                        ___
        flanco_o _________________________ ... ________|   |_________

    :Nota: a_i debe estar sincronica con el clk
        
    """

    a_q = Signal(Lo) 

    reg_a = FD(clk_i = clk_i, 
               d_i = a_i, 
               q_o = a_q)

    @always_comb
    def detecta_subida() :
        flanco_o.next =  (not a_q) & a_i

    return instances()
