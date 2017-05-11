# pal.py
# ======
# 
# IP Cores para el manejo de las senales de un sistema PAL (720x576i) 
# 
# Author : 
#     Hugo Arboleas, <harboleas@citidef.gob.ar>
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


def pal_sync(clk27_i,
             rst_i,
             mix_sync_o,
             odd_even_o,
             vs_o,
             hs_o) :
    """
    IP Core que genera las senales de sincronismo del sistema PAL (720x576i)

    Inputs

    * clk27_i - Entrada de clock de 27Mhz (clock de pixel x2)
    * rst_i   - Reset asincronico

    Outputs

    * mix_sync_o - Sincronismo compuesto
    * odd_even_o - Campo impar/par
    * vs_o       - Sincronismo vertical
    * hs_o       - Sincronismo horizontal

    """

    CLK_FREC = 27  # MHz
    T_LINEA_TOT = 64 * CLK_FREC    
    T_MEDIA_LINEA = 32 * CLK_FREC
    T_VERT_L = int(27.3 * CLK_FREC)
    T_VERT_H = T_MEDIA_LINEA - T_VERT_L
    T_EQU_L = int(2.3 * CLK_FREC)
    T_EQU_H = T_MEDIA_LINEA - T_EQU_L
    T_LINEA_L = int(4.7 * CLK_FREC)
    T_LINEA_H = T_LINEA_TOT - T_LINEA_L
    
    e = enum("VERT_L", "VERT_H", "POS_EQU_L", "POS_EQU_H", "LINEA_L", "LINEA_H", "PRE_EQU_L", "PRE_EQU_H", "VERT_L_2", "VERT_H_2",
             "POS_EQU_L_2", "POS_EQU_H_2", "MEDIA_LINEA_H", "LINEA_L_2", "LINEA_H_2", "MEDIA_LINEA_L_2", "MEDIA_LINEA_H_2",
             "PRE_EQU_L_2", "PRE_EQU_H_2")

    e_hs = enum("LINEA_L", "LINEA_H")

    estado = Signal(e.VERT_L) 
    
    estado_hs = Signal(e_hs.LINEA_L) 

    pulsos = Signal(intbv(0, 0, 310))
    tiempo = Signal(intbv(0, 0, T_LINEA_TOT))       
    tiempo_hs = Signal(intbv(0, 0, T_LINEA_TOT))       
   
    hs_rst = Signal(False)  # Reset para la fsm_hs, permite sincronizar las maquinas

    ########################################################################################################################
    #
    #                ___      _      _      _      _      _   ______   ______   ______   ______   ______   ____________   _
    #   mix_sync        |____| |____| |____| |____| |____| |_|      |_|      |_|      |_|      |_|      |_|            |_|
    #                ________                                          ____________________________________________________
    #   vs                   |________________________________________|
    #                         _____________________________________________________________________________________________
    #   odd_even     ________|
    #                ___   ___________   ___________   _____________   _______________   _______________   ____________   _
    #   hs              |_|           |_|           |_|             |_|               |_|               |_|            |_|
    #                                 
    #   hs_rst       ________________||___________________________________________________________________________________

   
    @always(clk27_i.posedge, rst_i.posedge)
    def fsm_mix_sync() :
        tiempo.next = tiempo + 1
        hs_rst.next = False  
        if rst_i :
            pulsos.next = 0
            tiempo.next = 0
            odd_even_o.next = True
            estado.next = e.VERT_L
            mix_sync_o.next = True
            vs_o.next = True

        else :
            ######## Campo impar ###########
            if estado == e.VERT_L :
                if tiempo == T_VERT_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.VERT_H
                    if pulsos == 0 :
                        vs_o.next = False        
            ################################
            elif estado == e.VERT_H :
                if tiempo == T_VERT_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 4 : # 5 pulsitos verticales
                        pulsos.next = 0
                        estado.next = e.POS_EQU_L
                    else :
                        estado.next = e.VERT_L
                # Genero el sync para la maquina que genera hs 
                if pulsos == 1 :
                    if tiempo == T_VERT_H - 2 :
                        hs_rst.next = True    
            ################################
            elif estado == e.POS_EQU_L :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.POS_EQU_H
                    if pulsos == 1 :
                        vs_o.next = True
            ################################
            elif estado == e.POS_EQU_H :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 4 : # 5 pulsos de post ecualizacion
                        pulsos.next = 0
                        estado.next = e.LINEA_L
                    else :
                        estado.next = e.POS_EQU_L
            ################################
            elif estado == e.LINEA_L :
                if tiempo == T_LINEA_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.LINEA_H
            ################################
            elif estado == e.LINEA_H :
                if tiempo == T_LINEA_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 304 :  # 305 Lineas
                        pulsos.next = 0
                        estado.next = e.PRE_EQU_L
                    else :
                        estado.next = e.LINEA_L
            ################################
            elif estado == e.PRE_EQU_L :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.PRE_EQU_H
            ################################
            elif estado == e.PRE_EQU_H :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 4 : 
                        pulsos.next = 0
                        odd_even_o.next = False
                        estado.next = e.VERT_L_2
                    else :
                        estado.next = e.PRE_EQU_L
            ######### Campo par ############
            elif estado == e.VERT_L_2 :
                if tiempo == T_VERT_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.VERT_H_2
                    if pulsos == 0 :
                        vs_o.next = False
            ################################
            elif estado == e.VERT_H_2 :
                if tiempo == T_VERT_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 4 :
                        pulsos.next = 0
                        estado.next = e.POS_EQU_L_2
                    else :
                        estado.next = e.VERT_L_2
            ################################
            elif estado == e.POS_EQU_L_2 :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.POS_EQU_H_2
                    if pulsos == 1 :
                        vs_o.next = True
            ################################
            elif estado == e.POS_EQU_H_2 :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    if pulsos == 4 :
                        pulsos.next = 0
                        estado.next = e.MEDIA_LINEA_H
                    else :
                        mix_sync_o.next = False
                        estado.next = e.POS_EQU_L_2
            ################################
            elif estado == e.MEDIA_LINEA_H :
                if tiempo == T_MEDIA_LINEA - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = False
                    estado.next = e.LINEA_L_2
            ################################
            elif estado == e.LINEA_L_2 :
                if tiempo == T_LINEA_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.LINEA_H_2
            ################################
            elif estado == e.LINEA_H_2 :
                if tiempo == T_LINEA_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 303 :
                        pulsos.next = 0
                        estado.next = e.MEDIA_LINEA_L_2
                    else :
                        estado.next = e.LINEA_L_2
            ################################
            elif estado == e.MEDIA_LINEA_L_2 :
                if tiempo == T_LINEA_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.MEDIA_LINEA_H_2
            ################################
            elif estado == e.MEDIA_LINEA_H_2 :
                if tiempo == (T_MEDIA_LINEA - T_LINEA_L) - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = False
                    estado.next = e.PRE_EQU_L_2
            ################################
            elif estado == e.PRE_EQU_L_2 :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = True
                    estado.next = e.PRE_EQU_H_2
            ################################
            elif estado == e.PRE_EQU_H_2 :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = False
                    if pulsos == 4 :
                        pulsos.next = 0
                        odd_even_o.next = True
                        estado.next = e.VERT_L
                    else :
                        estado.next = e.PRE_EQU_L_2
            else :
                estado.next = e.VERT_L

    @always(clk27_i.posedge)
    def fsm_hs() :

        tiempo_hs.next = tiempo_hs + 1
        
        if hs_rst :
            tiempo_hs.next = 0
            estado_hs.next = e_hs.LINEA_L 
            hs_o.next = False

        else :
            if estado_hs == e_hs.LINEA_L :
                if tiempo_hs == T_LINEA_L - 1 :
                    tiempo_hs.next = 0
                    estado_hs.next = e_hs.LINEA_H
                    hs_o.next = True
            elif estado_hs == e_hs.LINEA_H :
                if tiempo_hs == T_LINEA_H - 1 :
                    tiempo_hs.next = 0
                    estado_hs.next = e_hs.LINEA_L
                    hs_o.next = False
           

    return instances() 


##################################################

def pal_coord(clk27_i,
              hs_i,
              vs_i,
              odd_even_i,
              pix_ce_o,
              act_vid_o,
              ini_frame_o,
              x_o,
              y_o) :
    """
    Core para generar las coordenadas (x,y) del active current pixel de un sistema PAL (720x576i).  
    

             x
         *--->
         |  -------------------------
       y v |(0,0)                    |
           |                         |
           |                         |
           |       Zona activa       | 
           |        de video         | 
           |                         | 
           |                         |
           |                (719,575)|
            -------------------------

    Inputs

    * clk27_i    - entrada de clock de pixel x2 ( 27Mhz )
    * vs_i       - entrada de sincronismo vertical
    * hs_i       - entrada de sincronismo horizontal
    * odd_even_i - entrada de campo odd/even
    
    Outputs
    
    * pix_ce_o    - salida de pixel clock enable  
    * act_vid_o   - salida que determina la ventana temporal del video activo  
    * ini_frame_o - inicio del frame  
    * x_o         - salida de la coordenada x del pixel activo actual [0 .. 720] 
    * y_o         - salida de la coordenada y del pixel activo actual [0 .. 576]

    """


    pass

    
# vim: set ts=8 sw=4 tw=0 et :
