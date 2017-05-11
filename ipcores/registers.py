# registers.py
# ============
# 
# Registros y Flip Flops
# 
# Author : 
#     Hugo Arboleas, <harboleas@citedef.gob.ar>
# 
####################################################

from myhdl import *

def reg(clk_i,
        rst_i,
        ce_i,
        d_i,
        q_o) :
    """
    Registro tipo D 
    
    Inputs

    *   clk_i - Clock
    *   rst_i - Reset 
    *   ce_i  - Clock enable 
    *   d_i   - Data in (n bits)
    
    Outputs
           
    *   q_o   - Data out (n bits)

    """ 

    @always(clk_i.posedge, rst_i.posedge)
    def rtl() :
        if rst_i :
            q_o.next = 0
        else : # rising clk
            if ce_i :
                q_o.next = d_i

    return instances()

#############################################
            
def count(clk_i, 
          rst_i,
          ce_i,
          q_o) :

    """
    Contador binario

    Inputs

    *   clk_i  - Clock
    *   rst_i  - Reset 
    *   ce_i   - Clock enable
    
    Outputs

    *   q_o    - Data out (n bits)

    """

    n = len(q_o)  

    i = Signal(modbv(0)[n:]) # registro para contar 

    @always(clk_i.posedge, rst_i.posedge)
    def rtl() :
        if rst_i :
            i.next = 0
        else : # rising clk
            if ce_i :
                i.next = i + 1

    @always_comb
    def out() :
        q_o.next = i

    return instances()

#############################################

def accum(clk_i,
          rst_i,
          load_i,
          d_i,
          ce_i,
          b_i,
          q_o) :
    """
    Acumulador 
    
    Inputs

    *   clk_i  - Clock
    *   rst_i  - Reset 
    *   load_i - Load data 
    *   d_i    - Data in (n bits)
    *   ce_i   - Clock enable 
    *   b_i    - Accumulator in (m bits)

    Outputs

    *   q_o    - Accumulator out (n bits)

    """  

    n = len(q_o) 

    a = Signal(intbv(0)[n:])  # registro acumulador 

    @always(clk_i.posedge, rst_i.posedge)
    def rtl() :
        if rst_i :
            a.next = 0
        else :  # rising clk
            if load_i :         
                a.next = d_i
            elif ce_i :
                a.next = a + b

    @always_comb
    def out() :
        q_o.next = a

    return instances()

#############################################

def add_sub(a_i,
            b_i,
            add_i,
            s_o) :
    """
    Sumador / Restador

    Inputs

    *   a_i   - Operando 1 
    *   b_i   - Operando 2 
    *   add_i - Selecciona oper. 0 : resta, 1 : suma

    Outputs

    *   s_o   - Resultado de la operacion 

    """

    @always_comb
    def oper() :
        if add_i :
            s_o.next = a_i + b_i
        else :
            s_o.next = a_i - b_i

    return instances()

#############################################

def pos_edge_detect(clk_i,
                    a_i,
                    q_o) :

    """
    Detector de flanco de subida 

    Inputs

    *   clk_i  - clock in
    *   a_i    - data in

    Outputs

    *   q_o   - rising edge

    Operacion :

                  _   _   _   _   _   _
        clk_i    | |_| |_| |_| |_| |_| |
                          _____________
        a_i      ________|
                              _________
        a_q      ____________|
                          ___         
        q_o      ________|   |__________
                
    """

    a_q = Signal(False) 

    @always(clk_i.posedge)
    def reg() :
        a_q.next = a_i

    @always_comb
    def detect() :
        up_o.next =  a_i and (not a_q)
        down_o.next = (not a_i) and a_q

    return instances()

#############################################

def neg_edge_detect(clk_i,
                    a_i,
                    q_o) :

    """
    Detector de flanco de bajada 

    Inputs

    *   clk_i  - clock in
    *   a_i    - data in

    Outputs

    *   q_o   - falling edge

    Operacion :

                    _   _   _   _   _   _  
        clk_i      | |_| |_| |_| |_| |_| | 
                 __________                
        a_i                |______________ 
                 ______________            
        a_q                    |__________ 
                            ___               
        q_o      __________|   |__________ 


    """

    a_q = Signal(False) 

    @always(clk_i.posedge)
    def reg() :
        a_q.next = a_i

    @always_comb
    def detect() :
        up_o.next =  a_i and (not a_q)
        down_o.next = (not a_i) and a_q

    return instances()


#############################################

def shift_reg(clk_i,
              rst_i,
              load_i,
              d_i,
              left_i,
              ce_i,
              sl_i,
              sr_i,
              q_o) :
    """
    Shift Register

    Inputs

    *   clk_i   - Clk
    *   rst_i   - Reset 
    *   load_i  - Load data
    *   d_i     - Data in
    *   left_i  - Shift direction. 0 : right, 1 : left
    *   ce_i    - Clock enable 
    *   sl_i    - Shift left in
    *   sr_i    - Shift right in

    Outputs

    *   q_o     - Data out

    """

    n = len(q_o) 

    aux = Signal(intbv(0)[n:])

    @always(clk_i.posedge, rst_i.posedge)
    def rtl() :
        if rst_i :
            aux.next = 0
        else :  # rising clk
            if load_i :
                aux.next = d_i
            elif ce_i :
                if left_i :
                    aux.next = concat(aux[n-1:], sl_i)
                else :
                    aux.next = concat(sr_i, aux[n:1])

    @always_comb
    def out() :
        q_o.next = aux

    return instances()

# vim: set ts=8 sw=4 tw=0 et :
