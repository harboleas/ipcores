"""
Modulos de Video
================

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from Contadores import CB_R, CB_RE
from FlipFlops import FT_R, FJK, FD, FT_S, FD_E
from Deteccion_flancos import detecta_flanco_bajada
from rom_font import ROM_FONT


Hi = True     # Niveles logicos
Lo = False


#######################################################################################################################

def ITU_656_deco(clk27_i, 
                 data_i, 
                 pixel_x_o, 
                 pixel_y_o,
                 pix_ena_o,
                 video_activo_o,
                 Y_o,
                 Cb_o,
                 Cr_o,
                 ini_frame_o) :
    """Decodifica la norma ITU-656 (PAL), obteniendo las coordenadas del pixel actual y su valor de YCbCr

    :Parametros:
        - `clk27_i`        -- entrada de clock de 27Mhz 
        - `data_i`         -- entrada de datos en norma itu 656 (PAL)
        - `pix_ena_o`      -- salida de pixel enable  
        - `pixel_x_o`      -- salida de la coordenada x del pixel activo actual [0 .. 720] 
        - `pixel_y_o`      -- salida de la coordenada y del pixel activo actual [0 .. 576]
        - `video_activo_o` -- salida que determina la ventana temporal del video activo  
        - `Y_o`            -- valor de luma del pixel actual (unsigned)     
        - `Cb_o`           -- valor de croma del pixel actual (signed)    
        - `Cr_o`           -- valor de croma del pixel actual (signed)    
        - `ini_frame_o`    -- salida de inicio del cuadro (inicio del campo impar)

    """   

    # Info del Horiz
    PIXELS_x_LINEA = 864          # Cantidad de pixels de una linea de video PAL
    PIXELS_x_LINEA_ACTIVA = 720   # Cantidad de pixels activos de una linea de video

    # Info del Vert
    TOTAL_LINEAS   = 625     # Total de lineas del PAL
    LINEAS_ACTIVAS = 576     # Cantidad de lineas activas de video PAL

    LINEA_INI_VIDEO_ACTIVO_ODD = 22       # Linea de comienzo del video activo en el campo impar 
    LINEA_FIN_VIDEO_ACTIVO_ODD = 309       # Linea de finalizacion del video activo en el campo impar 

    LINEA_INI_VIDEO_ACTIVO_EVEN = 335     # Linea de comienzo del video activo en el campo par 
    LINEA_FIN_VIDEO_ACTIVO_EVEN = 622     # Linea de finalizacion del video activo en el campo par 

    n = len(data_i)

    #################################    
    ### Senales y registros

    data_q1 = Signal(intbv(0)[n:])   # Registros para la ventana de deteccion de los codigos de sincronismo
    data_q2 = Signal(intbv(0)[n:])
    data_q3 = Signal(intbv(0)[n:])
    sav = Signal(Lo)                 # Deteccion del start active video SAV
    sav_q1 = Signal(Lo)               
    sav_q2 = Signal(Lo)    
    eav = Signal(Lo)      # Deteccion del end active video 
    n_f = Signal(Lo)      # Bit de Frame
    v = Signal(Lo)        # Bit de Vertical   


    Y = Signal(intbv(0)[n:])
    Cb = Signal(intbv(0)[n:])
    Cb_q = Signal(intbv(0)[n:])

    ena_Y = Signal(Lo)       # Para muestrear la informacion de luma
    ena_x = Signal(Lo)       # Para contar la coordenada x 
    ena_Y_2 = Signal(Lo)     # Aux para generar ena_Cb
    ena_Cb = Signal(Lo)      # Para muestrear la informacion de croma blue
    ena_Cb_q = Signal(Lo)    # Aux para generar ena_Cr
    ena_Cr = Signal(Lo)      # Para muestrear la informacion de croma red

    pos_x = Signal(intbv(0, 0, PIXELS_x_LINEA))
    nro_linea = Signal(intbv(0, 0, TOTAL_LINEAS)) 

    rst_x = Signal(Lo)  # Reset del contador horizontal
    rst_y = Signal(Lo)  # Reset del contador de lineas

    odd_even = Signal(Lo)  # 1 Impar (Trama 1), 0 Par (Trama 2)

    video_activo_x = Signal(Lo)
    video_activo_y = Signal(Lo)

    ena_aux = Signal(Lo)
    ini_frame = Signal(Lo)
    ena_ini_frame = Signal(Lo)
    rst_ini_frame = Signal(Lo)
    cuenta_ini_frame = Signal(intbv(0, 0, 15 + 1))

    
    #################################
    ### Datapath

    #########################################################################################
    ### Descripcion del codigo SAV de referencia para la temporizacion de la senal de video
    #            
    #                   ____      ____      ____      ____      ____      ____      ____
    #   clk27_i    ____|    |____|    |____|    |____|    |____|    |____|    |____|    | 
    #
    #   data_i              |   FF    |   00    |    00   |    XY   |   Cb    |   Y0    |
    #
    #              H Blank  |                  SAV                  |    Video activo     
    #
    #
    #    Descripcion de los bits del byte XY del SAV :
    #    -------------------------------------------
    #
    #       XY[6] = F : 0 durante la trama (campo ) 1
    #                   1 durante la trama 2
    #
    #       XY[5] = V : 0 fuera de la supresion vertical
    #                   1 durante la supresion vertical
    #
    #       XY[4] = H : 0 en SAV  (Start Active Video)
    #                   1 en EAV  (End Active Video)
    #



    # Ventana de 4 bytes para la deteccion del codigo de ref. para la temp    
    reg_1 = FD(clk_i = clk27_i,
               d_i = data_i, 
               q_o = data_q1)

    reg_2 = FD(clk_i = clk27_i,
               d_i = data_q1, 
               q_o = data_q2)

    reg_3 = FD(clk_i = clk27_i,
               d_i = data_q2,
               q_o = data_q3)

    @always_comb
    def detec_cod_ref() :
        if data_q3 == 0xFF and data_q2 == 0 and data_q1 == 0 :
            sav.next = not data_i[4]
            eav.next = data_i[4]
            n_f.next = not data_i[6]
            v.next = not data_i[5]
        else :
            v.next = Lo
            n_f.next = Lo
            sav.next = Lo
            eav.next = Lo

    ########################################################################################################## 
    #
    #
    #   data_i     |    XY   |   Cb0   |   Y0    |   Cr    |    Y1   |    Cb1  |   Y2    |   Cr1   |   Y3    |
    #
    #             _      ____      ____      ____      ____      ____      ____      ____      ____      ____
    #   clk27_i    |____|    |____|    |____|    |____|    |____|    |____|    |____|    |____|    |____|    | 
    #
    #               ____
    #   sav       _|    |____________________________________________________________________________________
    #
    #                              _________           _________            ________           ________
    #   ena_Y     * * * |_________|         |_________|         |__________|        |_________|        |_____
    #
    #                    
    #   Y                * * * * * *        |        Y0         |       Y1          |       Y2         |   Y3
    #
    #                    _________                               __________                             _____
    #   ena_Cb    ______|         |_____________________________|          |___________________________|
    #
    #
    #   Cb           * * *        |                Cb0                     |                Cb1
    #
    #                                        _________                               _________
    #   ena_Cr    __________________________|         |_____________________________|         |______________
    #
    #
    #   Cr                               * * *        |               Cr0                     |          Cr1
    #
    #
    #   Nota : La frecuencia de ena_Y es la mitad de clk27_i y la frec de ena_Cx es la mitad de ena_Y
    #

 
    gen_ena_Y = FT_R(clk_i = clk27_i,
                     rst_i = sav,
                     t_i = Signal(Hi), 
                     q_o = ena_Y)  # Divide por 2 la frec de clk comenzando en bajo luego de sav    

    reg_Y = FD_E(clk_i = clk27_i, 
                 ce_i = ena_Y,
                 d_i = data_i,
                 q_o = Y)          # Registro la luma
     
    gen_ena_Y_2 = FT_S(clk_i = clk27_i, 
                       set_i = sav,
                       t_i = ena_Y,
                       q_o = ena_Y_2)   # Divide por 2 la frec de ena_Y comenzando en alto luego de sav
    
    @always_comb
    def gen_ena_Cb() :
        ena_Cb.next = ena_Y_2 and (not ena_Y)          # Arma ena_Cb 
    
    reg_Cb = FD_E(clk_i = clk27_i,
                  ce_i = ena_Cb, 
                  d_i = data_i,
                  q_o = Cb)         # Registro la croma


    gen_ena_Cb_q = FD(clk_i = clk27_i,
                      d_i = ena_Cb, 
                      q_o = ena_Cb_q)  
 
    gen_ena_Cr = FD(clk_i = clk27_i, 
                    d_i = ena_Cb_q, 
                    q_o = ena_Cr)         # Demora la senal ena_Cb 2 clocks para generar ena_Cr

    reg_Cr = FD_E(clk_i = clk27_i, 
                  ce_i = ena_Cr, 
                  d_i = data_i,
                  q_o = Cr_o)       # Registro la croma

    
    # Ahora para acomodar temporalmente Y, Cb, Cr aplico el delay necesario a cada una
    # Cr : sin delay
    # Y  : 1 clk de delay
    # Cb : 2 clk de delay

    out_Y = FD(clk_i = clk27_i, 
               d_i = Y, 
               q_o = Y_o)
    
    q_Cb = FD(clk_i = clk27_i, 
              d_i = Cb, 
              q_o = Cb_q)

    out_Cb = FD(clk_i = clk27_i, 
                d_i = Cb_q, 
                q_o = Cb_o)

    
    #######################################################################
    ### Generacion de las coordenadas del pixel actual
    #
    #             _      ____      ____      ____      ____      ____      ____      ____      ____      ____
    #   clk27_i    |____|    |____|    |____|    |____|    |____|    |____|    |____|    |____|    |____|    | 
    #
    #               ____
    #   sav       _|    |____________________________________________________________________________________
    #
    #                              _________           _________            ________           ________
    #   ena_Y     * * * |_________|         |_________|         |__________|        |_________|        |_____
    #
    #                    
    #   Y                * * * * * *        |        Y0         |       Y1          |       Y2         |   Y3
    #
    #                                        _________           _________            ________           ____
    #   ena_x                     |_________|         |_________|         |__________|        |_________|    
    #
    #
    #   Y_o                             * * *         |        Y0         |       Y1          |       Y2        
    #
    #                                        _________
    #   rst_x       ________________________|         |______________________________________________________
    #
    #   pixel_x        862        |       863         |         0         |        1          |        2  


    gen_sav_q1 = FD(clk_i = clk27_i, 
                    d_i = sav,
                    q_o = sav_q1)

    gen_sav_q2 = FD(clk_i = clk27_i,
                    d_i = sav_q1,
                    q_o = sav_q2)

    gen_rst_x = FD(clk_i = clk27_i, 
                   d_i = sav_q2, 
                   q_o = rst_x)

    gen_ena_x = FD(clk_i = clk27_i, 
                   d_i = ena_Y, 
                   q_o = ena_x)
   
    gen_pos_x = CB_RE(clk_i = clk27_i, 
                      rst_i = rst_x, 
                      ce_i = ena_x, 
                      q_o = pos_x)    # Contador para la coordenada X

    ####################################################################################    
    #            
    #   data_i             |   FF    |   00    |    00   |    XY   |   Cb    |   Y0    |
    #
    #                      |                  EAV                  |    H Blank     
    #                  ____      ____      ____      ____      ____      ____      ____
    #   clk27_i    ___|    |____|    |____|    |____|    |____|    |____|    |____|    | 
    #                                                          _________________________
    #   odd_even   ___________________________________________| 
    #                                                     ____        
    #   eav        ______________________________________|    |_________________________                                             
    #                                                     ____
    #   n_f        ______________________________________|    |_________________________                           
    #                                                     ____ 
    #   rst_y      ______________________________________|    |_________________________                                                                             


    gen_odd_even = FD_E(clk_i = clk27_i, 
                        ce_i = eav, 
                        d_i = n_f, 
                        q_o = odd_even)

    @always_comb
    def gen_rst_y() :
        rst_y.next = not odd_even and eav and n_f

    gen_nro_linea = CB_RE(clk_i = clk27_i, 
                          rst_i = rst_y, 
                          ce_i = eav, 
                          q_o = nro_linea)

    gen_video_activo_y = FD_E(clk_i = clk27_i, 
                              ce_i = eav, 
                              d_i = v, 
                              q_o = video_activo_y)

    @always(pos_x)
    def gen_video_activo_x() :
        if pos_x < PIXELS_x_LINEA_ACTIVA :
            video_activo_x.next = Hi
        else :
            video_activo_x.next = Lo

    @always(pos_x, video_activo_x)
    def gen_pixel_x() :  
        if video_activo_x :
            pixel_x_o.next = pos_x
        else :
            pixel_x_o.next = 0

    @always(clk27_i.posedge)
    def gen_pixel_y() :   
        if video_activo_y :
            if odd_even :
                pixel_y_o.next = (nro_linea - LINEA_INI_VIDEO_ACTIVO_ODD) * 2  # el "* 2" es debido al barrido entrelazado y el campo impar tiene la primer linea 
            else :
                pixel_y_o.next = (nro_linea - LINEA_INI_VIDEO_ACTIVO_EVEN) * 2 + 1  # el + 1 es porque el campo par tiene la segunda linea         
        else :
            pixel_y_o.next = 0


    @always_comb
    def gen_pix_ena() :
        pix_ena_o.next = ena_x

    @always_comb
    def gen_video_activo() :
        video_activo_o.next = video_activo_x and video_activo_y

    ######################################################################################
    ### Generacion de ini_frame 
 
    gen_ena_aux = FJK(clk_i = clk27_i, 
                      j_i = rst_y,
                      k_i = ini_frame,
                      q_o = ena_aux)

    @always_comb
    def gen_ena_ini_frame() :
        ena_ini_frame.next = ena_x and ena_aux 

    @always_comb
    def gen_rst_ini_frame() :
        rst_ini_frame.next = rst_y or ini_frame

    cont_ini_frame = CB_RE(clk_i = clk27_i,
                           rst_i = rst_ini_frame,
                           ce_i = ena_ini_frame,
                           q_o = cuenta_ini_frame) 

    @always(cuenta_ini_frame)
    def gen_ini_frame() :
        if cuenta_ini_frame == 15 :       # pixels despues del ultimo activo cae el sincronismo 
            ini_frame.next = Hi
        else :
            ini_frame.next = Lo


    @always_comb
    def conex_ini_frame() :
        ini_frame_o.next = ini_frame
    

    return instances()     

#######################################################################################################################

def genera_mix_sync_PAL(clk27_i, 
                        rst_i,
                        ini_field_o,
                        odd_even_o,
                        mix_sync_o) :
    """Genera la senal de sincronismo compuesto"""

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

    estado = Signal(e.VERT_L) 

    pulsos = Signal(intbv(0, 0, 310))
    tiempo = Signal(intbv(0,0, T_LINEA_TOT))       
    
    @always(clk27_i.posedge)
    def FSM() :
        tiempo.next = tiempo + 1
        ini_field_o.next = Lo
        if rst_i :
            pulsos.next = 0
            tiempo.next = 0
            ini_field_o.next = Hi
            odd_even_o.next = Hi
            estado.next = e.VERT_L
            mix_sync_o.next = Lo
        else :
            ######## Campo impar ###########
            if estado == e.VERT_L :
                if tiempo == T_VERT_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.VERT_H
            ################################
            elif estado == e.VERT_H :
                if tiempo == T_VERT_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 4 : # 4 pulsitos verticales
                        pulsos.next = 0
                        estado.next = e.POS_EQU_L
                    else :
                        estado.next = e.VERT_L
            ################################
            elif estado == e.POS_EQU_L :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.POS_EQU_H
            ################################
            elif estado == e.POS_EQU_H :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 4 : # 4 pulsos de post ecualizacion
                        pulsos.next = 0
                        estado.next = e.LINEA_L
                    else :
                        estado.next = e.POS_EQU_L
            ################################
            elif estado == e.LINEA_L :
                if tiempo == T_LINEA_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.LINEA_H
            ################################
            elif estado == e.LINEA_H :
                if tiempo == T_LINEA_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 304 :  # 304 Lineas
                        pulsos.next = 0
                        estado.next = e.PRE_EQU_L
                    else :
                        estado.next = e.LINEA_L
            ################################
            elif estado == e.PRE_EQU_L :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.PRE_EQU_H
            ################################
            elif estado == e.PRE_EQU_H :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 4 : 
                        pulsos.next = 0
                        ini_field_o.next = Hi
                        odd_even_o.next = Lo
                        estado.next = e.VERT_L_2
                    else :
                        estado.next = e.PRE_EQU_L
            ######### Campo par ############
            elif estado == e.VERT_L_2 :
                if tiempo == T_VERT_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.VERT_H_2
            ################################
            elif estado == e.VERT_H_2 :
                if tiempo == T_VERT_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 4 :
                        pulsos.next = 0
                        estado.next = e.POS_EQU_L_2
                    else :
                        estado.next = e.VERT_L_2
            ################################
            elif estado == e.POS_EQU_L_2 :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.POS_EQU_H_2
            ################################
            elif estado == e.POS_EQU_H_2 :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    if pulsos == 4 :
                        pulsos.next = 0
                        estado.next = e.MEDIA_LINEA_H
                    else :
                        mix_sync_o.next = Lo
                        estado.next = e.POS_EQU_L_2
            ################################
            elif estado == e.MEDIA_LINEA_H :
                if tiempo == T_MEDIA_LINEA - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Lo
                    estado.next = e.LINEA_L_2
            ################################
            elif estado == e.LINEA_L_2 :
                if tiempo == T_LINEA_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.LINEA_H_2
            ################################
            elif estado == e.LINEA_H_2 :
                if tiempo == T_LINEA_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 303 :
                        pulsos.next = 0
                        estado.next = e.MEDIA_LINEA_L_2
                    else :
                        estado.next = e.LINEA_L_2
            ################################
            elif estado == e.MEDIA_LINEA_L_2 :
                if tiempo == T_LINEA_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.MEDIA_LINEA_H_2
            ################################
            elif estado == e.MEDIA_LINEA_H_2 :
                if tiempo == (T_MEDIA_LINEA - T_LINEA_L) - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Lo
                    estado.next = e.PRE_EQU_L_2
            ################################
            elif estado == e.PRE_EQU_L_2 :
                if tiempo == T_EQU_L - 1 :
                    tiempo.next = 0
                    mix_sync_o.next = Hi
                    estado.next = e.PRE_EQU_H_2
            ################################
            elif estado == e.PRE_EQU_H_2 :
                if tiempo == T_EQU_H - 1 :                          
                    tiempo.next = 0
                    pulsos.next = pulsos + 1
                    mix_sync_o.next = Lo
                    if pulsos == 4 :
                        pulsos.next = 0
                        ini_field_o.next = Hi
                        odd_even_o.next = Hi
                        estado.next = e.VERT_L
                    else :
                        estado.next = e.PRE_EQU_L_2
            else :
                estado.next = e.VERT_L

    return instances() 

#######################################################################################################################

def VGA_control(clk50_i,
                hs_o,
                vs_o,
                video_activo_o, 
                pix_address_o, 
                RGB_data_i, 
                red_o, 
                green_o, 
                blue_o) :
    """Modulo que genera las senales de sincronismo de un sistema VGA (800x600 @ 72Hz) 

    :Parametros:
        - `clk50_i`        -- Entrada de clock de pixel @ 50Mhz
        - `hs_o`           -- Sincronismo horizontal
        - `vs_o`           -- Sincronismo vertical
        - `video_activo_o` -- Salida que determina la ventana temporal del video activo (nBlank)  
        - `pix_address_o`  -- Direccion del proximo pixel a leer 
        - `RGB_data_i`     -- Valor del pixel leido desde la memoria
        - `red_o`          -- Salida de rojo
        - `green_o`        -- Salida de verde
        - `blue_o`         -- Salida de azul
    """
 
    ######################################
    # Parametros del Horizontal (en pixels)
    H_FRONT = 56
    H_SYNC = 120
    H_BACK = 64
    H_ACT =	800
    H_BLANK = H_FRONT + H_SYNC + H_BACK
    H_TOTAL = H_FRONT + H_SYNC + H_BACK + H_ACT
    ######################################    
    # Parametros del Vertical (en lineas)
    V_FRONT = 37
    V_SYNC = 6
    V_BACK = 23
    V_ACT = 600
    V_BLANK	= V_FRONT + V_SYNC + V_BACK
    V_TOTAL	= V_FRONT + V_SYNC + V_BACK + V_ACT
    
    ###################
    # Senales y registros

    h_cont = Signal(intbv(0, 0, H_TOTAL))     # registros para llevar la pos. del barrido 
    v_cont = Signal(intbv(0, 0, V_TOTAL))
    
    rst_h = Signal(Lo)   # Reset del contador horizontal y clock ena del vert
    rst_v = Signal(Lo)   # Reset del vertical       
 
    ####################################################
    #

    contador_H = CB_R(clk_i = clk50_i, 
                      rst_i = rst_h, 
                      q_o = h_cont)            # Cuenta pix horiz

    contador_V = CB_RE(clk_i = clk50_i, 
                       rst_i = rst_v, 
                       ce_i = rst_h, 
                       q_o = v_cont)    # Cuenta lineas  

    @always_comb
    def gen_rst() :
        if h_cont == H_TOTAL - 1 :
            rst_h.next = Hi
        else :
            rst_h.next = Lo
        if v_cont == (V_TOTAL - 1) and rst_h == Hi:
            rst_v.next = Hi
        else :
            rst_v.next = Lo

#    @always_comb
#    def gen_sync() :
#        if <h_cont

    return instances()
        

#######################################################################################################################

def genera_coord_PAL(clk27_i, 
                     vs_i, 
                     hs_i,
                     odd_even_i,
                     pix_ce_o,
                     pixel_x_o,
                     pixel_y_o,
                     video_activo_o,
                     ini_frame_o) :
    """Este modulo genera las coordenadas (x,y) del pixel activo actual de un sistema PAL (720x576i).  
    ::

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

    :Parametros:
        - `clk27_i`        -- entrada de clock de pixel x2 ( 27Mhz )
        - `vs_i`           -- entrada de sincronismo vertical
        - `hs_i`           -- entrada de sincronismo horizontal
        - `odd_even_i`     -- entrada de campo odd/even
        - `pix_ce_o`       -- salida de pixel clock enable  
        - `pixel_x_o`      -- salida de la coordenada x del pixel activo actual [0 .. 720] 
        - `pixel_y_o`      -- salida de la coordenada y del pixel activo actual [0 .. 576]
        - `video_activo_o` -- salida que determina la ventana temporal del video activo  
        - `ini_frame_o`    -- inicio del frame  

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
    
    ini_hs = Signal(Lo)     # Pulso de inicio de sincronismo horizontal
    ini_vs = Signal(Lo)     # Inicio de sincronismo vertical 
    pix_ce = Signal(Lo)     # Clock enable para contar pixels  

    barrido_x = Signal(intbv(0, 0, PIXELS_x_LINEA))   # Registros para llevar la posicion del barrido    
    nro_linea = Signal(intbv(0, 0, TOTAL_LINEAS))     # 

    ini_odd = Signal(Lo)          # Pulso de inicio de campo impar 
    rst_aux = Signal(Lo)
    rst_n_lineas = Signal(Lo)     # Reset del contador de lineas

    video_activo_x = Signal(Lo)
    video_activo_y = Signal(Lo)


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
                       t_i = Signal(Hi), 
                       q_o = pix_ce)       # Divide x2 la frec de clock
    
    gen_barrido_x = CB_RE(clk_i = clk27_i, 
                          rst_i = ini_hs, 
                          ce_i = pix_ce, 
                          q_o = barrido_x)     # Cuenta los "pixels" (tanto activos como los de blanking)
                                                    # en una linea de video, comenzando desde el flanco de bajada de hs   
                  
    @always_comb
    def gen_video_activo_x() :    
        if INICIO_X <= barrido_x and barrido_x < INICIO_X + PIXELS_x_LINEA_ACTIVA :    # Comparador para determinar la ventana temporal de la linea activa 
            video_activo_x.next = Hi
        else :
            video_activo_x.next = Lo
   

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
            video_activo_y.next = Hi
        else :
            video_activo_y.next = Lo

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

