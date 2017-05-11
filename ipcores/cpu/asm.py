"""
Assembler TZR1 
==============

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
-------------------------------------------------
"""    

import sys
import re

p = open(sys.argv[1])
pr = p.read()
p.close()

################ Analizador lexico #################

def_tokens = [("label", " *([a-z_A-Z][0-9a-z_A-Z]*) *:"),                        
              ("op", "(add|and|call|cmp|jc|jmp|jz|mov|nop|not|or|ret|shl|shr|sub)"),
              ("reg", "(r[0-9]+)"), 
              ("addr_reg", "(\[r[0-9]+\])"), 
              ("addr_ent", "(\[(?:0x[0-9a-fA-F]+|0b[01]+|[0-9]+)\])"),
              ("entero", "(0x[0-9a-fA-F]+|0b[01]+|[0-9]+)"),
              ("id", "([a-z_A-Z][0-9a-z_A-Z]*)"),
              ("comen", "(#.*)"),
              ("fin_linea", "(\n)")]

lex = "|".join(t[1] for t in def_tokens)

tok_find = re.findall(lex, pr)

tokens = []
for t in tok_find :
    for i, tok in enumerate(t) :
        if tok :
            tokens.append((def_tokens[i][0], tok))


################ Analizador sintactico #################


estado = "ESPERA_INI_INST"
etiquetas = {}
nro_instr = 0
nro_linea = 1
program_asm = []

#### Forma de una instruccion
## [label :] op [arg1, arg2] [# Comentario] 

# FSM que reconoce la sintaxis
for tipo, token in tokens :

    if estado == "ESPERA_INI_INST" :                                 # Inicio de instruccion
        if tipo in ("fin_linea", "comen", "label") :
            if tipo == "label" :
                etiquetas[token] = nro_instr      # Guarda la direccion de la instruccion a la que hace ref el label

            elif tipo == "fin_linea" :
                nro_linea += 1         # Para indicar errores de sintaxis en el archivo fuente

        elif tipo == "op" :
            op = token                 # Voy armando el tipo de instruccion para luego convertirla con la tabla 
            if token in ("nop", "ret") :            # Operaciones sin argumentos  
                arg1 = None
                arg2 = None
                program_asm.append((op, arg1, arg2)) 
                estado = "ESPERA_FIN_INST"

            elif token in ("call", "jc", "jmp", "jz", "not", "shl", "shr") :    # Operaciones con un solo argumento  
                estado = "OP_1_ARG"                       

            else :                                        # Operaciones con dos argumentos  
                estado = "OP_2_ARG"                       
        else :
            print "Error de sintaxis en la linea %d" % nro_linea 
            sys.exit()

        continue      # va por el siguiente token
    
    elif estado == "OP_1_ARG" :     # Espera solo un argumento

        if op in ("not", "shl", "shr") :     # solo operan sobre registros
            if tipo == "reg" :
                op = op + "_ra"         
                arg1 = int(token[1:])
                arg2 = None
                program_asm.append((op, arg1, arg2)) 
                estado = "ESPERA_FIN_INST"
            else : 
                print "Error de sintaxis en la linea %d" % nro_linea 
                sys.exit()

        else :   #La operacion es de salto o call
            if tipo == "entero" :
                op = op + "_pck"
                try :
                    base = token[0:2]
                except :
                    base = 10                    
                arg1 = int(token, 16 if base == "0x" else 2 if base == "0b" else 10)
                arg2 = None
                program_asm.append((op, arg1, arg2)) 
                estado = "ESPERA_FIN_INST"

            elif tipo == "id" :
                op = op + "_pck"
                arg1 = token        # Luego se debe conviertir a entero una vez que se hayan obtenido todas las etiquetas
                arg2 = None
                program_asm.append((op, arg1, arg2)) 
                estado = "ESPERA_FIN_INST"

            else :
                print "Error de sintaxis en la linea %d" % nro_linea 
                sys.exit()

        continue        # siguiente token

    elif estado == "OP_2_ARG" :   # Espera 1er argumento

        if tipo == "reg" :
            op = op + "_ra"
            arg1 = int(token[1:])
            estado = "ESPERA_2_ARG"

        elif tipo == "addr_reg" :
            if op == "mov" :
                op = op + "_addr_rb"
                arg1 = int(token[2:-1])    
                estado = "ESPERA_2_ARG_REG"
            else :
                print "Error de sintaxis en la linea %d" % nro_linea 
                sys.exit()

        elif tipo == "addr_ent" :
            if op == "mov" :
                op = op + "_addr_k"
                aux = token[1:-1]
                try :
                    base = aux[0:2]
                except :
                    base = 10                    
                arg1 = int(aux, 16 if base == "0x" else 2 if base == "0b" else 10)
                estado = "ESPERA_2_ARG_REG"

            else :
                print "Error de sintaxis en la linea %d" % nro_linea 
                sys.exit()

        else :
            print "Error de sintaxis en la linea %d" % nro_linea 
            sys.exit()
            
        continue

    elif estado == "ESPERA_2_ARG" :   

        if tipo == "reg" :
            op = op + "_rb"
            arg2 = int(token[1:])
            program_asm.append((op, arg1, arg2)) 
            estado = "ESPERA_FIN_INST"

        elif tipo == "entero" :
            op = op + "_k"
            try :
                base = token[0:2]
            except :
                base = 10                    
            arg2 = int(token, 16 if base == "0x" else 2 if base == "0b" else 10)
            program_asm.append((op, arg1, arg2)) 
            estado = "ESPERA_FIN_INST"

        elif tipo == "addr_reg" :
            if op == "mov_ra" :
                op = op + "_addr_rb"
                arg2 = int(token[2:-1])    
                program_asm.append((op, arg1, arg2)) 
                estado = "ESPERA_FIN_INST"
            else :
                print "Error de sintaxis en la linea %d" % nro_linea 
                sys.exit()

        elif tipo == "addr_ent" :
            if op == "mov_ra" :
                op = op + "_addr_k"
                aux = token[1:-1]
                try :
                    base = aux[0:2]
                except :
                    base = 10                    
                arg2 = int(aux, 16 if base == "0x" else 2 if base == "0b" else 10)
                program_asm.append((op, arg1, arg2)) 
                estado = "ESPERA_FIN_INST"

            else :
                print "Error de sintaxis en la linea %d" % nro_linea 
                sys.exit()

 
        else :
            print "Error de sintaxis en la linea %d" % nro_linea 
            sys.exit()

        continue

    elif estado == "ESPERA_2_ARG_REG" :
        if tipo == "reg" :
            op = op + "_ra"
            arg2 = int(token[1:])
            program_asm.append((op, arg1, arg2)) 
            estado = "ESPERA_FIN_INST"

        else :
            print "Error de sintaxis en la linea %d" % nro_linea 
            sys.exit()

        continue           

    elif estado == "ESPERA_FIN_INST" :
        if tipo == "comen" :
            pass   # ingora los comentarios        
        elif tipo == "fin_linea" :
            nro_instr += 1
            nro_linea += 1
            estado = "ESPERA_INI_INST"
        else :
            print "Error de sintaxis en la linea %d" % nro_linea 
            sys.exit()

