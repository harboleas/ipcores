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

    # Info del Horiz
    PIXELS_x_LINEA = 864          # Cantidad de pixels de una linea de video
    PIXELS_x_LINEA_ACTIVA = 720   # Cantidad de pixels activos de una linea de video
    PIXELS_x_SYNC_H = 64          # Cantidad de pixels del pulso de sinc h.
    PIXELS_x_BP = 68              # Cantidad de pixels de back porch
    INICIO_X = PIXELS_x_SYNC_H + PIXELS_x_BP - 6 # Comienzo del pixel activo en la linea (Nota el -6 es por atraso en el tracker analogico)

    # Info del Vert
    TOTAL_LINEAS   = 625     # Total de lineas del PAL
    LINEAS_ACTIVAS = 576     # Cantidad de lineas activas de video

    LINEA_INI_VIDEO_ACTIVO_ODD = 21       # Linea de comienzo del video activo en el campo impar 
    LINEA_FIN_VIDEO_ACTIVO_ODD = 308       # Linea de finalizacion del video activo en el campo impar 

    LINEA_INI_VIDEO_ACTIVO_EVEN = 334     # Linea de comienzo del video activo en el campo par 
    LINEA_FIN_VIDEO_ACTIVO_EVEN = 621     # Linea de finalizacion del video activo en el campo par 


    # Senales y registros
    
    ini_hs = Signal(False)     # Pulso de inicio de sincronismo horizontal
    ini_vs = Signal(False)     # Inicio de sincronismo vertical 
    pix_ce = Signal(False)     # Clock enable para contar pixels  

    barrido_x = Signal(intbv(0, 0, PIXELS_x_LINEA))   # Registros para llevar la posicion del barrido    
    nro_linea = Signal(intbv(0, 0, TOTAL_LINEAS))     # 

    ini_odd = Signal(False)          # Pulso de inicio de campo impar 
    rst_aux = Signal(False)
    rst_n_lineas = Signal(False)     # Reset del contador de lineas

    video_activo_x = Signal(False)
    video_activo_y = Signal(False)


    ######################################################################################################## 
    #
    # Horizontal
    # ==========
    #                   _____________                                   __________________________________
    #    hs                          |_____________________________ ***
    #                     _   _   _   _   _   _   _   _   _   _   _       _   _   _   _   _   _   _   _
    #    clk @ 27MHz    _| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|  *** _| |_| |_| |_| |_| |_| |_| |_| |_|
    #                                 ___         
    #    ini_hs         _____________|   |_________________________ *** __________________________________  
    #                         ___     ___     ___     ___     ___       _     ___     ___     ___     ___
    #    pix_ce          |___|   |___|   |___|   |___|   |___|   |_ ***  |___|   |___|   |___|   |___|   |
    #                                                                        
    #    barrido_x       ]  862  ]  863  ]   0   ]   1   ]   2   ]  ***  ]  131  ]  132  ]  133  ]  134  ]
    #                                                                             ________________________
    #    video_activo_x ___________________________________________ *** _________|
    #
    #    pixel_x                                0                                [   0   ]   1   ]   2   ]
    #           



    gen_ini_hs = detecta_flanco_bajada(clk_i = clk27_i, 
                                       a_i = hs_i, 
                                       flanco_o = ini_hs)     

    gen_pix_ena = FT_R(clk_i = clk27_i, 
                       rst_i = ini_hs, 
                       t_i = Signal(True), 
                       q_o = pix_ce)       # Divide x2 la frec de clock
    
    gen_barrido_x = CB_RE(clk_i = clk27_i, 
                          rst_i = ini_hs, 
                          ce_i = pix_ce, 
                          q_o = barrido_x)     # Cuenta los "pixels" (tanto activos como los de blanking)
                                                    # en una linea de video, comenzando desde el flanco de bajada de hs   
                  
    @always_comb
    def gen_video_activo_x() :    
        if INICIO_X <= barrido_x and barrido_x < INICIO_X + PIXELS_x_LINEA_ACTIVA :    # Comparador para determinar la ventana temporal de la linea activa 
            video_activo_x.next = True
        else :
            video_activo_x.next = False
   

    ########################################################################################################################
    #
    # Vertical
    # ========
    #                ___      _      _      _      _      _   ______   ______   ______   ______   ______   ____________   _
    #   mix_sync        |____| |____| |____| |____| |____| |_|      |_|      |_|      |_|      |_|      |_|            |_|
    #                ___   ___________   ___________   _____________   _______________   _______________   ____________   _
    #   hs_i            |_|           |_|           |_|             |_|               |_|               |_|            |_|
    #                ________                                          ____________________________________________________
    #   vs_i                 |________________________________________|
    #                         _____________________________________________________________________________________________
    #   odd_even_i   ________|
    #
    #   nro_linea       ]     624     ]      0      ]       1       ]        2        ]        3        ]      4       ]
    #



    gen_ini_vs = detecta_flanco_bajada(clk_i = clk27_i, 
                                       a_i = vs_i, 
                                       flanco_o = ini_vs)

    @always_comb
    def gen_ini_odd() :                      # Genera un pulso al comienzo del campo impar para resetear el contador de lineas 
        ini_odd.next = ini_vs & odd_even_i
        
    gen_rst_n_linea = FJK(clk_i = clk27_i, 
                          j_i = ini_odd, 
                          k_i = ini_hs, 
                          q_o = rst_aux)     

    @always_comb
    def gen_rst_vert() :
        rst_n_lineas.next = rst_aux & ini_hs          # un pulsito al comienzo del primer hs dentro del vs del campo impar 

    gen_nro_linea = CB_RE(clk_i = clk27_i, 
                          rst_i = rst_n_lineas, 
                          ce_i = ini_hs, 
                          q_o = nro_linea)   # Cuenta las lineas de video desde el comienzo del campo impar

    @always_comb
    def gen_video_activo_y() :    
        if (LINEA_INI_VIDEO_ACTIVO_EVEN <= nro_linea and nro_linea <= LINEA_FIN_VIDEO_ACTIVO_EVEN) or (LINEA_INI_VIDEO_ACTIVO_ODD <= nro_linea and nro_linea <= LINEA_FIN_VIDEO_ACTIVO_ODD) :  
            video_activo_y.next = True
        else :
            video_activo_y.next = False

    @always_comb
    def gen_video_activo() :
        video_activo_o.next = video_activo_x & video_activo_y    # Parte util de la senal de video

    @always(barrido_x, video_activo_x)
    def gen_pixel_x() :                
        if video_activo_x :
            pixel_x_o.next = barrido_x - INICIO_X  
        else :
            pixel_x_o.next = 0  

    
    @always(nro_linea, video_activo_y, odd_even_i)
    def gen_pixel_y() :
        if video_activo_y :
            if odd_even_i :
                pixel_y_o.next = (nro_linea - LINEA_INI_VIDEO_ACTIVO_ODD) * 2    # el "* 2" es debido al barrido entrelazado y el campo impar tiene la primer linea  
            else :
                pixel_y_o.next = (nro_linea - LINEA_INI_VIDEO_ACTIVO_EVEN) * 2 + 1      
        else :
            pixel_y_o.next = 0

    @always_comb
    def conex_pix_ce_o() :
        pix_ce_o.next = pix_ce

    @always_comb
    def gen_ini_frame() :
        ini_frame_o.next = odd_even_i and ini_vs

    return instances()

    pass

    
# vim: set ts=8 sw=4 tw=0 et :
