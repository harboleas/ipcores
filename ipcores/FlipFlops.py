"""
Flip Flops
==========

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *

Hi = True
Lo = False

################################################################
def F_SR(clk_i,
         s_i,
         r_i,
         q_o) :

    @always(clk_i.posedge)
    def F_SR_hdl() :
        if s_i and not r_i:
            q_o.next = Hi
        elif not s_i and r_i :
            q_o.next = Lo

    return instances() 
        

################################################################

def LD(g_i, 
       d_i,
       q_o) :
    """Gated latch de n bits"""

    @always(g_i, d_i)
    def LD_hdl() :
        if g_i :
            q_o.next = d_i

    return instances() 

#################################################################

def FD(clk_i, 
       d_i,
       q_o) :
    """FF D ( o Registro de n bits )
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |________________________|
  

    Tabla de verdad

    +-----+---------+-----------+
    | d_i |  clk_i  |    q_o    |
    +=====+=========+===========+
    |  L  |  L > H  |     L     |
    +-----+---------+-----------+
    |  H  |  L > H  |     H     |
    +-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    @always(clk_i.posedge)
    def FD_hdl() :
        q_o.next = d_i

    return instances()

##########################################################

def FD_E(clk_i, 
         ce_i, 
         d_i, 
         q_o) :
    """FF D ( o Registro de n bits ) con clock enable
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad

    +------+-----+---------+-----------+
    | ce_i | d_i |  clk_i  |    q_o    |
    +======+=====+=========+===========+
    |  L   |  X  |    X    | No Cambia |
    +------+-----+---------+-----------+
    |  H   |  L  |  L > H  |     L     |
    +------+-----+---------+-----------+
    |  H   |  H  |  L > H  |     H     |
    +------+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `ce_i`  -- clock enable
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """
    
    @always(clk_i.posedge)
    def FD_E_hdl() :
        if ce_i :
            q_o.next = d_i

    return instances()

##########################################################

def FD_R(clk_i, 
         rst_i, 
         d_i, 
         q_o) :
    """FF D ( o Registro de n bits ) con reset sincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-----+---------+-----------+
    | rst_i | d_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   H   |  X  |  L > H  |     L     |
    +-------+-----+---------+-----------+
    |   L   |  L  |  L > H  |     L     |
    +-------+-----+---------+-----------+
    |   L   |  H  |  L > H  |     H     |
    +-------+-----+---------+-----------+
 
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """
    
    @always(clk_i.posedge)
    def FD_R_hdl() :
        if rst_i :
            q_o.next = 0
        else :
            q_o.next = d_i

    return instances()

##########################################################

def FD_S(clk_i, 
         set_i, 
         d_i, 
         q_o) :
    """FF D ( o Registro de n bits ) con set sincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-----+---------+-----------+
    | set_i | d_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   H   |  X  |  L > H  |     H     |
    +-------+-----+---------+-----------+
    |   L   |  L  |  L > H  |     L     |
    +-------+-----+---------+-----------+
    |   L   |  H  |  L > H  |     H     |
    +-------+-----+---------+-----------+

    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `set_i` -- set sincronico
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1
    
    @always(clk_i.posedge)
    def FD_S_hdl() :
        if set_i :
            q_o.next = qmax
        else :
            q_o.next = d_i
    
    return instances()

##########################################################

def FD_RE(clk_i, 
          rst_i, 
          ce_i, 
          d_i, 
          q_o) :
    """FF D ( o Registro de n bits ) con clock enable y reset sincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad

    +-------+------+-----+---------+-----------+
    | rst_i | ce_i | d_i |  clk_i  |    q_o    |
    +=======+======+=====+=========+===========+
    |   H   |  X   |  X  |  L > H  |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  L   |  X  |    X    | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  L  |  L > H  |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  H  |  L > H  |     H     |
    +-------+------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico
        - `ce_i`  -- clock enable
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    @always(clk_i.posedge)
    def FD_RE_hdl() :
        if rst_i :
            q_o.next = 0
        else :
            if ce_i :
                q_o.next = d_i

    return instances()

##########################################################

def FD_SE(clk_i, 
          set_i, 
          ce_i, 
          d_i, 
          q_o) :
    """FF D ( o Registro de n bits ) con clock enable y set sincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| set_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad

    +-------+------+-----+---------+-----------+
    | set_i | ce_i | d_i |  clk_i  |    q_o    |
    +=======+======+=====+=========+===========+
    |   H   |  X   |  X  |  L > H  |     H     |
    +-------+------+-----+---------+-----------+
    |   L   |  L   |  X  |    X    | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  L  |  L > H  |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  H  |  L > H  |     H     |
    +-------+------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i` -- entrada de clock
        - `set_i` -- set sincronico
        - `ce_i`  -- clock enable
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1
    
    @always(clk_i.posedge)
    def FD_SE_hdl() :
        if set_i :
            q_o.next = qmax
        else :
            if ce_i :
                q_o.next = d_i
    
    return instances()

##########################################################

def FD_RS(clk_i, 
          rst_i, 
          set_i, 
          d_i, 
          q_o) :
    """FF D ( o Registro de n bits ) con reset y set sincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-------+-----+---------+-----------+
    | rst_i | set_i | d_i |  clk_i  |    q_o    |
    +=======+=======+=====+=========+===========+
    |   H   |   X   |  X  |  L > H  |     L     |
    +-------+-------+-----+---------+-----------+
    |   L   |   H   |  X  |  L > H  |     H     |
    +-------+-------+-----+---------+-----------+
    |   L   |   L   |  L  |  L > H  |     L     |
    +-------+-------+-----+---------+-----------+
    |   L   |   L   |  H  |  L > H  |     H     |
    +-------+-------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico
        - `set_i` -- set sincronico
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1
    
    @always(clk_i.posedge)
    def FD_RS_hdl() :
        if rst_i :
            q_o.next = 0
        elif set_i :
            q_o.next = qmax
        else :
            q_o.next = d_i
    
    return instances()


