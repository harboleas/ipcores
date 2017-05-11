"""
Modulo para calculo de baricentro
=================================

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from lib.Aritmeticos import ACC_RE, DIV_Sec
from lib.Contadores import CB_RE
from lib.FlipFlops import FD, FD_E, FJK_R, F_SR
from lib.udiv import udiv

Lo = False
Hi = True

################################################################################################

def baricentro(clk_i,    # Clock
               rst_i,    # Reset del modulo 
               ce_i,     # Clock enable (dato valido)
               d_i,      # Masa del punto  
               x_i,      # Coordenada X del punto 
               y_i,      # Coordenada Y del punto 
               ini_roi_i, # Region de interes para el calculo de baricentro 
               fin_roi_i, 
               roi_i,
               baricentro_listo_o,  
               baricentro_x_o,      # Resultado del calculo del baricentro 
               baricentro_y_o,
               baricentro_ok_o,     # Indica si se pudo calcular el bari, el roi no estaba vacio
               TOTAL_PUNTOS_GATE,
               MAX_ACUM_X,
               MAX_ACUM_Y) :
    """Este modulo calcula las coordenadas del baricentro del contenido de la region de interes"""

    puntos_totales = Signal(intbv(0, 0, TOTAL_PUNTOS_GATE + 1))
    sum_x = Signal(intbv(0, 0, MAX_ACUM_X + 1))
    sum_y = Signal(intbv(0, 0, MAX_ACUM_Y + 1))

    fin_div_x = Signal(Lo)
    fin_div_y = Signal(Lo)
    fin_div_x_q = Signal(Lo)
    fin_div_y_q = Signal(Lo)
    fin_div = Signal(Lo)

    update = Signal(Lo)
    contar = Signal(Lo)
    dividir = Signal(Lo)
    acumular = Signal(Lo)
    rst = Signal(Lo)
    div0_x = Signal(Lo)
    div0_y = Signal(Lo)
    div0 = Signal(Lo)

    n = len(x_i)
    m = len(y_i)
    cociente_x = Signal(intbv(0)[n:])
    cociente_y = Signal(intbv(0)[m:])

    bari_ok = Signal(Lo)

    e = enum("ESPERAR_INI", "ACUMULAR", "DIVIDIR")
    estado = Signal(e.ESPERAR_INI)

    ####################################
    # Datapath

    ## Cuenta los puntos con "masa" dentro de la region de interes 
    cont_puntos = CB_RE(clk_i = clk_i, 
                        rst_i = rst, 
                        ce_i = contar, 
                        q_o = puntos_totales)

    ## Sumatoria de la pos_x de los puntos con "masa" dentro de la region de interes 
    acum_x = ACC_RE(clk_i = clk_i, 
                    rst_i = rst, 
                    ce_i = acumular, 
                    b_i = x_i, 
                    q_o = sum_x)

    ## Sumatoria de la pos_x de los puntos con "masa" dentro de la region de interes
    acum_y = ACC_RE(clk_i = clk_i, 
                    rst_i = rst, 
                    ce_i = acumular, 
                    b_i = y_i, 
                    q_o = sum_y)

    ## Al finalizar la region de interes, comienza la division
    #div_x = DIV_Sec(clk_i = clk_i, 
    #                rst_i = rst, 
    #                ini_i = dividir, 
    #                dividendo_i = sum_x, 
    #                divisor_i = puntos_totales, 
    #                div0_o = div0_x, 
    #                fin_o = fin_div_x, 
    #                cociente_o = cociente_x) 

    div_x = udiv(clk_i = clk_i, 
                    rst_i = rst, 
                    ini_i = dividir, 
                    dividendo_i = sum_x, 
                    divisor_i = puntos_totales, 
                    div0_o = div0_x, 
                    done_o = fin_div_x, 
                    cociente_o = cociente_x,
                    resto_o = Signal(intbv(0)[len(cociente_x):])) 
    
    #div_y = DIV_Sec(clk_i = clk_i, 
    #                rst_i = rst, 
    #                ini_i = dividir, 
    #                dividendo_i = sum_y, 
    #                divisor_i = puntos_totales, 
    #                div0_o = div0_y, 
    #                fin_o = fin_div_y, 
    #                cociente_o = cociente_y) 
    
    div_y = udiv(clk_i = clk_i, 
                    rst_i = rst, 
                    ini_i = dividir, 
                    dividendo_i = sum_y, 
                    divisor_i = puntos_totales, 
                    div0_o = div0_y, 
                    done_o = fin_div_y, 
                    cociente_o = cociente_y,
                    resto_o = Signal(intbv(0)[len(cociente_y):])) 

    @always_comb
    def division_0() :
        div0.next = div0_x | div0_y                             

    reg_fin_div_x = F_SR(clk_i = clk_i,
                         s_i = fin_div_x,
                         r_i = fin_div,        # Para que fin_div dure solo un clock
                         q_o = fin_div_x_q)


    reg_fin_div_y = F_SR(clk_i = clk_i,
                         s_i = fin_div_y,
                         r_i = fin_div,        # Para que fin_div dure solo un clock
                         q_o = fin_div_y_q)

    @always_comb
    def fin_division() :
        fin_div.next = fin_div_x_q & fin_div_y_q    


    gen_baricentro_listo = FD(clk_i = clk_i,
                              d_i = fin_div,
                              q_o = baricentro_listo_o)  

    # Al finalizar la division actualizo los resultados y se mantienen hasta que un nuevo dato este listo o hasta un rst externo

    reg_div_x = FD_E(clk_i = clk_i,
                     ce_i = fin_div,
                     d_i = cociente_x,
                     q_o = baricentro_x_o)

    reg_div_y = FD_E(clk_i = clk_i,
                     ce_i = fin_div,
                     d_i = cociente_y,
                     q_o = baricentro_y_o)

    reg_bari_ok = FD_E(clk_i = clk_i,
                       ce_i = fin_div,
                       d_i = bari_ok,    
                       q_o = baricentro_ok_o)

    ## Ordena los procesos de acumular y dividir
    @always(clk_i.posedge)
    def FSM_estados() :
        if rst_i :
            estado.next = e.ESPERAR_INI

        else :
            if estado == e.ESPERAR_INI :
                if ini_roi_i :
                    estado.next = e.ACUMULAR

            elif estado == e.ACUMULAR :
                if fin_roi_i :            
                    estado.next = e.DIVIDIR

            elif estado == e.DIVIDIR :
                if div0 :
                    estado.next = e.ESPERAR_INI
                elif not div0 and fin_div :
                    estado.next = e.ESPERAR_INI
            else :
                estado.next = e.ESPERAR_INI
   

    @always(estado, ini_roi_i, fin_roi_i, roi_i, d_i, ce_i, div0, fin_div)
    def FSM_salidas() :

        if estado == e.ESPERAR_INI :
            acumular.next = Lo
            contar.next = Lo
            dividir.next = Lo
            bari_ok.next = Lo
            if ini_roi_i :
                rst.next = Hi
            else :
                rst.next = Lo

        elif estado == e.ACUMULAR :
            bari_ok.next = Lo
            rst.next = Lo
            if d_i and ce_i and roi_i:       
                acumular.next = Hi          # Acumula la pos y cuenta los puntos con "masa"
                contar.next = Hi
            else :
                acumular.next = Lo
                contar.next = Lo
            if fin_roi_i:                   # Al finalizar la region de interes comienzo a dividir
                dividir.next = Hi
            else :
                dividir.next = Lo
  
        elif estado == e.DIVIDIR :
            rst.next = Lo
            acumular.next = Lo
            contar.next = Lo
            dividir.next = Lo
            if not div0 and fin_div :
                bari_ok.next = Hi
            else :
                bari_ok.next = Lo
        else :
            acumular.next = Lo
            contar.next = Lo
            dividir.next = Lo
            bari_ok.next = Lo
            rst.next = Hi    

 
    return instances()



