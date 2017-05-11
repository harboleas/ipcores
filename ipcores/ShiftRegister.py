"""
Shift Register
==============

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *

Hi = True        # Definicion de los niveles logicos
Lo = False

##############################################################

def SR_RE_SiPo_Der(clk_i, 
                   rst_i, 
                   ce_i, 
                   sr_i, 
                   q_o) :
    """Shift register con reset sincronico y clock enable
    tipo serial in parallel out de n bits,
    con desplazamiento a derecha ::

            ________________________
           |                        |____
       ----| sr_i             q_o   |____ 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| rst_i                  |
           |________________________|
 
    
        sr_i >> q[n-1] >> ... >> q[0]     

    :Parametros:
        - `clk_i`    :  entrada de clock
        - `rst_i`    :  reset sincronico  
        - `ce_i`     :  clock enable
        - `sr_i`     :  serial right in (1 bit)
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(q_o)

    q_aux = Signal(intbv(0)[n:0])

    @always(clk_i.posedge)
    def SR_RE_SiPo_Der_hdl() :
        if rst_i :
            q_aux.next = 0
        else :
            if ce_i :
                q_aux.next = concat(sr_i, q_aux[n:1])      

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

##############################################################

def SR_RE_SiPo_Izq(clk_i, 
                   rst_i, 
                   ce_i, 
                   sl_i, 
                   q_o) :
    """Shift register con reset sincronico y clock enable, 
    tipo serial in parallel out de n bits,
    con desplazamiento a izquierda ::

            ________________________
           |                        |____
       ----| sl_i             q_o   |____ 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| rst_i                  |
           |________________________|
 
        q[n-1] << ... << q[0] << sl_i      

    :Parametros:
        - `clk_i`    :  entrada de clock
        - `rst_i`    :  reset sincronico  
        - `ce_i`     :  clock enable
        - `sl_i`     :  serial left in (1 bit)
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(q_o)

    q_aux = Signal(intbv(0)[n:0])

    @always(clk_i.posedge)
    def SR_RE_SiPo_Izq_hdl() :
        if rst_i :
            q_aux.next = 0
        else :
            if ce_i :
                q_aux.next = concat(q_aux[n-1:0], sl_i)        

    @always_comb
    def conex_q() :
        q_o.next = q_aux

    return instances()

##################################################################

def SR_RLE_PiPo_Izq(clk_i, 
                    rst_i, 
                    load_i, 
                    d_i, 
                    ce_i, 
                    q_o) :
    """Shift register con reset y carga sincronica y clock enable 
    tipo parallel in parallel out de n bits,
    con desplazamiento a izquierda ::

            ________________________
       ____|                        |____
       ____| d_i                q_o |____ 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| load_i                 |
           |                        |
       ----| rst_i                  |
           |________________________|
 
    :Parametros:
        - `clk_i`    :  entrada de clock
        - `rst_i`    :  reset sincronico  
        - `load_i`   :  carga sincronica  
        - `d_i`      :  data in (n bits)
        - `ce_i`     :  clock enable
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_RLE_PiPo_Izq_hdl() :
        if rst_i :
            aux.next = 0 
        elif load_i :
            aux.next = d_i 
        else :
            if ce_i :
                aux.next = concat(aux[n-1:0], Lo)           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

##################################################################

def SR_RLE_PiPo_Der(clk_i, 
                    rst_i, 
                    load_i, 
                    d_i, 
                    ce_i, 
                    q_o) :
    """Shift register con reset y carga sincronica y clock enable
    tipo parallel in parallel out de n bits,
    con desplazamiento a derecha ::
 
            ________________________
       ____|                        |____
       ____| d_i                q_o |____ 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| load_i                 |
           |                        |
       ----| rst_i                  |
           |________________________|
 
    :Parametros:
        - `clk_i`    :  entrada de clock
        - `rst_i`    :  reset sincronico  
        - `load_i`   :  carga  
        - `d_i`      :  data in (n bits)
        - `ce_i`     :  clock enable
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_RLE_PiPo_Der_hdl() :
        if rst_i :
            aux.next = 0 
        elif load_i :
            aux.next = d_i
        else :
            if ce_i :
                aux.next = concat(Lo, aux[n:1])           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

###############################################################
def SR_LE_PiPo_Izq(clk_i, 
                   load_i, 
                   d_i, 
                   ce_i, 
                   q_o) :
    """Shift register con carga sincronica y clock enable 
    tipo parallel in parallel out de n bits,
    con desplazamiento a izquierda ::
 
            ________________________
       ____|                        |____
       ____| d_i                q_o |____ 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| load_i                 |
           |________________________|
 
    :Parametros:
        - `clk_i`    :  entrada de clock
        - `load_i`   :  carga sincronica  
        - `d_i`      :  data in (n bits)
        - `ce_i`     :  clock enable
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_LE_PiPo_Izq_hdl() :
        if load_i :
            aux.next = d_i 
        else :
            if ce_i :
                aux.next = concat(aux[n-1:0], Lo)           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

