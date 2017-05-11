"""
Register File
=============

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""
from myhdl import *


def RegFile(clk_i,
            addr_a_i,
            we_i,
            a_i,
            a_o,
            addr_b_i,
            b_o) :

    """Register File de m registros de n bits 
    ::                          
                       ________________                            
                      |                |                           
             a_i ---->|    Reg File    |----> a_o 
                      |                |                 
        addr_a_i ---->|                |----> b_o                 
                      |                |                         
        addr_b_i ---->|                |                 
                      |                |                         
            we_i ---->|                |                                                      
                      |                |                         
           clk_i ---->|                |                         
                      |________________|                                                  


    :Parametros:
        - `clk_i`    :  entrada de clock
        - `addr_a_i` :  direccion de lectura y escritura canal A (log_2 m bits) 
        - `we_i`     :  write enable  
        - `a_i`      :  data in canal A (n bits)
        - `a_o`      :  data out canal A (n bits)
        - `addr_b_i` :  direccion de lectura canal B (log_2 m bits)
        - `b_o`      :  data out canal B (n bits)

    """
    
    n = len(a_i)              # Cantidad de bits de almacenamiento de los registros 

    m = 2 ** len(addr_a_i)    # Cantidad de registros

    
    reg_file_mem = [Signal(intbv(0)[n:]) for i in range(m)]    # RAM ( Dual Port ) de m registros de n bits


    ################################  

    @always(clk_i.posedge)
    def write_a() :
        if we_i :             
            reg_file_mem[addr_a_i].next = a_i                                 


    @always_comb
    def read_a() :
        a_o.next = reg_file_mem[addr_a_i]        
         
    @always_comb
    def read_b() :
        b_o.next = reg_file_mem[addr_b_i]

    return instances()

