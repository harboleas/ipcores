# udiv.py
# =======
# 
# Unsigned Divider 
# 
# Author: 
#     Hugo Arboleas, <harboleas@citedef.gob.ar>
# 
##############################################################################
# 
# Copyright 2015 Hugo Arboleas
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from myhdl import *

def udiv(clk_i,
         rst_i,
         a_i,
         b_i,
         start_i,
         q_o,
         r_o,
         done_o,
         div0_o) :

    """ 
    Unsigned Divider
    ================

    Divisor secuencial de enteros sin signo de n bits
    
    Inputs 
    
    *   clk_i   - Clock 
    *   rst_i   - Reset 
    *   a_i     - Dividendo de n bits
    *   b_i     - Divisor de m bits
    *   start_i - Comienza la operacion
    
    Outputs
           
    *   q_o    - Cociente de n bits
    *   r_o    - Resto de n bits
    *   done_o - Fin de la operacion (1 clk)
    *   div0_o - Error de division por 0 
    

    Nota : La operacion se efectua en n + 1 ciclos de clock.
           Donde n es la cantidad de bits del cociente.
    """

    # Estados de la FSM
    t_state = enum("ESPERA_START", "DIVIDE") 
    state = Signal(t_state.ESPERA_START)

    n_bits = len(a_i)    
    m_bits = len(b_i)
   
    q_par = Signal(intbv(0)[n_bits:])    # cociente parcial 
    r_par = Signal(intbv(0)[n_bits+1:])  # resto parcial (un bit mas para la ultima iteracion) 
    a_par = Signal(intbv(0)[n_bits:])    # dividendo parcial 

    b = Signal(intbv(0)[m_bits:])  # divisor registrado

    i = Signal(intbv(0, 0, n_bits + 1)) # contador de las iteraciones del algoritmo de division 

    r_aux = intbv(0)[n_bits:] # resto auxiliar   

    @always(clk_i.posedge, rst_i.posedge)
    def fsm() :

        if rst_i :   
            q_o.next = 0
            r_o.next = 0
            done_o.next = False
            div0_o.next = False
            state.next = t_state.ESPERA_START

        else : # rising clk

            ############################## 
            if state == t_state.ESPERA_START :
                div0_o.next = False
                done_o.next = False
                    
                if start_i :        
                    if b_i == 0 :     
                        # Error division por 0 
                        div0_o.next = True
                        done_o.next = True
                    else :                  
                        i.next = 0
                        b.next = b_i
                        a_par.next = concat(a_i[n_bits-1:], False)  
                        r_aux[:] = 0
                        r_par.next = concat(r_aux, a_i[n_bits-1])
                        q_par.next = 0
                        state.next = t_state.DIVIDE  

            ##############################    
            elif state == t_state.DIVIDE :

                if i < n_bits : 
                    # Calcula el i-esimo bit del cociente (contando desde el mas significativo)
                    if r_par[n_bits:] >= b :
                        q_par.next = concat(q_par[n_bits-1:], True)   
                        r_aux[:] = r_par[n_bits:] - b
                    else :
                        q_par.next = concat(q_par[n_bits-1:], False) 
                        r_aux[:] = r_par[n_bits:]

                    # Calcula el resto parcial para la siguiente iteracion
                    r_par.next = concat(r_aux, a_par[n_bits-1]) 
                    a_par.next = concat(a_par[n_bits-1:], False)  
                    
                    i.next = i + 1  # siguiente iteracion
                
                else :
                    done_o.next = True
                    q_o.next = q_par
                    # El resto quedo desplazado  
                    r_o.next = r_par[n_bits+1 : 1]
                    state.next = t_state.ESPERA_START
            

    return instances()

# vim: set ts=8 sw=4 tw=0 et :
