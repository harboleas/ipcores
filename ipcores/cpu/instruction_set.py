from myhdl import *
"""
Instruction set :


        Inst.    |      Operacion       |                Opcode 16 bits
    -------------+----------------------+------------------------------------------------    
    ADD Ra, K    |  Ra <- Ra + K        |  0 0 0 0 0 . Ra Ra Ra . K  K  K  K  K  K  K  K  
    ADD Ra, Rb   |  Ra <- Ra + Rb       |  0 0 0 0 1 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    -------------+----------------------+------------------------------------------------
    AND Ra, K    |  Ra <- Ra & K        |  0 0 0 1 0 . Ra Ra Ra . K  K  K  K  K  K  K  K  
    AND Ra, Rb   |  Ra <- Ra & Rb       |  0 0 0 1 1 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    -------------+----------------------+------------------------------------------------
    CALL PCK     |  PC <- PCK           |  0 0 1 0 0 . K  K  K  . K  K  K  K  K  K  K  K
    -------------+----------------------+------------------------------------------------
    CMP Ra, K    |  Ra - K              |  0 0 1 0 1 . Ra Ra Ra . K  K  K  K  K  K  K  K  
    CMP Ra, Rb   |  Ra - Rb             |  0 0 1 1 0 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    -------------+----------------------+------------------------------------------------
    JC  PCK      |  PC <- PCK si C = 1  |  0 0 1 1 1 . K  K  K  . K  K  K  K  K  K  K  K
    JMP PCK      |  PC <- PCK           |  0 1 0 0 0 . K  K  K  . K  K  K  K  K  K  K  K
    JZ  PCK      |  PC <- PCK si Z = 1  |  0 1 0 0 1 . K  K  K  . K  K  K  K  K  K  K  K
    -------------+----------------------+------------------------------------------------
    MOV Ra, K    |  Ra <- K             |  0 1 0 1 0 . Ra Ra Ra . K  K  K  K  K  K  K  K
    MOV Ra, Rb   |  Ra <- Rb            |  0 1 0 1 1 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    MOV Ra, [K]  |  Ra <- addr(K)       |  0 1 1 0 0 . Ra Ra Ra . K  K  K  K  K  K  K  K
    MOV Ra, [Rb] |  Ra <- addr(Rb)      |  0 1 1 0 1 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    MOV [K], Ra  |  addr(K) <- Ra       |  0 1 1 1 0 . Ra Ra Ra . K  K  K  K  K  K  K  K
    MOV [Rb], Ra |  addr(Rb) <- Ra      |  0 1 1 1 1 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    -------------+----------------------+------------------------------------------------ 
    NOP          |  No operation        |  1 0 0 0 0 . 0  0  0  . 0  0  0  0  0  0  0  0
    -------------+----------------------+------------------------------------------------ 
    NOT Ra       |  Ra <- !Ra           |  1 0 0 0 1 . Ra Ra Ra . 0  0  0  0  0  0  0  0
    -------------+----------------------+------------------------------------------------
    OR Ra, K     |  Ra <- Ra | K        |  1 0 0 1 0 . Ra Ra Ra . K  K  K  K  K  K  K  K  
    OR Ra, Rb    |  Ra <- Ra | Rb       |  1 0 0 1 1 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0  
    -------------+----------------------+------------------------------------------------
    RET          |  PC <- stack         |  1 0 1 0 0 . 0  0  0  . 0  0  0  0  0  0  0  0
    -------------+----------------------+------------------------------------------------ 
    SHL Ra       |  Ra <- Ra << 1       |  1 0 1 0 1 . Ra Ra Ra . 0  0  0  0  0  0  0  0
    SHR Ra       |  Ra <- Ra >> 1       |  1 0 1 1 0 . Ra Ra Ra . 0  0  0  0  0  0  0  0       
    -------------+----------------------+------------------------------------------------
    SUB Ra, K    |  Ra <- Ra - K        |  1 0 1 1 1 . Ra Ra Ra . K  K  K  K  K  K  K  K  
    SUB Ra, Rb   |  Ra <- Ra - Rb       |  1 1 0 0 0 . Ra Ra Ra . Rb Rb Rb 0  0  0  0  0
    -------------+----------------------+------------------------------------------------
    
    Nota : todas la operaciones modifican el flag de carry y el del zero

"""

(ADD_RA_K, ADD_RA_RB, 
 AND_RA_K, AND_RA_RB, 
 CALL_PCK, 
 CMP_RA_K, CMP_RA_RB,
 JC_PCK, JMP_PCK, JZ_PCK,
 MOV_RA_K, MOV_RA_RB, MOV_RA_Addr_K, MOV_RA_Addr_RB, MOV_Addr_K_RA, MOV_Addr_RB_RA,
 NOP,
 NOT_RA,
 OR_RA_K, OR_RA_RB,
 RET,
 SHL_RA, SHR_RA,
 SUB_RA_K, SUB_RA_RB) = range(25) 


