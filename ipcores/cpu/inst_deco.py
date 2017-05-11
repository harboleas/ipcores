"""
Instruction Decoder
===================

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar> 
------------------------------------------------
"""

from myhdl import *
from instruction_set import *
from alu import alu_fun

Hi = True       # Definicion de niveles logicos
Lo = False      

def inst_deco(ir_i,              
              status_reg_i,

              addr_a_o,
              addr_b_o,
              k_o,
              pck_o,

              ctrl_mux_reg_k_o,    
              alu_fun_o,
              ctrl_mux_alu_mem_o,
              we_reg_file_o,
              ce_status_reg_o,
              inc_pc_o,
              wr_mem_o,
              rd_mem_o,
              jmp_o,
              call_o,
              ret_o) :

    """Decodifica la instruccion que se encuentra en la direccion apuntada por el Program Counter y genera las senales de control para ejecutarla

       :: 
                   -----------------------------------
                   |        |  Ra (3) |      K (8)   |               
                   |        |------------------------|    buses      |-  addr_a_o    
            ir_i : | op (5) |  Ra (3) | Rb (3) |  0  | ------------->|-  addr_b_o
                   |        |------------------------|               |-  k_o
                   |        |       PCK (11)         |               |-  pck_o
                   -----------------------------------       
                       | 
                       | 
                       | 
                       |
                       |      ------------        |-  ctrl_mux_reg_k_o
                       |      |          |        |-  alu_fun_o
                       ------>|          |        |-  ctrl_mux_alu_mem_o
                              |   DECO   |------->|-  we_reg_file_o 
            status_reg_i ---->|          |        |-  ce_status_reg_o
                              |          |        |-  inc_pc_o
                              ------------        |-  wr_mem_o
                                                  |-  rd_mem_o          
                                                  |-  jmp_o
                                                  |-  call_o
                                                  |-  ret_o

    """

       
    opcode = Signal(intbv(0)[5:])

    @always_comb
    def buses() :
        opcode.next = ir_i[16 : 11]    # Codigo de operacion

        addr_a_o.next = ir_i[11 : 8]   # Direccion de Ra en el reg file
        addr_b_o.next = ir_i[8 : 5]    # Direccion de Rb en el reg file
        k_o.next = ir_i[8:]            # Literal
        pck_o.next = ir_i[11:]         # Direccion de memoria de prog


    @always_comb
    def deco() :

        if opcode == ADD_RA_K :                 # Ra <- Ra + K 
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_ADD    # ALU = Ra + K 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en Ra    
            we_reg_file_o.next = Hi             # Escribir en el reg file (en Ra)        
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion (incrementa el contador de programa) 
            
            rd_mem_o.next = Lo                  # Las demas salidas se setean para que no tengan efecto
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == ADD_RA_RB :              # Ra <- Ra + Rb
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb del reg file como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_ADD    # ALU = Ra + Rb 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file (en Ra)        
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == AND_RA_K :               # Ra <- Ra & K
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_AND    # ALU = Ra & K 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion
            
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == AND_RA_RB :              # Ra <- Ra & Rb
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb del reg file como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_AND    # ALU = Ra & Rb 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == CALL_PCK :
            call_o.next = Hi         
            jmp_o.next = Lo         
            ret_o.next = Lo         
            inc_pc_o.next = Lo              

            ctrl_mux_reg_k_o.next = Lo      
            alu_fun_o.next = alu_fun.ALU_OPA     
            ctrl_mux_alu_mem_o.next = Lo        
            we_reg_file_o.next = Lo                  
            ce_status_reg_o.next = Lo       
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   

        elif opcode == CMP_RA_K :               # Modifica C,Z segun Ra - K
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_SUB    # ALU = Ra - K 
            ctrl_mux_alu_mem_o.next = Lo        #      
            we_reg_file_o.next = Lo             # No escribir en el reg file ya que el resultado no se guarda         
            ce_status_reg_o.next = Hi           # solo se actualizan los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion
            
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == CMP_RA_RB :              # Modifica C,Z segun Ra - Rb
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb del reg file como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_AND    # ALU = Ra - Rb 
            ctrl_mux_alu_mem_o.next = Lo        #     
            we_reg_file_o.next = Lo             # No escribir en el reg file ya que el resultado no se guarda        
            ce_status_reg_o.next = Hi           # solo se actualizan los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == JC_PCK :                 # Salta si el carry == 1
            if status_reg_i[1] :                          
                jmp_o.next = Hi         
                inc_pc_o.next = Lo              
                call_o.next = Lo         
                ret_o.next = Lo         
            else :                          
                jmp_o.next = Lo         
                inc_pc_o.next = Hi              
                call_o.next = Lo         
                ret_o.next = Lo         

            ctrl_mux_reg_k_o.next = Lo      
            alu_fun_o.next = alu_fun.ALU_OPA             
            ctrl_mux_alu_mem_o.next = Lo        
            we_reg_file_o.next = Lo                  
            ce_status_reg_o.next = Lo       
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   

        elif opcode == JMP_PCK :               # Salto incondicional 
            jmp_o.next = Hi         
            inc_pc_o.next = Lo              
            call_o.next = Lo         
            ret_o.next = Lo         

            ctrl_mux_reg_k_o.next = Lo      
            alu_fun_o.next = alu_fun.ALU_OPA             
            ctrl_mux_alu_mem_o.next = Lo        
            we_reg_file_o.next = Lo                  
            ce_status_reg_o.next = Lo       
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   

        elif opcode == JZ_PCK :                # Salta si zero == 1
            if status_reg_i[0] :                         
                jmp_o.next = Hi         
                inc_pc_o.next = Lo              
                call_o.next = Lo         
                ret_o.next = Lo         
            else :                          
                jmp_o.next = Lo         
                inc_pc_o.next = Hi              
                call_o.next = Lo         
                ret_o.next = Lo         

            ctrl_mux_reg_k_o.next = Lo      
            alu_fun_o.next = alu_fun.ALU_OPA             
            ctrl_mux_alu_mem_o.next = Lo        
            we_reg_file_o.next = Lo                  
            ce_status_reg_o.next = Lo       
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   


        elif opcode == MOV_RA_K :               # Ra <- K
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_OPB    # ALU = K 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion
            
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         


        elif opcode == MOV_RA_RB :              # Ra <- Rb
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb del reg file como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_OPB    # ALU = Rb 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == MOV_RA_Addr_K :          # Ra <- Addr(K)
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como direccion de la mem
            rd_mem_o.next = Hi                  # Preparo para leer desde la mem
            wr_mem_o.next = Lo                   
            ctrl_mux_alu_mem_o.next = Hi        # Elijo la salida de la mem para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            alu_fun_o.next = alu_fun.ALU_OPA      
            ce_status_reg_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == MOV_RA_Addr_RB :         # Ra <- Addr(Rb)
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb como direccion de la mem
            rd_mem_o.next = Hi                  # Preparo para leer desde la mem
            wr_mem_o.next = Lo                   
            ctrl_mux_alu_mem_o.next = Hi        # Elijo la salida de la mem para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            alu_fun_o.next = alu_fun.ALU_OPA      
            ce_status_reg_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == MOV_Addr_K_RA :          # Addr(K) <- Ra
            alu_fun_o.next = alu_fun.ALU_OPA    # Dato para escribir en la memoria ( ALU = Ra )      
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como direccion de la mem
            rd_mem_o.next = Lo               
            wr_mem_o.next = Hi                  # Preparo para escribir la memoria                   
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            we_reg_file_o.next = Lo                  
            ctrl_mux_alu_mem_o.next = Lo        
            ce_status_reg_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == MOV_Addr_RB_RA :         # Addr(Rb) <- Ra
            alu_fun_o.next = alu_fun.ALU_OPA    # Dato para escribir en la memoria ( ALU = Ra )      
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb como direccion de la mem
            rd_mem_o.next = Lo               
            wr_mem_o.next = Hi                  # Preparo para escribir la memoria                   
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            we_reg_file_o.next = Lo                  
            ctrl_mux_alu_mem_o.next = Lo        
            ce_status_reg_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == NOP :
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            ctrl_mux_reg_k_o.next = Lo       
            alu_fun_o.next = alu_fun.ALU_OPA       
            ctrl_mux_alu_mem_o.next = Lo         
            we_reg_file_o.next = Lo                  
            ce_status_reg_o.next = Lo       
            wr_mem_o.next = Lo
            rd_mem_o.next = Lo
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == NOT_RA :                 # Ra <- !Ra
            alu_fun_o.next = alu_fun.ALU_NOT    # ALU = !Ra 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            ctrl_mux_reg_k_o.next = Lo      
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == OR_RA_K :                # Ra <- Ra | K
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_OR     # ALU = Ra | K 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion
            
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == OR_RA_RB :               # Ra <- Ra | Rb
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb del reg file como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_OR     # ALU = Ra | Rb 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == RET :
            ret_o.next = Hi         
            call_o.next = Lo         
            jmp_o.next = Lo         
            inc_pc_o.next = Lo              

            ctrl_mux_reg_k_o.next = Lo      
            alu_fun_o.next = alu_fun.ALU_OPA     
            ctrl_mux_alu_mem_o.next = Lo        
            we_reg_file_o.next = Lo                  
            ce_status_reg_o.next = Lo       
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   


        elif opcode == SHL_RA :                 # Ra <- Ra << 1
            alu_fun_o.next = alu_fun.ALU_SHL    # ALU = Ra << 1 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            ctrl_mux_reg_k_o.next = Lo      
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == SHR_RA :                 # Ra <- Ra >> 1
            alu_fun_o.next = alu_fun.ALU_SHR    # ALU = Ra >> 1 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            ctrl_mux_reg_k_o.next = Lo      
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == SUB_RA_K :               # Ra <- Ra - K 
            ctrl_mux_reg_k_o.next = Hi          # Selecciono K como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_SUB    # ALU = Ra - K 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en Ra    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion (incrementa el contador de programa) 
            
            rd_mem_o.next = Lo              
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        elif opcode == SUB_RA_RB :              # Ra <- Ra - Rb
            ctrl_mux_reg_k_o.next = Lo          # Selecciono Rb del reg file como operando B de la ALU
            alu_fun_o.next = alu_fun.ALU_SUB    # ALU = Ra - Rb 
            ctrl_mux_alu_mem_o.next = Lo        # Elijo el resultado de la ALU para guardar en el reg file    
            we_reg_file_o.next = Hi             # Escribir en el reg file         
            ce_status_reg_o.next = Hi           # actualiza los registros de carry y zero
            inc_pc_o.next = Hi                  # Apunta a la proxima instruccion

            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         

        else :

            ctrl_mux_reg_k_o.next = Lo          
            alu_fun_o.next = alu_fun.ALU_OPA     
            ctrl_mux_alu_mem_o.next = Lo            
            we_reg_file_o.next = Lo                      
            ce_status_reg_o.next = Lo           
            inc_pc_o.next = Lo                  
            rd_mem_o.next = Lo
            wr_mem_o.next = Lo                   
            jmp_o.next = Lo         
            call_o.next = Lo         
            ret_o.next = Lo         


    return instances()

