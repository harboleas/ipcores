# uart.py
# ========
# 
# IP core para la transmision y recepcion de datos serie
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

def uart_tx(clk_i,
            rst_i,
            par_i,
            data_i,
            start_i,
            tx_o,
            done_o,
            CLK_FREQ = 50e6,
            BAUDRATE = 115200) :

    """
    uart_tx
    -------
    
    Modulo Tx 
    8 bits de datos, 1 bit de stop y bit de paridad.
    
    Inputs
    
    *   clk_i   - Clock 
    *   rst_i   - Reset 
    *   par_i   - Parity select (0:None, 1:Odd,  2,3:Even) 
    *   data_i  - TX data
    *   start_i - Start Tx
    
    Outputs
    
    *   tx_o   - Tx out
    *   done_o - Tx done (1 clk)
    
    Parametros
    
    *   CLK_FREQ 
    *   BAUDRATE 
    
   """

    TICKS_BIT = int(CLK_FREQ / BAUDRATE)   # Clocks por bit

    e = enum("ESPERA_START", "TX")  # los estados de la FSM

    estado = Signal(e.ESPERA_START)       

    ticks = Signal(intbv(0, 0, TICKS_BIT))   # Contador para el generador de baudrate 
    
    data_pack = Signal(intbv(0)[11:])        # Paquete de datos : start, data, stop y paridad

    num_bits_enviados = Signal(intbv(0, 0, 11))  # Contador de bits enviados  

    len_data_pack = Signal(intbv(0, 0, 11))  # Tamano del paquete de datos a enviar (segun paridad) 
    
    idle = Signal(True)

    @always(clk_i.posedge, rst_i.posedge)
    def fsm() :
        if rst_i :
            estado.next = e.ESPERA_START
            num_bits_enviados.next = 0
            ticks.next = 0
            data_pack.next = 0
            done_o.next = False
            idle.next = True

        else :  # rising clk 

            #############################            
            if estado == e.ESPERA_START :
                idle.next = True
                done_o.next = False
                if start_i :
                    estado.next = e.TX
                    num_bits_enviados.next = 0
                    ticks.next = 0
                    idle.next = False
                
                    # Armo el paquete, segun la paridad seleccionada 
                    len_data_pack.next = 10 
                    if par_i == 0 : # None
                        len_data_pack.next = 9
                        data_pack.next = concat(True, True, data_i, False)
                    elif par_i == 1 : # Odd
                        par_odd = not (data_i[0] ^ data_i[1] ^ data_i[2] ^ data_i[3] ^ data_i[4] ^ data_i[5] ^ data_i[6] ^ data_i[7]) 
                        data_pack.next = concat(True, par_odd, data_i, False)
                    else : # Even
                        par_even = bool(data_i[0] ^ data_i[1] ^ data_i[2] ^ data_i[3] ^ data_i[4] ^ data_i[5] ^ data_i[6] ^ data_i[7])  
                        data_pack.next = concat(True, par_even, data_i, False)
            
            #############################            
            elif estado == e.TX :
                if ticks == TICKS_BIT - 1:
                    ticks.next = 0
                    data_pack.next = concat(False, data_pack[11:1])   # Shifteo a la derecha para enviar el siguiente bit 
                    if num_bits_enviados == len_data_pack :                          
                        estado.next = e.ESPERA_START
                        idle.next = True
                        done_o.next = True
                    else :
                        num_bits_enviados.next = num_bits_enviados + 1
                else :
                    ticks.next = ticks + 1

    @always_comb
    def tx_out() :
        tx_o.next = data_pack[0] or idle

    return instances()

####################################################################################