#############################################################################

def mix_sync_2_hs(clk27_i, 
                  mix_sync_i,                   
                  vs_i,
                  odd_even_i,
                  hs_o) :

    """Genera hs a partir de mix_sync"""

    FREC_CLK = 27e6
    TIEMPO_LINEA = 64e-6
    TIEMPO_H_SYNC = 4.7e-6
    TIEMPO_INHAB = 3 * TIEMPO_LINEA / 4   

    CUENTA_MAX = int(round(TIEMPO_LINEA * FREC_CLK))        
    CUENTA_H_SYNC = int(round(TIEMPO_H_SYNC * FREC_CLK))
    CUENTA_INHAB = int(round(TIEMPO_INHAB * FREC_CLK))
    

    ini_mix_sync = Signal(Lo)        # Pulso a la bajada de mix sync
    ini_vs = Signal(Lo)              # Pulso a la bajada de vs
    ini_field = Signal(Lo)           
    rst = Signal(Lo)
    ena_mix_sync = Signal(Lo)
    cuenta = Signal(intbv(0, 0, CUENTA_MAX + 1))
    

    #                ___      _      _      _      _      _   ______   ______   ______   ______   ______   ____________   _
    #   mix_sync        |____| |____| |____| |____| |____| |_|      |_|      |_|      |_|      |_|      |_|            |_|
    #                ________                                          ____________________________________________________
    #   vs_i                 |________________________________________|
    #                         _____________________________________________________________________________________________
    #   odd_even_i   ________|
    #
    #   ini_field_o  _________________|____________________________________________________________________________________
    #                ___   ___________   ___________   _____________   _______________   _______________   ____________   _
    #   hs_o            |_|           |_|           |_|             |_|               |_|               |_|            |_|
    #
    #   estado     ESPERA_VS |A|  B   |       ESPERA_VS 
    #                                              _               _                 _                 _              _   
    #   ena_mix_sync                   ___________| |_____________| |_______________| |_______________| |____________| |___

    ######################


    det_baj_mix_sync = detecta_flanco_bajada(clk_i = clk27_i,
                                             a_i = mix_sync_i,
                                             flanco_o = ini_mix_sync)

    det_baja_vs = detecta_flanco_bajada(clk_i = clk27_i,
                                        a_i = vs_i,
                                        flanco_o = ini_vs)


    e = enum("A", "B", "ESPERA_VS")
    estado = Signal(e.ESPERA_VS) 
                                                  
    @always(clk27_i.posedge)
    def FSM() :                    # Genera un pulso en la segunda bajada de mix sync dentro del vert
        ini_field.next = Lo
        if ini_vs :                 # ini_vs es el reset de la maquina
           estado.next = e.A
        else :
            ###########################
            if estado == e.A :      # Espera por el primer pulso de mix sync dentro de vert
                if ini_mix_sync :
                    estado.next = e.B
            ###########################
            elif estado == e.B :    # Espera por el segundo pulso .... 
                if ini_mix_sync :
                    ini_field.next = Hi            # .... y levanta ini_field        
                    estado.next = e.ESPERA_VS
            ############################    
            else :  # ESPERA_VS
                pass     # No hace nada solo espera hasta el proximo vertical

    
    cont = CB_R(clk_i = clk27_i,
                rst_i = rst,
                q_o = cuenta)
            
    @always_comb
    def gen_rst() :
        rst.next = (ini_field and odd_even_i) or (ena_mix_sync and ini_mix_sync)     

    @always(cuenta)
    def comparador1() :
        if cuenta < CUENTA_H_SYNC :
            hs_o.next = Lo
        else :
            hs_o.next = Hi 

    @always(cuenta)
    def comparador2() :
        if cuenta < CUENTA_INHAB :
            ena_mix_sync.next = Lo
        else :
            ena_mix_sync.next = Hi


    return instances()