##########################################################


def FD_RSE(clk_i, 
           rst_i, 
           set_i, 
           ce_i, 
           d_i, 
           q_o) :
    """Flip flop tipo D ( o Registro de n bits ) con clock enable, reset y set sincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-------+------+-----+---------+-----------+
    | rst_i | set_i | ce_i | d_i |  clk_i  |    q_o    |
    +=======+=======+======+=====+=========+===========+
    |   H   |   X   |  X   |  X  |  L > H  |     L     |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   H   |  X   |  X  |  L > H  |     H     |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   L   |  L   |  X  |    X    | No Cambia |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   L   |  H   |  L  |  L > H  |     L     |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   L   |  H   |  H  |  L > H  |     H     |
    +-------+-------+------+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico  
        - `set_i` -- set sincronico  
        - `ce_i`  -- clock enable
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1

    @always(clk_i.posedge)
    def FD_RSE_hdl() :
        
        if rst_i :
            q_o.next = 0

        elif set_i :
            q_o.next = qmax 

        else :
            if ce_i :
                q_o.next = d_i

    return instances()

#########################################################

def FD_C(clk_i, 
         clr_i, 
         d_i, 
         q_o) :
    """FF D ( o Registro de n bits ) con clear asincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-----+---------+-----------+
    | clr_i | d_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   H   |  X  |    X    |     L     |
    +-------+-----+---------+-----------+
    |   L   |  L  |  L > H  |     L     |
    +-------+-----+---------+-----------+
    |   L   |  H  |  L > H  |     H     |
    +-------+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `clr_i` -- clear asincronico
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    @always(clk_i.posedge, clr_i.posedge)
    def FD_C_hdl() :
        if clr_i :
            q_o.next = 0
        else :
            q_o.next = d_i

    return instances()

##########################################################