def uart_rx(clk_i,
            rst_i,
            par_i,
            rx_i,
            ready_o,
            data_o,
            frame_err_o,
            par_err_o,
            CLK_FREQ = 50e6,
            BAUDRATE = 115200) :

    """
    uart_rx
    -------
    
    Modulo Rx 
    8 bits de datos, 1 bit de stop y bit de paridad.
    
    Inputs
    
    *   clk_i - Clock
    *   rst_i - Reset 
    *   par_i - Parity select (0:None, 1:Odd,  2,3:Even) 
    *   rx_i  - Rx in
    
    Outputs
    
    *   ready_o     - Data ready (1 clk)
    *   data_o      - Read data 
    *   frame_err_o - Frame error
    *   par_err_o   - Parity error 
    
    Parametros
    
    *   CLK_FREQ 
    *   BAUDRATE

   """

    TICKS_BIT = int(CLK_FREQ / BAUDRATE)
    TICKS_HALF_BIT = TICKS_BIT / 2 

    e = enum("ESPERA_START_BIT", "VERIF_START", "RX", "FIN")

    estado = Signal(e.ESPERA_START_BIT)

    ticks = Signal(intbv(0, 0, TICKS_BIT))   # Contador para el generador de baudrate 
    
    data_pack = Signal(intbv(0)[11:])        # Paquete de datos : start, data, stop y paridad

    num_bits_recib = Signal(intbv(0, 0, 11))  # Contador de bits recibidos  

    len_data_pack = Signal(intbv(0, 0, 11))  # Tamano del paquete de datos a leer (segun paridad) 
    
    par_q = Signal(intbv(0)[2:])  # Registro para guardar el tipo de paridad

    @always(clk_i.posedge, rst_i.posedge)
    def fsm() :

        if rst_i :
            estado.next = e.ESPERA_START_BIT
            num_bits_recib.next = 0
            ticks.next = 0
            data_pack.next = 0
            ready_o.next = False
            par_err_o.next = False
            frame_err_o.next = False
            par_q.next = 0
        
        else : # rising clk

            ################################
            if estado == e.ESPERA_START_BIT :
                ready_o.next = False
                if rx_i == False :

                    par_q.next = par_i   # Registra paridad

                    if par_i == 0 : # None 
                        len_data_pack.next = 9
                    else :
                        len_data_pack.next = 10

                    par_err_o.next = False
                    frame_err_o.next = False
 
                    estado.next = e.VERIF_START
                    ticks.next = 0
                    num_bits_recib.next = 0

            ################################
            elif estado == e.VERIF_START :
                if ticks == TICKS_HALF_BIT - 1 :  # Muestreo en la mitad del bit
                    ticks.next = 0
                    if rx_i == False :  # Verifico que sea el bit de start
                        data_pack.next = concat(rx_i, data_pack[11:1])   
                        num_bits_recib.next = num_bits_recib + 1
                        estado.next = e.RX 
                    else :  
                        # Frame error
                        estado.next = e.ESPERA_START_BIT
                        frame_err_o.next = True    
                else :
                    ticks.next = ticks + 1

            ################################
            elif estado == e.RX :
                if ticks == TICKS_BIT - 1 :
                    ticks.next = 0
                    data_pack.next = concat(rx_i, data_pack[11:1])    # Muestreo y shifteo a la derecha para armar el paquete
                    if num_bits_recib == len_data_pack :
                        if rx_i :  # Verifico el bit de stop
                            estado.next = e.FIN        
                        else :
                            frame_err_o.next = True
                            estado.next = e.ESPERA_START_BIT
                    else :
                        num_bits_recib.next = num_bits_recib + 1
                else :
                    ticks.next = ticks + 1

            ################################
            elif estado == e.FIN :
                
                data_o.next = data_pack[9:1]
               
                par_odd = not (data_pack[1] ^ data_pack[2] ^ data_pack[3] ^ data_pack[4] ^  
                           data_pack[5] ^ data_pack[6] ^ data_pack[7] ^ data_pack[8])  

                par_even = bool(data_pack[1] ^ data_pack[2] ^ data_pack[3] ^ data_pack[4] ^  
                                data_pack[5] ^ data_pack[6] ^ data_pack[7] ^ data_pack[8] ) 

                par_bit = data_pack[9]

                if par_q == 0 : # None
                    ready_o.next = True
                elif par_q == 1 : # Odd
                    if par_bit == par_odd :
                        ready_o.next = True
                    else :
                        par_err_o.next = True
                else : # Even
                    if par_bit == par_even :
                        ready_o.next = True
                    else :
                        par_err_o.next = True
 
                estado.next = e.ESPERA_START_BIT
                 
    return instances()

# vim: set ts=8 sw=4 tw=0 et :
