"""
Nucleo del TZR1
===============

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar> 
------------------------------------------------

"""

from myhdl import *
from alu import alu, alu_fun
from reg_file import RegFile
from inst_deco import inst_deco
from pc import pc
from FlipFlops import FD_E

Hi = True       # Definicion de niveles logicos
Lo = False      

def TZR1(clk_i,
         rst_i,
         addr_o,        
         data_i,
         data_o,
         write_o,
         read_o,
         program) :

    """ Nucleo del micro
        ::


                                                                              .------------------------------.
                                                                              |                              |
                                                                              |                              v
              .-------------------.                                           |                   .--------------------.
              |    Program ROM    |                                           |                   |         a_i        |
              |     2Ki x 16      |   .---------------------------------.     |                   |                    |
              |                   |   |        Program Counter          |     |                   |      REG FILE      |
              |                   |   |                                 |     |                   |                    |
              |            addr_i |<--| pc_o                            |     |   we_reg_file --->| we_i               |
              |                   |   |                                 |     |                   |                    |
              |                   |   | inc_pc   jmp   call   ret   pck |     |       addr_a  --->| addr_a_i           |
              |                   |   '---------------------------------'     |                   |                    |
              |                   |       ^       ^     ^      ^     ^        |       addr_b  --->| addr_b_i           |
              |                   |       |       |     |      |     |        |                   |                    |                   
              |        d_o        |     inc_pc   jmp   call   ret   pck       |                   |                    |                   
              '-------------------'                                           |                   |    a_o       b_o   |                   
                        |                                                     |                   '--------------------'                                              
                        |                                                     |                         |         |                                                    
                        |                                                     |                         |         |    .----- K                                        
                        v                                                     |                         |         |    |                                               
            .------------------------.                                        |                         |         v    v                                               
            |         ir_i           |                                        |                         |        .-------.                                             
            |                        |                                        |                         |        |  MUX  |<--- ctrl_mux_reg_k                          
            | DECO                   |                                        |                         |        '-------'                                                         
            |                        |                                        |                         |            |                                                             |
            |         status_reg_i   |<---                                    |                         |            |--------------------------------------------------> addr_o   |                  
            |      ce_status_reg_o   |--->                                    |                         |            |                                                             |
            |            alu_fun_o   |--->                                    |                         |            |                                              ----> write_o  |          
            |             addr_a_o   |--->                                    |                         v            v                                                             |
            |             addr_b_o   |--->                                    |                       -----  ALU   -----                                            ----> read_o   |         
            |        we_reg_file_o   |--->                                    |                       \    \      /    /                                                           |
            |     ctrl_mux_reg_k_o   |--->                                    |                        \    ------    /       .------------.                                       |
            |                  k_o   |--->                                    |             alu_fun --->\            /------->| STATUS REG |---> status_reg                        |   I/O MEM
            |             wr_mem_o   |--->                                    |                          \          /         '------------'                                       |
            |   ctrl_mux_alu_mem_o   |--->                                    |                           ----------                 ^                                             |
            |             inc_pc_o   |--->                                    |                                |                     |                                             |
            |                jmp_o   |--->                                    |         .-------.              |                ce_status                                          |
            |                pck_o   |--->                                    |         |  MUX  |              |                                                                   |
            |               call_o   |--->                                    |         |       |<----------------------------------------------------------------------> data_o   |                                                         |
            |                ret_o   |--->                                    '---------|       |                                                                                  |
            |             rd_mem_o   |--->                                              |       |<----------------------------------------------------------------------- data_i   |
            '------------------------'                                                  |       |                                                                                  |
                                                                                        '-------'
                                                                                            ^
                                                                                            |
                                                                                    ctrl_mux_alu_mem
    """

    ####### Senales #######

    ########################
    #  Reg   
    addr_a = Signal(intbv(0)[3:])  # 8 Registros    
    addr_b = Signal(intbv(0)[3:])    
    we_reg_file = Signal(Lo)
    a_i = Signal(intbv(0)[8:])
    a_o = Signal(intbv(0)[8:])
    b_o = Signal(intbv(0)[8:])
    
    ########################
    # Alu
    ALU_fun = Signal(alu_fun.ALU_OPA)
    ALU_resul = Signal(intbv(0)[8:])
    ALU_status = Signal(intbv(0)[2:])

    ########################
    # Status reg
    status_reg_q = Signal(intbv(0)[2:])
    ce_status_reg = Signal(Lo)

    ########################
    # Inst Deco    
    ir = Signal(intbv(0)[16:])
    ctrl_mux_reg_k = Signal(Lo)    
    k = Signal(intbv(0)[8:])
    ctrl_mux_alu_mem = Signal(Lo)
    inc_pc = Signal(Lo)
    jmp = Signal(Lo)
    call = Signal(Lo)
    ret = Signal(Lo)
    pck = Signal(intbv(0)[11:])

    ########################
    # Program counter    

    pc_q = Signal(intbv(0)[11:]) 


    #########################
    # Muxes
    mux_alu_mem_o = Signal(intbv(0)[8:])
    mux_reg_k_o = Signal(intbv(0)[8:])
    
    ###############################
    ## Estructura

    INST_DECO = inst_deco(ir_i = ir,
                          status_reg_i = status_reg_q,
                          ce_status_reg_o = ce_status_reg,
                          alu_fun_o = ALU_fun,
                          addr_a_o = addr_a,
                          addr_b_o = addr_b,
                          we_reg_file_o = we_reg_file,
                          ctrl_mux_reg_k_o = ctrl_mux_reg_k,    
                          k_o = k,
                          wr_mem_o = write_o,
                          rd_mem_o = read_o,
                          ctrl_mux_alu_mem_o = ctrl_mux_alu_mem,
                          inc_pc_o = inc_pc,
                          jmp_o = jmp,
                          call_o = call,
                          ret_o = ret,
                          pck_o = pck) 


    PROG_COUNTER = pc(clk_i = clk_i,
                      rst_i = rst_i,
                      inc_pc_i = inc_pc,
                      jmp_i = jmp,
                      call_i = call,
                      ret_i = ret,
                      pck_i = pck,
                      pc_o = pc_q,
                      stack_size = 16) 


    @always_comb
    def ROM_read() :
        ir.next = program[int(pc_q)] 


    REG_FILE = RegFile(clk_i = clk_i,
                       addr_a_i = addr_a,
                       we_i = we_reg_file,
                       a_i = a_i,
                       a_o = a_o,
                       addr_b_i = addr_b,
                       b_o = b_o)

    ALU = alu(op_A_i = a_o,
              op_B_i = mux_reg_k_o,
              fun_i = ALU_fun,
              resul_o = ALU_resul,
              status_o = ALU_status)

    STATUS_REG = FD_E(clk_i = clk_i,
                      ce_i = ce_status_reg,
                      d_i = ALU_status,
                      q_o = status_reg_q)


    @always_comb
    def MUXES() :
        mux_reg_k_o.next = k if ctrl_mux_reg_k else b_o 
        a_i.next = data_i if ctrl_mux_alu_mem else ALU_resul
        

    @always_comb
    def conex() :
        addr_o.next = mux_reg_k_o
        data_o.next = ALU_resul


    return instances()

