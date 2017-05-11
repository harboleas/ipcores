"""
PWM
===

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from Contadores import CB_R, CB_RE
from FlipFlops import FD_E

Lo = False
Hi = True

########################################################

def PWM(clk_i,
        d_i,
        pwm_o,
        CLK_FREC,
        PWM_FREC) :


    n = len(d_i)

    CUENTA_DIVISOR = int(round(CLK_FREC / ( PWM_FREC * 2**n )))

    cuenta_div = Signal(intbv(0, 0, CUENTA_DIVISOR + 1))

    cuenta_pwm = Signal(intbv(0)[n:])

    dato = Signal(intbv(0)[n:])
    rst_pwm = Signal(Lo)
    ce_pwm = Signal(Lo)

    contador_div = CB_R(clk_i = clk_i,           # "Divisor de frecuencia" 
                        rst_i = ce_pwm,
                        q_o = cuenta_div)

    @always(cuenta_div)
    def gen_ce_pwm() :
        if cuenta_div == CUENTA_DIVISOR - 1 :
            ce_pwm.next = Hi
        else :
            ce_pwm.next = Lo                     
                        

    contador_pwm = CB_RE(clk_i = clk_i,              
                         rst_i = rst_pwm,
                         ce_i = ce_pwm,
                         q_o = cuenta_pwm)

    reg_dato = FD_E(clk_i = clk_i,
                    ce_i = rst_pwm,
                    d_i = d_i,
                    q_o = dato)
    
    @always(cuenta_pwm, ce_pwm)
    def gen_rst_pwm() :
        if ce_pwm and cuenta_pwm == 2**n - 1 :
            rst_pwm.next = Hi
        else :
            rst_pwm.next = Lo

    @always(cuenta_pwm, dato)
    def gen_pwm_o() :
        if cuenta_pwm < dato :
            pwm_o.next = Hi
        else :
            pwm_o.next = Lo


    return instances()


