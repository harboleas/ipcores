"""
PID
===

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from FlipFlops import FD_RE
from Aritmeticos import ACC_RE

Lo = False
Hi = True

######################################

def PID(clk_i,           # clk 
        rst_i,           # reset del modulo
        update_i,        # muestreo del error
        e_i,             # error de entrada
        u_o,             # correccion
        Kp, Ki, Kd,      # constantes del PID (ej: Kp = 2.34, Ki = 0.001, Kd = 0.0289)  
        N ) :            # cantidad de bits de la parte fraccionaria 

    """PID con algoritmo "velocidad" """ 


    K0 = int(round((Kp + Ki + Kd) / 2**-N))         # escala las constantes con resolucion 2**-N
    K1 = int(round((Kp + 2*Kd) / 2**-N))
    K2 = int(round(Kd / 2**-N))

    K0_s = Signal(intbv(K0, 0, K0 + 1))             # Por problemas en la conversion a VHDL
    K1_s = Signal(intbv(K1, 0, K1 + 1))
    K2_s = Signal(intbv(K2, 0, K2 + 1))

    MIN_ERROR = e_i.min
    MAX_ERROR = e_i.max

    e_n_0 = Signal(intbv(0, MIN_ERROR, MAX_ERROR))    # Error actual
    e_n_1 = Signal(intbv(0, MIN_ERROR, MAX_ERROR))    # Error en "n - 1"
    e_n_2 = Signal(intbv(0, MIN_ERROR, MAX_ERROR))    # Error en "n - 2"

    Kmax = max(K0, K1, K2)

    MIN_ERROR_K = Kmax * MIN_ERROR
    MAX_ERROR_K = Kmax * MAX_ERROR

    e_n_0_K0 = Signal(intbv(0, MIN_ERROR_K, MAX_ERROR_K))    # Error actual
    e_n_1_K1 = Signal(intbv(0, MIN_ERROR_K, MAX_ERROR_K))    # Error en "n - 1"
    e_n_2_K2 = Signal(intbv(0, MIN_ERROR_K, MAX_ERROR_K))    # Error en "n - 2"

    MIN_DELTA_U_AUX = 2 * MIN_ERROR_K
    MAX_DELTA_U_AUX = 2 * MAX_ERROR_K

    delta_u_aux = Signal(intbv(0, MIN_DELTA_U_AUX, MAX_DELTA_U_AUX))

    MIN_DELTA_U = 3 * MIN_ERROR_K
    MAX_DELTA_U = 3 * MAX_ERROR_K

    delta_u = Signal(intbv(0, MIN_DELTA_U, MAX_DELTA_U))

    MIN_U = MIN_DELTA_U 
    MAX_U = MAX_DELTA_U 

    u_n_0 = Signal(intbv(0, MIN_U, MAX_U))            # salida con maxima resolucion
    u_n_1 = Signal(intbv(0, MIN_U, MAX_U))

    MIN_U_AUX = MIN_U >> N
    MAX_U_AUX = MAX_U >> N

    u_aux = Signal(intbv(0, MIN_U_AUX, MAX_U_AUX))     # salida escalada 

    MIN_U_O = u_o.min
    MAX_U_O = u_o.max

    #####################
    ### Descripcion 

    gen_e_n_0 = FD_RE(clk_i = clk_i,
                      rst_i = rst_i,
                      ce_i = update_i,
                      d_i = e_i,
                      q_o = e_n_0)         # Actualiza error

    gen_e_n_1 = FD_RE(clk_i = clk_i,
                      rst_i = rst_i,
                      ce_i = update_i,
                      d_i = e_n_0,
                      q_o = e_n_1)         # Error en n-1 

    gen_e_n_2 = FD_RE(clk_i = clk_i,
                      rst_i = rst_i,
                      ce_i = update_i,
                      d_i = e_n_1,
                      q_o = e_n_2)         # Error en n-2

    gen_u_n_1 = FD_RE(clk_i = clk_i,
                      rst_i = rst_i,
                      ce_i = update_i,
                      d_i = u_n_0,
                      q_o = u_n_1)         # Correccion anterior 

    @always_comb
    def gen_e_K() :
        e_n_0_K0.next = e_n_0 * K0_s      
        e_n_1_K1.next = e_n_1 * K1_s
        e_n_2_K2.next = e_n_2 * K2_s

    @always_comb
    def gen_delta_u_aux() :
        delta_u_aux.next = e_n_0_K0 + e_n_2_K2

    @always_comb
    def gen_delta_u() :
        delta_u.next = delta_u_aux - e_n_1_K1      

    @always(delta_u, u_n_1)
    def gen_u() :                             # Calcula la correccion de salida y la acota
        if u_n_1 + delta_u >= MAX_U :
            u_n_0.next = MAX_U - 1
        elif u_n_1 + delta_u <= MIN_U :
            u_n_0.next = MIN_U
        else :
            u_n_0.next = u_n_1 + delta_u

    @always_comb
    def shift_u() :
        u_aux.next = u_n_0 >> N     # Escala la salida
 
    @always(u_aux)
    def gen_u_o():                  # Acota la salida 
        if u_aux >= MAX_U_O :
            u_o.next = MAX_U_O - 1
        elif u_aux <= MIN_U_O :
            u_o.next = MIN_U_O
        else :
            u_o.next = u_aux        

    return instances()     

#############################################################

#import matplotlib.pyplot as plt
#from numpy import *

#def test() :

#    clk = Signal(Lo) 
#    rst = Signal(Lo)
#    update = Signal(Lo)
#    error = Signal(intbv(0, -256*2 + 30, 256*2 + 30 + 1))
#    u = Signal(intbv(0, -256, 256))
#    set_point = 30
#    out = Signal(intbv(0, -256*2, 256*2))

#    o = zeros(1000)
##    e = zeros(1000)

#    cuenta = Signal(intbv(0, 0, 16))


#    @always(delay(10))
#    def gen_clk() :
#        clk.next = not clk

#    @always(delay(150000))
#    def stop() :
#        plt.plot(o)
##        plt.plot(e)
#        plt.show()
#        raise StopSimulation


#    @always_comb
#    def gen_out() :
#        out.next = u * 2

#    @always_comb
#    def gen_error() :
#        error.next = set_point - out              

#    @instance
#    def gen_o() :
#        i = 0
#        while True :
#            o[i] = out
##            e[i] = error
#            i = i + 1
#            yield update.negedge

#    @always(clk.posedge)
#    def contar() :
#        if cuenta == 15 :
#            cuenta.next = 0
#            update.next = Hi
#        else :
#            cuenta.next = cuenta + 1
#            update.next = Lo

#    dut = PID(clk, rst, update, error, u, 0.25, 0.1, 0, 5)

#    return instances()

#tb = traceSignals(test)  # Genera el archivo vcd con todas las senales involucradas
#sim = Simulation(tb)
#sim.run()    




 