# Resuelve las direcciones de las etiquetas
program_asm_2 = []

for op, arg1, arg2 in program_asm :
    arg1_aux = arg1
    if op in ("call_pck", "jc_pck", "jmp_pck", "jz_pck") and type(arg1) == str :
        try :
            arg1_aux = etiquetas[arg1]
        except :
            print "Error : etiqueta no definida"  
            sys.exit()           
    program_asm_2.append((op, arg1_aux, arg2))

program_asm = program_asm_2

############### Conversion ###############

from instruction_set import *

### Tabla para la conversion
TABLA = { "add_ra_k"       : lambda arg1, arg2 : (ADD_RA_K << 11) + (arg1 << 8) + arg2,
          "add_ra_rb"      : lambda arg1, arg2 : (ADD_RA_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "and_ra_k"       : lambda arg1, arg2 : (AND_RA_K << 11) + (arg1 << 8) + arg2,
          "and_ra_rb"      : lambda arg1, arg2 : (AND_RA_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "call_pck"       : lambda arg1, arg2 : (CALL_PCK << 11) + arg1,
          "cmp_ra_k"       : lambda arg1, arg2 : (CMP_RA_K << 11) + (arg1 << 8) + (arg2 << 5),
          "cmp_ra_rb"      : lambda arg1, arg2 : (CMP_RA_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "jc_pck"         : lambda arg1, arg2 : (JC_PCK << 11) + arg1,
          "jmp_pck"        : lambda arg1, arg2 : (JMP_PCK << 11) + arg1,
          "jz_pck"         : lambda arg1, arg2 : (JZ_PCK << 11) + arg1,
          "mov_ra_k"       : lambda arg1, arg2 : (MOV_RA_K << 11) + (arg1<<8) + arg2,
          "mov_ra_rb"      : lambda arg1, arg2 : (MOV_RA_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "mov_ra_addr_k"  : lambda arg1, arg2 : (MOV_RA_Addr_K << 11) + (arg1<<8) + arg2,
          "mov_ra_addr_rb" : lambda arg1, arg2 : (MOV_RA_Addr_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "mov_addr_k_ra"  : lambda arg1, arg2 : (MOV_Addr_K_RA << 11) + (arg2<<8) + arg1,
          "mov_addr_rb_ra" : lambda arg1, arg2 : (MOV_Addr_RB_RA << 11) + (arg2 << 8) + (arg1 << 5),
          "nop"            : lambda arg1, arg2 : (NOP << 11),  
          "or_ra_k"        : lambda arg1, arg2 : (OR_RA_K << 11) + (arg1 << 8) + arg2,
          "or_ra_rb"       : lambda arg1, arg2 : (OR_RA_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "ret"            : lambda arg1, arg2 : (RET << 11),  
          "sub_ra_k"       : lambda arg1, arg2 : (SUB_RA_K << 11) + (arg1 << 8) + arg2,
          "sub_ra_rb"      : lambda arg1, arg2 : (SUB_RA_RB << 11) + (arg1 << 8) + (arg2 << 5),
          "shl_ra"         : lambda arg1, arg2 : (SHL_RA << 11) + (arg1 << 8),
          "shr_ra"         : lambda arg1, arg2 : (SHR_RA << 11) + (arg1 << 8) }


program_hex = [ TABLA[inst](arg1, arg2) for inst, arg1, arg2 in program_asm ]  

program_hex = tuple(program_hex)

f = open(sys.argv[1][:-4]+".py", "w")
f.write("program = " + str(program_hex))
f.close()