def FD_P(clk_i, 
         prst_i, 
         d_i, 
         q_o) :
    """FF D ( o Registro de n bits ) con preset asincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| prst_i                 |
            |________________________|
  

    Tabla de verdad

    +--------+-----+---------+-----------+
    | prst_i | d_i |  clk_i  |    q_o    |
    +========+=====+=========+===========+
    |   H    |  X  |    X    |     H     |
    +--------+-----+---------+-----------+
    |   L    |  L  |  L > H  |     L     |
    +--------+-----+---------+-----------+
    |   L    |  H  |  L > H  |     H     |
    +--------+-----+---------+-----------+

    
    :Parametros:
        - `clk_i`  -- entrada de clock
        - `prst_i` -- preset asincronico
        - `d_i`    -- data in (n bits)
        - `q_o`    -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1

    @always(clk_i.posedge, prst_i.posedge)
    def FD_P_hdl() :
        if prst_i :
            q_o.next = qmax
        else :
            q_o.next = d_i

    return instances()

##########################################################

def FD_CE(clk_i, 
          clr_i, 
          ce_i, 
          d_i, 
          q_o) :
    """FF D ( o Registro de n bits ) con clock enable y clear asincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad

    +-------+------+-----+---------+-----------+
    | clr_i | ce_i | d_i |  clk_i  |    q_o    |
    +=======+======+=====+=========+===========+
    |   H   |  X   |  X  |    X    |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  L   |  X  |    X    | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  L  |  L > H  |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  H  |  L > H  |     H     |
    +-------+------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i` -- entrada de clock
        - `clr_i` -- clear asincronico
        - `ce_i`  -- clock enable
        - `d_i`   -- data in (n bits)
        - `q_o`   -- data out (n bits)
 
    """

    @always(clk_i.posedge, clr_i.posedge)
    def FD_CE_hdl() :
        if clr_i :
            q_o.next = 0
        else :
            if ce_i :
                q_o.next = d_i

    return instances()

##########################################################

def FD_PE(clk_i, 
          prst_i, 
          ce_i, 
          d_i, 
          q_o) :
    """FF D ( o Registro de n bits ) con clock enable y preset asincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| prst_i                 |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad

    +--------+------+-----+---------+-----------+
    | prst_i | ce_i | d_i |  clk_i  |    q_o    |
    +========+======+=====+=========+===========+
    |   H    |  X   |  X  |    X    |     H     |
    +--------+------+-----+---------+-----------+
    |   L    |  L   |  X  |    X    | No Cambia |
    +--------+------+-----+---------+-----------+
    |   L    |  H   |  L  |  L > H  |     L     |
    +--------+------+-----+---------+-----------+
    |   L    |  H   |  H  |  L > H  |     H     |
    +--------+------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `prst_i` -- preset asincronico
        - `ce_i`   -- clock enable
        - `d_i`    -- data in (n bits)
        - `q_o`    -- data out (n bits)
 
    """
    n = len(q_o)
    qmax = 2**n - 1

    @always(clk_i.posedge, prst_i.posedge)
    def FD_PE_hdl() :
        if prst_i :
            q_o.next = qmax
        else :
            if ce_i :
                q_o.next = d_i

    return instances()

##########################################################

def FD_CP(clk_i, 
          clr_i, 
          prst_i, 
          d_i, 
          q_o) :
    """FF D ( o Registro de n bits ) con clear y preset asincronico
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+------+-+-----+---------+-----------+
    | clr_i | prst_i | d_i |  clk_i  |    q_o    |
    +=======+========+=====+=========+===========+
    |   H   |   X    |  X  |    X    |     L     |
    +-------+--------+-----+---------+-----------+
    |   L   |   H    |  X  |    X    |     H     |
    +-------+--------+-----+---------+-----------+
    |   L   |   L    |  L  |  L > H  |     L     |
    +-------+--------+-----+---------+-----------+
    |   L   |   L    |  H  |  L > H  |     H     |
    +-------+--------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico
        - `prst_i` -- preset asincronico
        - `d_i`    -- data in (n bits)
        - `q_o`    -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1

    @always(clk_i.posedge, clr_i.posedge, prst_i.posedge)
    def FD_CP_hdl() :
        if clr_i :
            q_o.next = 0
        elif prst_i :
            q_o.next = qmax
        else :
            q_o.next = d_i

    return instances()

##########################################################

def FD_CPE(clk_i, 
           clr_i, 
           prst_i, 
           ce_i, 
           d_i, 
           q_o) :
    """Flip flop tipo D ( o Registro de n bits ) con clock enable, clear y preset asincronicos
    ::
 
             ________________________
        ____|                        |____
        ____| d_i                q_o |____
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| prst_i                 |
            |________________________|
  

    Tabla de verdad

    +-------+--------+------+-----+---------+-----------+
    | clr_i | prst_i | ce_i | d_i |  clk_i  |    q_o    |
    +=======+========+======+=====+=========+===========+
    |   H   |   X    |  X   |  X  |    X    |     L     |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   H    |  X   |  X  |    X    |     H     |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   L    |  L   |  X  |    X    | No Cambia |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   L    |  H   |  L  |  L > H  |     L     |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   L    |  H   |  H  |  L > H  |     H     |
    +-------+--------+------+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico  
        - `prst_i` -- preset asincronico  
        - `ce_i`   -- clock enable
        - `d_i`    -- data in (n bits)
        - `q_o`    -- data out (n bits)
 
    """

    n = len(q_o)
    qmax = 2**n - 1

    @always(clk_i.posedge, clr_i.posedge, prst_i.posedge)
    def FD_CPE_hdl() :

        if clr_i :
            q_o.next = 0

        elif prst_i :
            q_o.next = qmax

        else :
            if ce_i :
                q_o.next = d_i 

    return instances()

##########################################################

def FJK(clk_i, 
        j_i, 
        k_i, 
        q_o) :
    """Flip flop tipo JK 
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |________________________|
  

    Tabla de verdad

    +-----+-----+---------+-----------+
    | j_i | k_i |  clk_i  |    q_o    |
    +=====+=====+=========+===========+
    |  L  |  L  |  L > H  | No Cambia |
    +-----+-----+---------+-----------+
    |  L  |  H  |  L > H  |     L     |
    +-----+-----+---------+-----------+
    |  H  |  L  |  L > H  |     H     |
    +-----+-----+---------+-----------+
    |  H  |  H  |  L > H  |  Cambia   |
    +-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_hdl() :
        if j_i :
            if k_i :
                q_aux.next = not q_aux
            else :
                q_aux.next = Hi
        else :
            if k_i :
                q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

#################################################################

def FJK_E(clk_i, 
          ce_i, 
          j_i, 
          k_i, 
          q_o) :
    """Flip flop tipo JK con clock enable
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad

    +------+-----+-----+---------+-----------+
    | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +======+=====+=====+=========+===========+
    |  L   |  X  |  X  |    X    | No Cambia |
    +------+-----+-----+---------+-----------+
    |  H   |  L  |  L  |  L > H  | No Cambia |
    +------+-----+-----+---------+-----------+
    |  H   |  L  |  H  |  L > H  |     L     |
    +------+-----+-----+---------+-----------+
    |  H   |  H  |  L  |  L > H  |     H     |
    +------+-----+-----+---------+-----------+
    |  H   |  H  |  H  |  L > H  |  Cambia   |
    +------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `ce_i`  -- clock enable
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_E() :
        if ce_i :        
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

###################################################################

def FJK_R(clk_i, 
          rst_i, 
          j_i, 
          k_i, 
          q_o) :
    """Flip flop tipo JK con reset sincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-----+-----+---------+-----------+
    | rst_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+=====+=====+=========+===========+
    |   H   |  X  |  X  |  L > H  |     L     |
    +-------+-----+-----+---------+-----------+
    |   L   |  L  |  L  |  L > H  | No Cambia |
    +-------+-----+-----+---------+-----------+
    |   L   |  L  |  H  |  L > H  |     L     |
    +-------+-----+-----+---------+-----------+
    |   L   |  H  |  L  |  L > H  |     H     |
    +-------+-----+-----+---------+-----------+
    |   L   |  H  |  H  |  L > H  |  Cambia   |
    +-------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico  
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_R_hdl() :

        if rst_i :
            q_aux.next = Lo
        
        else :
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

######################################################################

def FJK_S(clk_i, 
          rst_i, 
          j_i, 
          k_i, 
          q_o) :
    """Flip flop tipo JK con set sincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-----+-----+---------+-----------+
    | set_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+=====+=====+=========+===========+
    |   H   |  X  |  X  |  L > H  |     H     |
    +-------+-----+-----+---------+-----------+
    |   L   |  L  |  L  |  L > H  | No Cambia |
    +-------+-----+-----+---------+-----------+
    |   L   |  L  |  H  |  L > H  |     L     |
    +-------+-----+-----+---------+-----------+
    |   L   |  H  |  L  |  L > H  |     H     |
    +-------+-----+-----+---------+-----------+
    |   L   |  H  |  H  |  L > H  |  Cambia   |
    +-------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `set_i` -- set sincronico  
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_S_hdl() :

        if set_i :
            q_aux.next = Hi
        
        else :
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

###################################################################

def FJK_RE(clk_i, 
           rst_i, 
           ce_i, 
           j_i, 
           k_i, 
           q_o) :
    """Flip flop tipo JK con clock enable y reset sincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| rst_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+------+-----+-----+---------+-----------+
    | rst_i | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+======+=====+=====+=========+===========+
    |   H   |  X   |  X  |  X  |  L > H  |     L     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  L   |  X  |  X  |    X    | No Cambia |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  L  |  L  |  L > H  | No Cambia |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  L  |  H  |  L > H  |     L     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  H  |  L  |  L > H  |     H     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  H  |  H  |  L > H  |  Cambia   |
    +-------+------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico  
        - `ce_i`  -- clock enable
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """


    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_RE_hdl() :

        if rst_i :
            q_aux.next = Lo
        
        else :
            if ce_i :
                if j_i :
                    if k_i :
                        q_aux.next = not q_aux
                    else :
                        q_aux.next = Hi
                else :
                    if k_i :
                        q_aux.next = Lo

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

###################################################################

def FJK_SE(clk_i, 
           set_i, 
           ce_i, 
           j_i, 
           k_i, 
           q_o) :
    """Flip flop tipo JK con clock enable y set sincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+------+-----+-----+---------+-----------+
    | set_i | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+======+=====+=====+=========+===========+
    |   H   |  X   |  X  |  X  |  L > H  |     H     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  L   |  X  |  X  |    X    | No Cambia |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  L  |  L  |  L > H  | No Cambia |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  L  |  H  |  L > H  |     L     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  H  |  L  |  L > H  |     H     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  H  |  H  |  L > H  |  Cambia   |
    +-------+------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `set_i` -- set sincronico  
        - `ce_i`  -- clock enable
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_SE_hdl() :
        if set_i :
            q_aux.next = Hi
        
        else :
            if ce_i :
                if j_i :
                    if k_i :
                        q_aux.next = not q_aux
                    else :
                        q_aux.next = Hi
                else :
                    if k_i :
                        q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

#################################################################

def FJK_RS(clk_i, 
           rst_i, 
           set_i, 
           j_i, 
           k_i, 
           q_o) :
    """Flip flop tipo JK con reset y set sincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-------+-----+-----+---------+-----------+
    | rst_i | set_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+=======+=====+=====+=========+===========+
    |   H   |   X   |  X  |  X  |  L > H  |     L     |
    +-------+-------+-----+-----+---------+-----------+
    |   L   |   H   |  X  |  X  |  L > H  |     H     |
    +-------+-------+-----+-----+---------+-----------+
    |   L   |   L   |  L  |  L  |  L > H  | No Cambia |
    +-------+-------+-----+-----+---------+-----------+
    |   L   |   L   |  L  |  H  |  L > H  |     L     |
    +-------+-------+-----+-----+---------+-----------+
    |   L   |   L   |  H  |  L  |  L > H  |     H     |
    +-------+-------+-----+-----+---------+-----------+
    |   L   |   L   |  H  |  H  |  L > H  |  Cambia   |
    +-------+-------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico  
        - `set_i` -- set sincronico  
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_RS_hdl() :
        if rst_i :
            q_aux.next = Lo

        elif set_i :
            q_aux.next = Hi 
       
        else :
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

#################################################################
    
def FJK_RSE(clk_i, 
            rst_i, 
            set_i, 
            ce_i, 
            j_i, 
            k_i, 
            q_o) :
    """Flip flop tipo JK con clock enable, reset y set sincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-------+------+-----+-----+---------+-----------+
    | rst_i | set_i | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+=======+======+=====+=====+=========+===========+
    |   H   |   X   |  X   |  X  |  X  |  L > H  |     L     |
    +-------+-------+------+-----+-----+---------+-----------+
    |   L   |   H   |  X   |  X  |  X  |  L > H  |     H     |
    +-------+-------+------+-----+-----+---------+-----------+
    |   L   |   L   |  L   |  X  |  X  |    X    | No Cambia |
    +-------+-------+------+-----+-----+---------+-----------+
    |   L   |   L   |  H   |  L  |  L  |  L > H  | No Cambia |
    +-------+-------+------+-----+-----+---------+-----------+
    |   L   |   L   |  H   |  L  |  H  |  L > H  |     L     |
    +-------+-------+------+-----+-----+---------+-----------+
    |   L   |   L   |  H   |  H  |  L  |  L > H  |     H     |
    +-------+-------+------+-----+-----+---------+-----------+
    |   L   |   L   |  H   |  H  |  H  |  L > H  |  Cambia   |
    +-------+-------+------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `rst_i` -- reset sincronico  
        - `set_i` -- set sincronico  
        - `ce_i`  -- clock enable
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FJK_RSE_hdl() :
        
        if rst_i :
            q_aux.next = Lo

        elif set_i :
            q_aux.next = Hi 

        else :
            if ce_i :
                if j_i :
                    if k_i :
                        q_aux.next = not q_aux
                    else :
                        q_aux.next = Hi
                else :
                    if k_i :
                        q_aux.next = Lo

    @always_comb
    def conex_q() :
        q_o.next = q_aux


    return instances()

##########################################################


def FJK_C(clk_i, 
          clr_i, 
          j_i, 
          k_i, 
          q_o) :
    """Flip flop tipo JK con clear asincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+-----+-----+---------+-----------+
    | clr_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+=====+=====+=========+===========+
    |   H   |  X  |  X  |    X    |     L     |
    +-------+-----+-----+---------+-----------+
    |   L   |  L  |  L  |  L > H  | No Cambia |
    +-------+-----+-----+---------+-----------+
    |   L   |  L  |  H  |  L > H  |     L     |
    +-------+-----+-----+---------+-----------+
    |   L   |  H  |  L  |  L > H  |     H     |
    +-------+-----+-----+---------+-----------+
    |   L   |  H  |  H  |  L > H  |  Cambia   |
    +-------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `clr_i` -- clear asincronico  
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge)
    def FJK_C_hdl() :

        if clr_i :
            q_aux.next = Lo
        
        else :
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

######################################################################

def FJK_P(clk_i, 
          prst_i, 
          j_i, 
          k_i, 
          q_o) :
    """Flip flop tipo JK con preset asincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| prst_i                 |
            |________________________|
  

    Tabla de verdad

    +--------+-----+-----+---------+-----------+
    | prst_i | j_i | k_i |  clk_i  |    q_o    |
    +========+=====+=====+=========+===========+
    |   H    |  X  |  X  |    X    |     H     |
    +--------+-----+-----+---------+-----------+
    |   L    |  L  |  L  |  L > H  | No Cambia |
    +--------+-----+-----+---------+-----------+
    |   L    |  L  |  H  |  L > H  |     L     |
    +--------+-----+-----+---------+-----------+
    |   L    |  H  |  L  |  L > H  |     H     |
    +--------+-----+-----+---------+-----------+
    |   L    |  H  |  H  |  L > H  |  Cambia   |
    +--------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i`  -- entrada de clock
        - `prst_i` -- preset asincronico  
        - `j_i`    -- J in 
        - `k_i`    -- K in 
        - `q_o`    -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, prst_i.posedge)
    def FJK_P_hdl() :

        if prst_i :
            q_aux.next = Hi
        
        else :
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

