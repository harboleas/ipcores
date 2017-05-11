"""
ALU
===

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""
from myhdl import *

alu_fun = enum("ALU_ADD", "ALU_SUB", "ALU_OPA", "ALU_OPB", "ALU_AND", "ALU_OR", "ALU_NOT", "ALU_SHL", "ALU_SHR")

Hi = True
Lo = False

def alu(op_A_i,
        op_B_i,
        fun_i,
        resul_o,
        status_o) :

    """ALU
    ::

                         op_A_i        op_B_i
                            |             |
                         ___v___       ___v___
                         \      \_____/      /
                          \                 /
                fun_i ---->\               /---> status_o
                            \             /
                             \___________/
                                   |
                                   v
                                resul_o


    :Parametros:
        - `op_A_i`   :  operando A (n bits)
        - `op_B_i`   :  operando B (n bits)
        - `fun_i`    :  selecciona la operacion 
        - `resul_o`  :  resultado de la operacion (n bits)
        - `status_o` :  salida de carry y zero
 
    
    """

    n = len(op_A_i)

    resul_temp = Signal(intbv(0, -2**n, 2**n - 1 ))
    carry = Signal(Lo)
    zero = Signal(Lo)

    @always_comb
    def operaciones() :

        if fun_i == alu_fun.ALU_ADD :
            resul_temp.next = op_A_i + op_B_i

        elif fun_i == alu_fun.ALU_SUB :
            resul_temp.next = op_A_i - op_B_i

        elif fun_i == alu_fun.ALU_OPA :
            resul_temp.next = op_A_i

        elif fun_i == alu_fun.ALU_OPB :
            resul_temp.next = op_B_i

        elif fun_i == alu_fun.ALU_AND :
            resul_temp.next = op_A_i & op_B_i

        elif fun_i == alu_fun.ALU_OR :
            resul_temp.next = op_A_i | op_B_i

        elif fun_i == alu_fun.ALU_NOT :
            resul_temp.next = ~op_A_i    

        elif fun_i == alu_fun.ALU_SHL :
            resul_temp.next = op_A_i << 1    

        elif fun_i == alu_fun.ALU_SHR :
            resul_temp.next = op_A_i >> 1    

     
    @always_comb
    def carry_zero() :
        carry.next = resul_temp[n]
        zero.next = Lo if resul_temp else Hi 


    @always_comb
    def conex_out() :
        resul_o.next = resul_temp[n:]
        status_o.next = concat(carry, zero)       


    return instances()

   
