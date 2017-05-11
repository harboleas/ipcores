"""
Extremos
========

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from FlipFlops import FD_RE, FD_SE

Hi = True      # Niveles Logicos
Lo = False

##################################################################################################

def maximo(clk_i, 
           rst_i, 
           ce_i, 
           d_i, 
           maximo_o) :
    """Este modulo obtiene el valor maximo de una secuencia de datos tipo unsigned.
    A medida que la secuencia entra por d_i, el registro maximo_o refleja el valor maximo de
    la secuencia, desde el reset hasta el ultimo dato valido (ce_i)::

                        FD_RE                                          COMP
                    ______________                                  ___________
               ____|              |________________________________|           |
          d_i  ____| d          q |________________________________| A         |
                   |              |  | |                           |           |   
        clk_i  ----|> clk         |  | |                           |           |
                   |              |  | |                           |           |
         ce_i  ----| ce           |  | |                           |           |
                   |              |  | |                           |     A > B |----
        rst_i  ----| rst          |  | |                           |           |   |
                   |______________|  | |        FD_RE              |           |   |
                                     | |    ______________         |           |   |
                                     | |___|              |________|           |   |
                                     |_____| d          q |________| B         |   |
                                           |              |  | |   |___________|   |
                                clk_i  ----|> clk         |  | |                   |
                                           |              |  | |                   |
                            ---------------| ce           |  | |__                 |
                            |              |              |  |____ maximo_o        | 
                            |   rst_i  ----| rst          |                        |
                            |              |______________|                        | 
                            |                                                      |
                            |______________________________________________________|

    :Parametros:
        - `clk_i`    : entrada de clock
        - `rst_i`    : reset sincronico
        - `ce_i`     : dato valido (clock enable)
        - `d_i`      : entrada de datos
        - `maximo_o` : salida del maximo

    """
    
    n = len(d_i)

    A = Signal(intbv(0)[n:])
    B = Signal(intbv(0)[n:])

    A_May_B = Signal(Lo)

    reg_in = FD_RE(clk_i = clk_i, 
                   rst_i = rst_i, 
                   ce_i = ce_i, 
                   d_i = d_i, 
                   q_o = A)   # Registro de entrada de datos

    reg_max = FD_RE(clk_i = clk_i, 
                    rst_i = rst_i, 
                    ce_i = A_May_B, 
                    d_i = A, 
                    q_o = B)     # Registro de salida

    @always(A,B)
    def comparador() :     # Comparador
        if A > B :
            A_May_B.next = Hi
        else :
            A_May_B.next = Lo

    @always_comb
    def conex_max() :
        maximo_o.next = B

    return instances()

#########################################################################################
        
def minimo(clk_i, 
           rst_i, 
           ce_i, 
           d_i, 
           minimo_o) :
    """Este modulo obtiene el valor minimo de una secuencia de datos tipo unsigned.
    A medida que la secuencia entra por d_i, el registro minimo_o refleja el valor minimo de
    la secuencia, desde el reset hasta el ultimo dato valido (ce_i)::

                        FD_SE                                          COMP
                    ______________                                  ___________
               ____|              |________________________________|           |
          d_i  ____| d          q |________________________________| A         |
                   |              |  | |                           |           |   
        clk_i  ----|> clk         |  | |                           |           |
                   |              |  | |                           |           |
         ce_i  ----| ce           |  | |                           |           |
                   |              |  | |                           |     A < B |----
        rst_i  ----| set          |  | |                           |           |   |
                   |______________|  | |        FD_SE              |           |   |
                                     | |    ______________         |           |   |
                                     | |___|              |________|           |   |
                                     |_____| d          q |________| B         |   |
                                           |              |  | |   |___________|   |
                                clk_i  ----|> clk         |  | |                   |
                                           |              |  | |                   |
                            ---------------| ce           |  | |__                 |
                            |              |              |  |____ minimo_o        | 
                            |   rst_i  ----| set          |                        |
                            |              |______________|                        | 
                            |                                                      |
                            |______________________________________________________|

    :Parametros:
        - `clk_i`    : entrada de clock
        - `rst_i`    : reset sincronico
        - `ce_i`     : dato valido
        - `d_i`      : entrada de datos
        - `minimo_o` : salida del minimo

    """
    
    n = len(d_i)

    A = Signal(intbv(0)[n:])
    B = Signal(intbv(0)[n:])

    A_Men_B = Signal(Lo)

    reg_in = FD_SE(clk_i = clk_i, 
                   set_i = rst_i, 
                   ce_i = ce_i, 
                   d_i = d_i, 
                   q_o = A)  # Registro de entrada

    reg_min = FD_SE(clk_i = clk_i, 
                    set_i = rst_i, 
                    ce_i = A_Men_B,
                    d_i = A, 
                    q_o = B)  # Registro de salida

    @always(A,B)
    def comparador() :     # Comparador
        if A < B :
            A_Men_B.next = Hi
        else :
            A_Men_B.next = Lo

    @always_comb
    def conex_min() :
        minimo_o.next = B

    return instances()

#########################################################################################

