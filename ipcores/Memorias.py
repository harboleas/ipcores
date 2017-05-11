"""
Memorias
========

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from Contadores import CB_RE

Hi = True        # Definicion de los niveles logicos
Lo = False

############################################################

def RAM_SP(clk_i, 
           ena_i, 
           rst_i, 
           we_i, 
           addr_i, 
           d_i, 
           d_o) :
    """Memoria RAM Single Port sincronica de n posiciones y
    m bits::

            ________________________
       ____|                        |____
       ____| d_i                d_o |____
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ena_i                  |
           |                        |
       ----| rst_i                  |
           |                        |
       ----| we_i                   |
       ____|                        |
       ____| addr_i                 |
           |________________________|


    Tabla de verdad

    +-------+-------+------+---------+--------+-----+-----------+----------------+
    | ena_i | rst_i | we_i |  clk_i  | addr_i | d_i |    d_o    |      RAM       |
    +=======+=======+======+=========+========+=====+===========+================+
    |   L   |   X   |   X  |    X    |   X    |  X  | No Cambia |   No Cambia    |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   H   |   L  |  L > H  |   X    |  X  |     0     |   No Cambia    |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   H   |   H  |  L > H  |  ADDR  |  D  |     0     | RAM[ADDR] <= D |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   L   |   L  |  L > H  |  ADDR  |  X  | RAM[ADDR] |   No Cambia    |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   L   |   H  |  L > H  |  ADDR  |  D  |     D     | RAM[ADDR] <= D |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
 
 

    :Parametros:
        - `clk_i`  :  entrada de clock
        - `ena_i`  :  chip enable
        - `rst_i`  :  reset sincronico
        - `we_i`   :  write enable
        - `addr_i` :  direccion (n bits)
        - `d_i`    :  data in (m bits)
        - `d_o`    :  data out (m bits)

    """    

    n = len(addr_i)
    m = len(d_i)
 
    if m == 1 :
        ram = [Signal(Lo) for i in range(2**n)]
    else :
        ram = [Signal(intbv(0)[m:]) for i in range(2**n)]

    @always(clk_i.posedge)
    def RAM_SP_hdl() :
        if ena_i :
            if rst_i :
                if not we_i :
                    d_o.next = 0
                else :
                    d_o.next = 0
                    ram[int(addr_i)].next = d_i
            else :
                if not we_i :
                    d_o.next = ram[int(addr_i)]
                else :
                    d_o.next = d_i
                    ram[int(addr_i)].next = d_i

    return instances()

############################################################

def RAM_DP(clkA_i, 
           enaA_i, 
           rstA_i, 
           weA_i, 
           addrA_i, 
           dA_i, 
           dA_o, 
           clkB_i, 
           enaB_i, 
           rstB_i, 
           weB_i, 
           addrB_i, 
           dB_i, 
           dB_o) :
    """Memoria RAM Dual Port sincronica de n posiciones y
    m bits::

            ________________________
       ____|                        |____
       ____| d_i                d_o |____
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ena_i                  |
           |           A            |
       ----| rst_i                  |
           |                        |
       ----| we_i                   |
       ____|                        |
       ____| addr_i                 |
           |________  RAM   ________|
       ____|                        |____
       ____| d_i                d_o |____
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ena_i                  |
           |           B            |
       ----| rst_i                  |
           |                        |
       ----| we_i                   |
       ____|                        |
       ____| addr_i                 |
           |________________________|


    Tabla de verdad (A/B)

    +-------+-------+------+---------+--------+-----+-----------+----------------+
    | ena_i | rst_i | we_i |  clk_i  | addr_i | d_i |    d_o    |      RAM       |
    +=======+=======+======+=========+========+=====+===========+================+
    |   L   |   X   |   X  |    X    |   X    |  X  | No Cambia |   No Cambia    |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   H   |   L  |  L > H  |   X    |  X  |     0     |   No Cambia    |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   H   |   H  |  L > H  |  ADDR  |  D  |     0     | RAM[ADDR] <= D |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   L   |   L  |  L > H  |  ADDR  |  X  | RAM[ADDR] |   No Cambia    |
    +-------+-------+------+---------+--------+-----+-----------+----------------+
    |   H   |   L   |   H  |  L > H  |  ADDR  |  D  |     D     | RAM[ADDR] <= D |
    +-------+-------+------+---------+--------+-----+-----------+----------------+

 
    :Parametros:
        - `clkA_i`   :  entrada de clock
        - `enaA_i`   :  chip enable
        - `rstA_i`   :  reset sincronico
        - `weA_i`    :  write enable
        - `addrA_i`  :  direccion (n bits)
        - `dA_i`     :  data in (m bits)
        - `dA_o`     :  data out (m bits)
        - `clkB_i`   :  entrada de clock
        - `enaB_i`   :  chip enable
        - `rstB_i`   :  reset sincronico
        - `weB_i`    :  write enable
        - `addrB_i`  :  direccion (n bits)
        - `dB_i`     :  data in (m bits)
        - `dB_o`     :  data out (m bits)


    """    

    n = len(addrA_i)
    m = len(dA_i)

    if m == 1 :
        ram = [Signal(Lo) for i in range(2**n)]
    else :
        ram = [Signal(intbv(0)[m:]) for i in range(2**n)]
 
    @always(clkA_i.posedge)
    def RAM_DP_A_hdl() :
        if enaA_i :
            if rstA_i :
                if not weA_i :
                    dA_o.next = 0
                else :
                    dA_o.next = 0
                    ram[int(addrA_i)].next = dA_i
            else :
                dA_o.next = ram[int(addrA_i)]
                if weA_i :
                    ram[int(addrA_i)].next = dA_i


    @always(clkB_i.posedge)
    def RAM_DP_B_hdl() :
        if enaB_i :
            if rstB_i :
                if not weB_i :
                    dB_o.next = 0
                else :
                    dB_o.next = 0
                    ram[int(addrB_i)].next = dB_i
            else :
                dB_o.next = ram[int(addrB_i)]
                if weB_i :
                    ram[int(addrB_i)].next = dB_i


    return instances()


############################################################

def FIFO(clk_i, 
         ce_i, 
         d_i, 
         q_o, 
         k) :
    """Estrucutra FIFO de k etapas y n bits de datos 
    con clock enable 
    ::

            ________________________
       ____|                        |____
       ____| d_i                q_o |____
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |________________________|
 
    :Parametros:
        - `clk_i` :  entrada de clock
        - `ce_i`  :  clock enable
        - `d_i`   :  data in (n bits)
        - `q_o`   :  data out (n bits)
        - `k`     :  longitud de la cola

    """    

    # Descripcion estructural
    #

    n = len(d_i)
    addr_max = k - 1

    rst_cont = Signal(Lo)
    w_addr = Signal(intbv(0, 0, k))  # Puntero de llenado de la cola  (Puerto A)
    r_addr = Signal(intbv(1, 0, k))  # Puntero de vaciado o lectura   (Puerto B)
    
    p = len(w_addr)

    if n == 1 :
        ram = [Signal(Lo) for i in range(2**p)]
    else :
        ram = [Signal(intbv(0)[n:]) for i in range(2**p)]


    ###############################################

    gen_w_addr = CB_RE(clk_i = clk_i, 
                       rst_i = rst_cont, 
                       ce_i = ce_i, 
                       q_o = w_addr)   # Puntero de llenado

    @always(w_addr, ce_i)
    def gen_r_addr() :
        if w_addr == addr_max :
            rst_cont.next = ce_i
            r_addr.next = 0
        else :
            rst_cont.next = Lo
            r_addr.next = w_addr + 1   # El puntero de vaciado esta uno por delante del de llenado  


    @always(clk_i.posedge)
    def RAM_access() :
        if ce_i :
            ram[int(w_addr)].next = d_i
            q_o.next = ram[int(r_addr)]


    return instances()

############################################################