###############################################################
def SR_LE_PiSo_Izq(clk_i, 
                   load_i, 
                   d_i, 
                   ce_i, 
                   q_o) :
    """Shift register con carga sincronica y clock enable 
    tipo parallel in serial out de n bits,
    con desplazamiento a izquierda ::
 
            ________________________
       ____|                        |
       ____| d_i                q_o |---- 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| load_i                 |
           |________________________|
 
    :Parametros:
        - `clk_i`    :  entrada de clock
        - `load_i`   :  carga sincronica  
        - `d_i`      :  data in (n bits)
        - `ce_i`     :  clock enable
        - `q_o`      :  data out (1 bit)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_LE_PiSo_Izq_hdl() :
        if load_i :
            aux.next = d_i 
        else :
            if ce_i :
                aux.next = concat(aux[n-1:0], Lo)           

    @always_comb
    def conex_q() :
        q_o.next = aux[n-1]

    return instances()


##################################################################

def SR_LE_PiPo_Der(clk_i, 
                   load_i, 
                   d_i, 
                   ce_i, 
                   q_o) :
    """Shift register con carga sincronica y clock enable
    tipo parallel in parallel out de n bits,
    con desplazamiento a derecha ::
 
            ________________________
       ____|                        |____
       ____| d_i                q_o |____ 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| load_i                 |
           |________________________|
 
    :Parametros:
        - `clk_i`    :  entrada de clock
        - `load_i`   :  carga  
        - `d_i`      :  data in (n bits)
        - `ce_i`     :  clock enable
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_LE_PiPo_Der_hdl() :
        if load_i :
            aux.next = d_i
        else :
            if ce_i :
                aux.next = concat(Lo, aux[n:1])           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

###############################################################

def SR_LE_PiSo_Der(clk_i, 
                   load_i, 
                   d_i, 
                   ce_i, 
                   q_o) :
    """Shift register con carga sincronica y clock enable
    tipo parallel in serial out de n bits,
    con desplazamiento a derecha ::
 
            ________________________
       ____|                        |
       ____| d_i                q_o |---- 
           |                        |
       ----|> clk_i                 |
           |                        |
       ----| ce_i                   |
           |                        |
       ----| load_i                 |
           |________________________|
 
    :Parametros:
        - `clk_i`    :  entrada de clock
        - `load_i`   :  carga  
        - `ce_i`     :  clock enable
        - `d_i`      :  data in (n bits)
        - `q_o`      :  data out (1 bit)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_LE_PiSo_Der_hdl() :
        if load_i :
            aux.next = d_i
        else :
            if ce_i :
                aux.next = concat(Lo, aux[n:1])           

    @always_comb
    def conex_q() :
        q_o.next = aux[0]

    return instances()

###########################################################

def SR_LE_SiPo_Izq(clk_i, 
                   load_i, 
                   d_i, 
                   ce_i, 
                   sl_i, 
                   q_o) :
    """Shift register con carga sincronica y clock enable 
    tipo serial in parallel out de n bits,
    con desplazamiento a izquierda 

    :Parametros:
        - `clk_i`    :  entrada de clock
        - `load_i`   :  carga sincronica  
        - `d_i`      :  dato a cargar (n bits) 
        - `ce_i`     :  clock enable
        - `sl_i`     :  serial left in (1 bit)
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(q_o)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_LE_SiPo_Izq_hdl() :
        if load_i :
            aux.next = d_i 
        else :
            if ce_i :
                aux.next = concat(aux[n-1:0], sl_i)           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

##################################################################

def SR_LE_SiPo_Der(clk_i, 
                   load_i, 
                   d_i, 
                   ce_i, 
                   sr_i, 
                   q_o) :
    """Shift register con carga sincronica y clock enable
    tipo serial in parallel out de n bits,
    con desplazamiento a derecha 

    :Parametros:
        - `clk_i`    :  entrada de clock
        - `load_i`   :  carga  
        - `d_i`      :  data a cargar (n bits)
        - `ce_i`     :  clock enable
        - `sr_i`     :  serial right in (1 bit)
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(q_o)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_LE_SiPo_Der_hdl() :
        if load_i :
            aux.next = d_i
        else :
            if ce_i :
                aux.next = concat(sr_i, aux[n:1])           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

###############################################################


def SR_RLE_SiPo_Izq(clk_i, 
                    rst_i, 
                    load_i, 
                    d_i, 
                    ce_i, 
                    sl_i, 
                    q_o) :
    """Shift register con carga y reset sincronico y clock enable 
    tipo serial in parallel out de n bits,
    con desplazamiento a izquierda

    :Parametros:
        - `clk_i`    :  entrada de clock
        - `rst_i`    :  reset sincronico
        - `load_i`   :  carga sincronica  
        - `d_i`      :  dato a cargar (n bits) 
        - `ce_i`     :  clock enable
        - `sl_i`     :  serial left in (1 bit)
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(d_i)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_RLE_SiPo_Izq_hdl() :
        if rst_i :
            aux.next = 0
        elif load_i :
            aux.next = d_i 
        else :
            if ce_i :
                aux.next = concat(aux[n-1:0], sl_i)           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

##################################################################

def SR_RLE_SiPo_Der(clk_i, 
                    rst_i, 
                    load_i, 
                    d_i, 
                    ce_i, 
                    sr_i, 
                    q_o) :
    """Shift register con carga y reset sincronico y clock enable
    tipo serial in parallel out de n bits,
    con desplazamiento a derecha 

    :Parametros:
        - `clk_i`    :  entrada de clock
        - `rst_i`    :  reset sincronico
        - `load_i`   :  carga  
        - `d_i`      :  data a cargar (n bits)
        - `ce_i`     :  clock enable
        - `sr_i`     :  serial right in (1 bit)
        - `q_o`      :  data out (n bits)

    """    

    # Descripcion por comportamiento

    n = len(q_o)

    aux = Signal(intbv(0)[n:0])         # registro auxiliar

    @always(clk_i.posedge)
    def SR_RLE_SiPo_Der_hdl() :
        if rst_i :
            aux.next = 0
        elif load_i :
            aux.next = d_i
        else :
            if ce_i :
                aux.next = concat(sr_i, aux[n:1])           

    @always_comb
    def conex_q() :
        q_o.next = aux

    return instances()

##############################################################
