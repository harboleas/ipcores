"""
Conversion a flotante
=====================

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from Contadores import CB_RE
from FlipFlops import FD_E
from ShiftRegister import SR_LE_PiPo_Izq

Hi = True
Lo = False

def conversion_half_precision(clk_i, 
                              x_i, 
                              signo_x_i, 
                              bits_entero, 
                              ini_i, 
                              fl_x_o, 
                              done_o) :
    """Conversor a punto flotante half-precision::

        signo_x : 0 = +, 1 = -
    
        x       : bn --- b16 b15 b14 . b13 b12 b11 b10 b9 b8 b7 b6 b5 b4 b3 b2 b1 b0
                   |______________|  
                          |
                    bits_entero

        fl_x    :   S | Exp + 15 | mantisa              
                    |       |         |                      
        cant_bits   1       5        10   

        x = (-1)^S * 2^Exp * 1.mantisa


    :Nota: la parte fraccionaria de x_i debe tener 14 bits, ya que el valor minimo positivo que se puede representar en half precision es 2**-14
           y como el maximo es 65504, la parte entera de x_i puede tener hasta 16 bits (Tener en cuenta que esta implementacion solo convierte
           los numeros normalizados y el cero, si x_i > 65504, el conversor no funciona)

    """

    n = len(x_i)
    m = len(fl_x_o)                     # 16 para half precision
    fl_x = Signal(intbv(0)[m:])         # Flotante Half Precision
    x_q = Signal(intbv(0)[n:])
    pos = Signal(intbv(0, 0, n + 1))    # Pos del primer 1 de x_i
    exp = Signal(intbv(0)[5:])          
    mantisa = Signal(intbv(0)[10:])

    k = 15 + bits_entero - 1            # exponente real = bits_entero - 1 - pos
                                        # exponente desplazado por norma = 15 + exponente real = k - pos 

    fin_contador = Signal(Lo)           # fin_contador indica que x_i es cero => expo = 0 
    encontrado = Signal(Lo)             # Indica que se encontro la pos en x_i que tiene el 1 de mayor peso
    fin_busqueda = Signal(Lo)           # Indica que se encontro la pos en x_i que tiene el 1 de mayor peso o x_i es cero
    cargar = Signal(Lo)                 # Carga x_i en el shift register
    despl_y_contar = Signal(Lo)         # Desplaza a la izquierda x y cuenta la pos para saber donde esta el 1 de mayor peso en x
    latch = Signal(Lo)                  # Antes de levantar la bandera de done, "latcheo" fl_x

    # Datapath

    reg = SR_LE_PiPo_Izq(clk_i = clk_i, 
                         load_i = cargar, 
                         d_i = x_i, 
                         ce_i = despl_y_contar, 
                         q_o = x_q)       # Desplazo x a la izquierda para encontrar el 1 de mayor peso

    @always_comb
    def extrae_mantisa() :
        mantisa.next = x_q[n-1:n-11]        # La mantisa son los 10 bits despues del 1 de mayor peso

    @always_comb
    def conexion_encontrado() :
        encontrado.next = x_q[n-1]     

    @always_comb
    def fin_busq() :
        fin_busqueda.next = fin_contador | encontrado

    contador = CB_RE(clk_i = clk_i, 
                     rst_i = cargar, 
                     ce_i = despl_y_contar, 
                     q_o = pos)     # Contador para conocer la pos del 1 de mayor peso de x_i y luego calcular el exponente 

    @always(pos)
    def fin_cont() :
        if pos == n :
            fin_contador.next = Hi
        else :
            fin_contador.next = Lo

    @always_comb
    def restador() :
        exp.next = k - pos

    @always_comb
    def conex_fl() :
        fl_x.next = concat(signo_x_i, exp, mantisa)

    reg_fl = FD_E(clk_i = clk_i, 
                  ce_i = latch, 
                  d_i = fl_x, 
                  q_o = fl_x_o)


    ######## Unidad de control del conversor

    e = enum("ESPERA_INICIO", "BUSQUEDA", "FIN")

    estado = Signal(e.ESPERA_INICIO)

    @always(clk_i.posedge)
    def FSM_estados() :
        "Logica de cambio de estados"
        ##############################
        if estado == e.ESPERA_INICIO :
            if ini_i :
                estado.next = e.BUSQUEDA
        ##############################
        elif estado == e.BUSQUEDA :
            if fin_busqueda :
                estado.next = e.FIN
        ##############################
        elif estado == e.FIN :          
            estado.next = e.ESPERA_INICIO

        else :
            estado.next = e.ESPERA_INICIO


    @always(estado, ini_i, fin_busqueda)
    def FSM_salidas() :
        "Logica de salida"
        ##############################
        if estado == e.ESPERA_INICIO :
            done_o.next = Hi             
            latch.next = Lo
            despl_y_contar.next = Lo
            if ini_i :
                cargar.next = Hi
            else :
                cargar.next = Lo
        ##############################  
        elif estado == e.BUSQUEDA :
            done_o.next = Lo
            cargar.next = Lo
            if fin_busqueda :
                despl_y_contar.next = Lo
                latch.next = Hi
            else :
                despl_y_contar.next = Hi
                latch.next = Lo
        #############################
        elif estado == e.FIN :
            done_o.next = Lo
            latch.next = Lo
            despl_y_contar.next = Lo
            cargar.next = Lo

        else :
            done_o.next = Lo
            latch.next = Lo
            despl_y_contar.next = Lo
            cargar.next = Lo

    return instances()
