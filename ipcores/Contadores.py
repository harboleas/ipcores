"""
Contadores Binarios
===================

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *

Hi = True       # Definicion de niveles logicos
Lo = False     

###########################################

def CB(clk_i, 
       q_o) :
    """Contador binario de n bits ::

            _________________
           |                 |
           |                 |____
       ----|> clk_i      q_o |____
           |                 |
           |_________________|

 
    :Parametros:
        - `clk_i` : clock
        - `q_o`   : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge)
    def CB_hdl() :
        cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

def CB_R(clk_i, 
         rst_i, 
         q_o) :
    """Contador binario de n bits con reset
    sincronico ::

            __________________
           |                  |
           |                  |____
       ----|> clk_i       q_o |____
           |                  |
           |                  |
       ----| rst_i            |
           |__________________|

 
    :Parametros:
        - `clk_i` : clock
        - `rst_i` : reset sincronico
        - `q_o`   : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge)
    def CB_R_hdl() :
        if rst_i :
            cuenta_aux.next = 0
        else :
            cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

def CB_E(clk_i, 
         ce_i, 
         q_o) :
    """Contador binario de n bits con clock
    enable ::

            _________________
           |                 |
           |                 |____
       ----|> clk_i      q_o |____
           |                 |
           |                 |
       ----| ce_i            |
           |_________________|

 
    :Parametros:
        - `clk_i`: clock
        - `ce_i` : clock enable
        - `q_o`  : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge)
    def CB_E_hdl() :
        if ce_i :
            cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

def CB_RE(clk_i, 
          rst_i, 
          ce_i, 
          q_o) :
    """Contador binario de n bits con reset
    sincronico y clock enable::

            __________________
           |                  |
           |                  |____
       ----|> clk_i       q_o |____
           |                  |
       ----| rst_i            |
           |                  |
       ----| ce_i             |
           |__________________|

 
    :Parametros:
        - `clk_i` : clock
        - `rst_i` : reset sincronico
        - `ce_i`  : clock enable
        - `q_o`   : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge)
    def CB_RE_hdl() :
        if rst_i :
            cuenta_aux.next = 0
        else :
            if ce_i :
                cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

##################################################################

def CB_RLE(clk_i, 
           rst_i, 
           load_i, 
           d_i, 
           ce_i, 
           q_o) :
    """Contador binario de n bits con carga y reset
    sincronico y clock enable::

            __________________
           |                  |
           |                  |____
       ----|> clk_i       q_o |____
           |                  |
       ----| rst_i            |
           |                  |
       ----| load_i           |
           |                  |
       ----| ce_i             |
       ____|                  |
       ____| d_i              |
           |__________________|

 
    :Parametros:
        - `clk_i`  : clock
        - `rst_i`  : reset sincronico
        - `load_i` : carga sincronica
        - `d_i`    : valor para cargar ( n bits )
        - `ce_i`   : clock enable
        - `q_o`    : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge)
    def CB_RLE_hdl() :
        if rst_i :
            cuenta_aux.next = 0
        elif load_i :
            cuenta_aux.next = d_i
        else :
            if ce_i :
                cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

def CB_C(clk_i, 
         clr_i, 
         q_o) :
    """Contador binario de n bits con clear
    asincronico::

            __________________
           |                  |
           |                  |____
       ----|> clk_i       q_o |____
           |                  |
           |                  |
       ----| clr_i            |
           |__________________|

 
    :Parametros:
        - `clk_i`    : clock
        - `clr_i`    : clear asincronico
        - `q_o` : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge, clr_i.posedge)
    def CB_C_hdl() :
        if clr_i :
            cuenta_aux.next = 0
        else :
            cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

def CB_CE(clk_i, 
          clr_i, 
          ce_i, 
          q_o) :
    """Contador binario de n bits con clear
    asincronico y clock enable::

            _________________
           |                 |
           |                 |____
       ----|> clk_i      q_o |____
           |                 |
       ----| clr_i           |
           |                 |
       ----| ce_i            |
           |_________________|

 
    :Parametros:
        - `clk_i`    : clock
        - `clr_i`    : clear asincronico
        - `ce_i`     : clock enable
        - `q_o` : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])


    @always(clk_i.posedge, clr_i.posedge)
    def CB_CE_hdl() :
        if clr_i :
            cuenta_aux.next = 0
        else :
            if ce_i :
                cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

def CB_CLE(clk_i, 
           clr_i, 
           load_i, 
           d_i, 
           ce_i, 
           q_o) :
    """Contador binario de n bits con carga y clear
    asincronico y clock enable::

            __________________
           |                  |
           |                  |____
       ----|> clk_i       q_o |____
           |                  |
       ----| clr_i            |
           |                  |
       ----| load_i           |
           |                  |
       ----| ce_i             |
       ____|                  |
       ____| d_i              |
           |__________________|

 
    :Parametros:
        - `clk_i`  : clock
        - `clr_i`  : clear asincronico
        - `load_i` : carga sincronica
        - `d_i`    : valor para cargar ( n bits )
        - `ce_i`   : clock enable
        - `q_o`    : valor de la cuenta ( n bits )

    """

    n = len(q_o)
    valor_max = 2 ** n

    cuenta_aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge, clr_i.posedge)
    def CB_CLE_hdl() :
        if clr_i :
            cuenta_aux.next = 0
        else :
            if load_i :
                cuenta_aux.next = d_i
            else :
                if ce_i :
                    cuenta_aux.next = (cuenta_aux + 1) % valor_max

    @always_comb
    def conex_cuenta() :
        q_o.next = cuenta_aux

    return instances()

############################################ 

    
