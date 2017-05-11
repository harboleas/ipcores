"""
Monoestable
===========

:Autor: Juan Gasulla <jgasulla@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from Contadores import CB_RE
from Deteccion_flancos import detecta_flanco_subida

Hi = True     # Niveles logicos
Lo = False

def Monoestable(clk_i,
                rst_i, 
                a_i,
                q_o, 
                FREC_CLK = 27e6, TIEMPO = 240e-9 ) :
    """Este modulo genera una senal que dura un tiempo determinado cuando es disparada por a_i 

    :Parametros:            
        - `clk_i`    : entrada de clock
        - `rst_i`    : senal de reset
        - `a_i`      : senal de disparo
        - `q_o`      : salida triguereada

    Funcionamiento::

                    _   _   _   _   _   _       _   _   _   _   _   _
        clk_i      | |_| |_| |_| |_| |_| | ... | |_| |_| |_| |_| |_| |
                        __                            
        a_i      ______|  |_______________ ... _______________________

                           _______________ ... __________         
        q_o      _________|                              |______________


    :Nota: a_i debe estar sincronica con el clk
                                     
    """
    CUENTA_MAX = int(round(TIEMPO*FREC_CLK))
    cuenta = Signal(intbv(0, 0, CUENTA_MAX + 1))
    ena = Signal(Lo)
    flanco = Signal(Lo)

    e = enum("ESP_FLANCO", "CUENTA")
    estado = Signal(e.ESP_FLANCO) 
    
    cont_1 = CB_RE(clk_i = clk_i, 
                   rst_i = flanco, 
                   ce_i = ena, 
                   q_o = cuenta)

    flanco_1 = detecta_flanco_subida(clk_i = clk_i, 
                                   a_i = a_i, 
                                   flanco_o = flanco)

    @always(clk_i.posedge)
    def FSM() :
        if rst_i :
            estado.next = e.ESP_FLANCO
 
        else :
            if estado == e.ESP_FLANCO :
                if flanco :
                    estado.next = e.CUENTA
                    ena.next = Hi
                    q_o.next = Hi

            elif estado == e.CUENTA :              
                if cuenta == CUENTA_MAX - 1 : 
                    ena.next = Lo
                    q_o.next = Lo
                    estado.next = e.ESP_FLANCO            

    return instances()

#####################################################################################################
i = 0
def testbench() :

    def test_monoestable() :
        
        clk = Signal(Lo)
        rst = Signal(Lo)
        a = Signal(Lo)
        q = Signal(Lo)
       

        
        e = enum("INICIO", "A", "B", "FIN")
        estado = Signal(e.INICIO)

        Mono = Monoestable(clk, rst, a, q)

        @always(delay(10))
        def gen_clk() :
            clk.next = not clk

        @always(clk.posedge)
        def gen_a() :
            global i            
            i = i + 1
            if (30 < i < 32) or (34 < i < 39) or (60 < i < 62) :
                a.next = Hi
            else :
                a.next = Lo        

        return instances()

    tb = traceSignals(test_monoestable)
    sim = Simulation(tb)
    sim.run(1000)    