###################################################################

def FJK_CE(clk_i, 
           clr_i, 
           ce_i, 
           j_i, 
           k_i, 
           q_o) :
    """Flip flop tipo JK con clock enable y clear asincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| clr_i                  |
            |________________________|
  

    Tabla de verdad

    +-------+------+-----+-----+---------+-----------+
    | clr_i | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+======+=====+=====+=========+===========+
    |   H   |  X   |  X  |  X  |    X    |     L     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  L   |  X  |  X  |    X    | No Cambia |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  L  |  L  |  L > H  | No Cambia |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  L  |  H  |  L > H  |     L     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  H  |  L  |  L > H  |     H     |
    +-------+------+-----+-----+---------+-----------+
    |   L   |  H   |  H  |  H  |  L > H  |  Cambia   |
    +-------+------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `clr_i` -- clear asincronico  
        - `ce_i`  -- clock enable
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge)
    def FJK_CE_hdl() :

        if clr_i :
            q_aux.next = Lo
        
        else :
            if ce_i :
                if j_i :
                    if k_i :
                        q_aux.next = not q_aux
                    else :
                        q_aux.next = Hi
                else :
                    if k_i :
                        q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

###################################################################

def FJK_PE(clk_i, 
           prst_i, 
           ce_i, 
           j_i, 
           k_i, 
           q_o) :
    """Flip flop tipo JK con clock enable y preset asincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| prst_i                 |
            |________________________|
  

    Tabla de verdad

    +--------+------+-----+-----+---------+-----------+
    | prst_i | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +========+======+=====+=====+=========+===========+
    |   H    |  X   |  X  |  X  |    X    |     H     |
    +--------+------+-----+-----+---------+-----------+
    |   L    |  L   |  X  |  X  |    X    | No Cambia |
    +--------+------+-----+-----+---------+-----------+
    |   L    |  H   |  L  |  L  |  L > H  | No Cambia |
    +--------+------+-----+-----+---------+-----------+
    |   L    |  H   |  L  |  H  |  L > H  |     L     |
    +--------+------+-----+-----+---------+-----------+
    |   L    |  H   |  H  |  L  |  L > H  |     H     |
    +--------+------+-----+-----+---------+-----------+
    |   L    |  H   |  H  |  H  |  L > H  |  Cambia   |
    +--------+------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i`  -- entrada de clock
        - `prst_i` -- preset asincronico  
        - `ce_i`   -- clock enable
        - `j_i`    -- J in 
        - `k_i`    -- K in 
        - `q_o`    -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, prst_i.posedge)
    def FJK_PE_hdl() :

        if prst_i :
            q_aux.next = Hi
        
        else :
            if ce_i :
                if j_i :
                    if k_i :
                        q_aux.next = not q_aux
                    else :
                        q_aux.next = Hi
                else :
                    if k_i :
                        q_aux.next = Lo


    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

#################################################################

def FJK_CP(clk_i,
           clr_i, 
           prst_i, 
           j_i, 
           k_i, 
           q_o) :
    """Flip flop tipo JK con clear y preset asincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| prst_i                 |
            |________________________|
  

    Tabla de verdad

    +-------+--------+-----+-----+---------+-----------+
    | clr_i | prst_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+========+=====+=====+=========+===========+
    |   H   |   X    |  X  |  X  |    X    |     L     |
    +-------+--------+-----+-----+---------+-----------+
    |   L   |   H    |  X  |  X  |    X    |     H     |
    +-------+--------+-----+-----+---------+-----------+
    |   L   |   L    |  L  |  L  |  L > H  | No Cambia |
    +-------+--------+-----+-----+---------+-----------+
    |   L   |   L    |  L  |  H  |  L > H  |     L     |
    +-------+--------+-----+-----+---------+-----------+
    |   L   |   L    |  H  |  L  |  L > H  |     H     |
    +-------+--------+-----+-----+---------+-----------+
    |   L   |   L    |  H  |  H  |  L > H  |  Cambia   |
    +-------+--------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico  
        - `prst_i` -- preset asincronico  
        - `j_i`    -- J in 
        - `k_i`    -- K in 
        - `q_o`    -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge, prst_i.posedge)
    def FJK_CP_hdl() :
        
        if clr_i :
            q_aux.next = Lo

        elif prst_i :
            q_aux.next = Hi 

        else :
            if j_i :
                if k_i :
                    q_aux.next = not q_aux
                else :
                    q_aux.next = Hi
            else :
                if k_i :
                    q_aux.next = Lo

    @always_comb
    def conex_q() :
        q_o.next = q_aux


    return instances()

#################################################################

def FJK_CPE(clk_i, 
            clr_i, 
            prst_i, 
            ce_i, 
            j_i, 
            k_i, 
            q_o) :
    """Flip flop tipo JK con clock enable, clear y preset asincronico
    ::
 
             ________________________
            |                        |
        ----| j_i                q_o |----
            |                        |
        ----| k_i                    |
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| prst_i                 |
            |________________________|
  

    Tabla de verdad

    +-------+--------+------+-----+-----+---------+-----------+
    | clr_i | prst_i | ce_i | j_i | k_i |  clk_i  |    q_o    |
    +=======+========+======+=====+=====+=========+===========+
    |   H   |   X    |  X   |  X  |  X  |    X    |     L     |
    +-------+--------+------+-----+-----+---------+-----------+
    |   L   |   H    |  X   |  X  |  X  |    X    |     H     |
    +-------+--------+------+-----+-----+---------+-----------+
    |   L   |   L    |  L   |  X  |  X  |    X    | No Cambia |
    +-------+--------+------+-----+-----+---------+-----------+
    |   L   |   L    |  H   |  L  |  L  |  L > H  | No Cambia |
    +-------+--------+------+-----+-----+---------+-----------+
    |   L   |   L    |  H   |  L  |  H  |  L > H  |     L     |
    +-------+--------+------+-----+-----+---------+-----------+
    |   L   |   L    |  H   |  H  |  L  |  L > H  |     H     |
    +-------+--------+------+-----+-----+---------+-----------+
    |   L   |   L    |  H   |  H  |  H  |  L > H  |  Cambia   |
    +-------+--------+------+-----+-----+---------+-----------+
 
    
    :Parametros:
        - `clk_i` -- entrada de clock
        - `clr_i` -- clear asincronico  
        - `pst_i` -- preset asincronico  
        - `ce_i`  -- clock enable
        - `j_i`   -- J in 
        - `k_i`   -- K in 
        - `q_o`   -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge, prst_i.posedge)
    def FJK_CPE_hdl() :
        
        if clr_i :
            q_aux.next = Lo

        elif prst_i :
            q_aux.next = Hi 

        else :
            if ce_i :
                if j_i :
                    if k_i :
                        q_aux.next = not q_aux
                    else :
                        q_aux.next = Hi
                else :
                    if k_i :
                        q_aux.next = Lo

    @always_comb
    def conex_q() :
        q_o.next = q_aux


    return instances()

##########################################################


def FT(clk_i, 
       t_i, 
       q_o) :
    """Flip flop T 
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |________________________|
  
    
    Tabla de verdad
    
    +-----+---------+-----------+
    | t_i |  clk_i  |    q_o    |
    +=====+=========+===========+
    |  L  |  L > H  | No cambia |
    +-----+---------+-----------+
    |  H  |  L > H  |  Cambia   |
    +-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """
    
    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_hdl() :
        if t_i :
            q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

##################################################################

def FT_E(clk_i, 
         ce_i, 
         t_i, 
         q_o) :
    """Flip flop T con clock enable
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| ce_i                   |
            |________________________|
  
    
    Tabla de verdad
    
    +-------+-----+---------+-----------+
    | ce_i  | t_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   L   |  X  |   X     | No Cambia |
    +-------+-----+---------+-----------+
    |   H   |  L  |  L > H  | No cambia |
    +-------+-----+---------+-----------+
    |   H   |  H  |  L > H  |  Cambia   |
    +-------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_E_hdl() :
        if ce_i :
            if t_i :
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

##################################################################

def FT_R(clk_i, 
         rst_i, 
         t_i, 
         q_o) :
    """Flip flop T con reset sincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |________________________|
  
    
    Tabla de verdad

    +-------+-----+---------+-----------+
    | rst_i | t_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   H   |  X  |  L > H  |     L     |
    +-------+-----+---------+-----------+
    |   L   |  L  |  L > H  | No cambia |
    +-------+-----+---------+-----------+
    |   L   |  H  |  L > H  |  Cambia   |
    +-------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `rst_i`  -- reset sincronico
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_R_hdl() :
        if rst_i :
            q_aux.next = Lo
        else :
            if t_i : 
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_S(clk_i, 
         set_i, 
         t_i, 
         q_o) :
    """Flip flop T con set sincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| set_i                  |
            |________________________|
  
    
    Tabla de verdad

    +-------+-----+---------+-----------+
    | set_i | t_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   H   |  X  |  L > H  |     H     |
    +-------+-----+---------+-----------+
    |   L   |  L  |  L > H  | No cambia |
    +-------+-----+---------+-----------+
    |   L   |  H  |  L > H  |  Cambia   |
    +-------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `set_i`  -- set sincronico
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_S_hdl() :
        if set_i :
            q_aux.next = Hi
        else :
            if t_i : 
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_RE(clk_i, 
          rst_i, 
          ce_i, 
          t_i, 
          q_o) :
    """Flip flop T con clock enable y reset sincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  
    
    Tabla de verdad

    +-------+------+-----+---------+-----------+
    | rst_i | ce_i | t_i |  clk_i  |    q_o    |
    +=======+======+=====+=========+===========+
    |   H   |  X   |  X  |  L > H  |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  L   |  X  |    X    | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  L  |  L > H  | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  H  |  L > H  |  Cambia   |
    +-------+------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `rst_i`  -- reset sincronico
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_RE_hdl() :
        if rst_i :
            q_aux.next = Lo
        else :
            if ce_i :
                if t_i : 
                    q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_SE(clk_i, 
          set_i, 
          ce_i, 
          t_i, 
          q_o) :
    """Flip flop T con clock enable y set sincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| set_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  
    
    Tabla de verdad

    +-------+------+-----+---------+-----------+
    | set_i | ce_i | t_i |  clk_i  |    q_o    |
    +=======+======+=====+=========+===========+
    |   H   |  X   |  X  |  L > H  |     H     |
    +-------+------+-----+---------+-----------+
    |   L   |  L   |  X  |    X    | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  L  |  L > H  | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  H  |  L > H  |  Cambia   |
    +-------+------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `set_i`  -- set sincronico
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_SE_hdl() :
        if set_i :
            q_aux.next = Hi
        else :
            if ce_i :
                if t_i : 
                    q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_RS(clk_i, 
          rst_i, 
          set_i, 
          t_i, 
          q_o) :
    """Flip flop T con reset y set sincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |________________________|
  
    
    Tabla de verdad

    +-------+-------+-----+---------+-----------+
    | rst_i | set_i | t_i |  clk_i  |    q_o    |
    +=======+=======+=====+=========+===========+
    |   H   |   X   |  X  |  L > H  |     L     |
    +-------+-------+-----+---------+-----------+
    |   L   |   H   |  X  |  L > H  |     H     |
    +-------+-------+-----+---------+-----------+
    |   L   |   L   |  L  |  L > H  | No Cambia |
    +-------+-------+-----+---------+-----------+
    |   L   |   L   |  H  |  L > H  |  Cambia   |
    +-------+-------+-----+---------+-----------+


    :Parametros:
        - `clk_i`  -- entrada de clock
        - `rst_i`  -- reset sincronico
        - `set_i`  -- set sincronico
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """


    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_RS_hdl() :
        if rst_i :
            q_aux.next = Lo

        elif set_i :
            q_aux.next = Hi
                   
        else :
            if t_i : 
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_RSE(clk_i, 
           rst_i, 
           set_i, 
           ce_i, 
           t_i, 
           q_o) :
    """Flip Flop T con clock enable, reset y set sincronico
    ::
 
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| rst_i                  |
            |                        |
        ----| set_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad
 
    +-------+-------+------+-----+---------+-----------+
    | rst_i | set_i | ce_i | t_i |  clk_i  |    q_o    |
    +=======+=======+======+=====+=========+===========+
    |   H   |   X   |  X   |  X  |  L > H  |     L     |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   H   |  X   |  X  |  L > H  |     H     |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   L   |  L   |  X  |    X    | No Cambia |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   L   |  H   |  L  |  L > H  | No Cambia |
    +-------+-------+------+-----+---------+-----------+
    |   L   |   L   |  H   |  H  |  L > H  |  Cambia   |
    +-------+-------+------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `rst_i`  -- reset sincronico
        - `set_i`  -- set sincronico
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 
 
    """


    q_aux = Signal(Lo)

    @always(clk_i.posedge)
    def FT_RSE_hdl() :
        if rst_i :
            q_aux.next = Lo

        elif set_i :
            q_aux.next = Hi
                   
        else :
            if ce_i :
                if t_i : 
                    q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

#############################################################


def FT_C(clk_i, 
         clr_i, 
         t_i, 
         q_o) :
    """Flip flop T con clar asincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |________________________|
  
    
    Tabla de verdad

    +-------+-----+---------+-----------+
    | clr_i | t_i |  clk_i  |    q_o    |
    +=======+=====+=========+===========+
    |   H   |  X  |    X    |     L     |
    +-------+-----+---------+-----------+
    |   L   |  L  |  L > H  | No cambia |
    +-------+-----+---------+-----------+
    |   L   |  H  |  L > H  |  Cambia   |
    +-------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge)
    def FT_C_hdl() :
        if clr_i :
            q_aux.next = Lo
        else :
            if t_i : 
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_P(clk_i, 
         prst_i, 
         t_i, 
         q_o) :
    """Flip flop T con preset asincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| prst_i                 |
            |________________________|
  
    
    Tabla de verdad

    +--------+-----+---------+-----------+
    | prst_i | t_i |  clk_i  |    q_o    |
    +========+=====+=========+===========+
    |   H    |  X  |    X    |     H     |
    +--------+-----+---------+-----------+
    |   L    |  L  |  L > H  | No cambia |
    +--------+-----+---------+-----------+
    |   L    |  H  |  L > H  |  Cambia   |
    +--------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `prst_i` -- preset asincronico
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """


    q_aux = Signal(Lo)

    @always(clk_i.posedge, prst_i.posedge)
    def FT_P_hdl() :
        if prst_i :
            q_aux.next = Hi
        else :
            if t_i : 
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_CE(clk_i, 
          clr_i, 
          ce_i, 
          t_i, 
          q_o) :
    """Flip flop T con clock enable y clear asincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| ce_i                   |
            |________________________|
  
    
    Tabla de verdad

    +-------+------+-----+---------+-----------+
    | clr_i | ce_i | t_i |  clk_i  |    q_o    |
    +=======+======+=====+=========+===========+
    |   H   |  X   |  X  |    X    |     L     |
    +-------+------+-----+---------+-----------+
    |   L   |  L   |  X  |    X    | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  L  |  L > H  | No Cambia |
    +-------+------+-----+---------+-----------+
    |   L   |  H   |  H  |  L > H  |  Cambia   |
    +-------+------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """


    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge)
    def FT_CE_hdl() :
        if clr_i :
            q_aux.next = Lo
        else :
            if ce_i :
                if t_i : 
                    q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_PE(clk_i, 
          prst_i, 
          ce_i, 
          t_i, 
          q_o) :
    """Flip flop T con clock enable y preset asincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| prst_i                 |
            |                        |
        ----| ce_i                   |
            |________________________|
  
    
    Tabla de verdad

    +--------+------+-----+---------+-----------+
    | prst_i | ce_i | t_i |  clk_i  |    q_o    |
    +========+======+=====+=========+===========+
    |   H    |  X   |  X  |    X    |     H     |
    +--------+------+-----+---------+-----------+
    |   L    |  L   |  X  |    X    | No Cambia |
    +--------+------+-----+---------+-----------+
    |   L    |  H   |  L  |  L > H  | No Cambia |
    +--------+------+-----+---------+-----------+
    |   L    |  H   |  H  |  L > H  |  Cambia   |
    +--------+------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `prst_i` -- preset asincronico
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, prst_i.posedge)
    def FT_PE_hdl() :
        if prst_i :
            q_aux.next = Hi
        else :
            if ce_i :
                if t_i : 
                    q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################

def FT_CP(clk_i, 
          clr_i, 
          prst_i, 
          t_i, 
          q_o) :
    """Flip flop T con clear y preset asincronico
    ::
    
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| prst_i                 |
            |________________________|
  
    
    Tabla de verdad

    +-------+--------+-----+---------+-----------+
    | clr_i | prst_i | t_i |  clk_i  |    q_o    |
    +=======+========+=====+=========+===========+
    |   H   |   X    |  X  |    X    |     L     |
    +-------+--------+-----+---------+-----------+
    |   L   |   H    |  X  |    X    |     H     |
    +-------+--------+-----+---------+-----------+
    |   L   |   L    |  L  |  L > H  | No Cambia |
    +-------+--------+-----+---------+-----------+
    |   L   |   L    |  H  |  L > H  |  Cambia   |
    +-------+--------+-----+---------+-----------+

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico
        - `prst_i` -- preset asincronico
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 

    """


    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge, prst_i.posedge)
    def FT_CP_hdl() :
        if clr_i :
            q_aux.next = Lo

        elif prst_i :
            q_aux.next = Hi
 
        else :
            if t_i : 
                q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

####################################################################


def FT_CPE(clk_i, 
           clr_i, 
           prst_i, 
           ce_i, 
           t_i, 
           q_o) :
    """Flip Flop T con clock enable, clear y preset asincronico
    ::
 
             ________________________
            |                        |
        ----| t_i                q_o |----
            |                        |
        ----|> clk_i                 |
            |                        |
        ----| clr_i                  |
            |                        |
        ----| prst_i                 |
            |                        |
        ----| ce_i                   |
            |________________________|
  

    Tabla de verdad
 
    +-------+--------+------+-----+---------+-----------+
    | clr_i | prst_i | ce_i | t_i |  clk_i  |    q_o    |
    +=======+========+======+=====+=========+===========+
    |   H   |   X    |  X   |  X  |    X    |     L     |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   H    |  X   |  X  |    X    |     H     |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   L    |  L   |  X  |    X    | No Cambia |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   L    |  H   |  L  |  L > H  | No Cambia |
    +-------+--------+------+-----+---------+-----------+
    |   L   |   L    |  H   |  H  |  L > H  |  Cambia   |
    +-------+--------+------+-----+---------+-----------+
  

    :Parametros:
        - `clk_i`  -- entrada de clock
        - `clr_i`  -- clear asincronico
        - `prst_i` -- preset asincronico
        - `ce_i`   -- clock enable
        - `t_i`    -- toggle in 
        - `q_o`    -- data out 
 
    """

    q_aux = Signal(Lo)

    @always(clk_i.posedge, clr_i.posedge, prst_i.posedge)
    def FT_CPE_hdl() :
        if clr_i :
            q_aux.next = Lo

        elif prst_i :
            q_aux.next = Hi
 
        else :
            if ce_i :
                if t_i : 
                    q_aux.next = not q_aux

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

#############################################################