#############################################################################

def char_gen_ROM(sel_char_i, 
                 char_x_i,
                 char_y_i,
                 bit_char_o) :
    """Generador de caracteres de 8x16.

    :: 
                                           
                      _______________________ 
                     |         ROM           |      _______________
                 ____|                       |     |      MUX      |
      sel_char_i ____| Adrr[n:4]             |     |   (sel_col)   |
                     |                       |     |               |
                     |                       |_____|               |
                     |                D[7:0] |_____| d[7:0]      q |---- char_o
                 ____|                       |     |               |
        char_y_i ____| Adrr[3:0]             |     |               |
                     |                       |     |   sel[2:0]    |
                     |_______________________|      ---------------
                                                          |  |
                                                          |  |
                                                        char_x_i 

    
    :Parametros:    
        - `sel_char_i` : selecciona el char para visualizar
        - `char_y_i`   : selecciona la fila del char (4 bits mas bajos del barrido o coordenada Y) 
        - `char_x_i`   : selecciona la columna del char (3 bits mas bajos del barrido o coordenada X)   
        - `bit_char_o` : salida bit a bit de la matriz del char seleccionado    
                               
    """

    n = len(sel_char_i)
    m = len(char_y_i)

    dato = Signal(intbv(0)[8:])
    address_rom = Signal(intbv(0)[n+m:])

    @always_comb
    def address() :
        address_rom.next = concat(sel_char_i, char_y_i)   

    @always(address_rom)
    def read_ROM() :
        dato.next = ROM_FONT[int(address_rom)]

    @always(dato, char_x_i)
    def sel_col() :
        if char_x_i == 0 :
            bit_char_o.next = dato[7]
        elif char_x_i == 1 :
            bit_char_o.next = dato[6]
        elif char_x_i == 2 :
            bit_char_o.next = dato[5]
        elif char_x_i == 3 :
            bit_char_o.next = dato[4]
        elif char_x_i == 4 :
            bit_char_o.next = dato[3]
        elif char_x_i == 5 :
            bit_char_o.next = dato[2]
        elif char_x_i == 6 :
            bit_char_o.next = dato[1]
        else :
            bit_char_o.next = dato[0]

    return instances()

###############################################################################################


