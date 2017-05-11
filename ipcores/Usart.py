"""
Usart
=====

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from ShiftRegister import SR_LE_PiSo_Der, SR_RE_SiPo_Der
from Contadores import CB_R, CB_RE
from FlipFlops import FD, FD_E

Hi = True
Lo = False

#####################################################################################

def UART_TX(clk_i, 
            rst_i, 
            ini_tx_i, 
            dato_i, 
            tx_o, 
            fin_tx_o, 
            CLK_FREC_Hz, BAUDIOS) :
    """Modulo transmisor de : 8 bits de datos, sin paridad y 1 bit de stop

    Unidad de control

    .. graphviz::
        digraph { node [ color=lightblue2, style=filled ];
                  ESPERA_INI -> ESPERA_INI ;
                  ESPERA_INI -> TRANSM [ label = "ini" ];
                  TRANSM -> FIN;
                  FIN -> ESPERA_INI; }

    """

    TICKS_BIT = int(round(CLK_FREC_Hz / BAUDIOS))       # Duracion de un bit en ciclos de reloj

    TICKS_BIT_CMP = TICKS_BIT - 1   # Para que la comparacion n la convierta a "resize(signed.."

    SIZE_PAQ = len(dato_i) + 2                       # Tamano del paquete a enviar

    SIZE_PAQ_CMP = SIZE_PAQ - 1      # Para que la comparacion n la convierta a "resize(signed.."

    dato_paq = Signal(intbv(0)[SIZE_PAQ:])           # El dato empaquetado
	        

    bits_enviados = Signal(intbv(0, 0, SIZE_PAQ + 1))  # Cantidad de bits enviados

    ticks = Signal(intbv(0, 0, TICKS_BIT + 1))

    tx = Signal(Lo)


    e = enum("ESPERA_INI", "TRANSIMITIR", "FIN")
    estado = Signal(e.ESPERA_INI)

    # Senales de control
    rst = Signal(Hi)
    carga_dato = Signal(Lo)
    envia_bit = Signal(Lo)
    fin_envio = Signal(Lo)
    idle = Signal(Hi)
    contar_bits = Signal(Lo)          
    rst_ticks = Signal(Lo)
    fin_ticks = Signal(Lo)

    # Datapath

    @always_comb
    def paquete() :     # Arma el paquete con los bits de start, los datos y el stop   
	dato_paq.next = concat(Hi, dato_i, Lo)

    tx_reg = SR_LE_PiSo_Der(clk_i = clk_i, 
                            load_i = carga_dato, 
                            d_i = dato_paq, 
                            ce_i = envia_bit, 
                            q_o = tx)    # Shift register para enviar el paquete

    @always_comb
    def conex_salida() :
        tx_o.next = tx | idle         # Cuando no se envia nada, la linea permanece en alto (estado idle)

    contador_bits = CB_RE(clk_i = clk_i, 
                          rst_i = rst, 
                          ce_i = contar_bits, 
                          q_o = bits_enviados)     # Cuenta los bits enviados
    
    @always(bits_enviados)        
    def comp_fin_envio() :                          # Comparador que determina cuando se enviaron todos los bits
        if bits_enviados == SIZE_PAQ_CMP :
            fin_envio.next = Hi
        else :
            fin_envio.next = Lo

    contador_ticks = CB_R(clk_i = clk_i, 
                          rst_i = rst_ticks, 
                          q_o = ticks)    # Cuenta ciclos de reloj para saber la duracion de un bit

    @always(ticks)
    def comp_ticks() :
        if ticks == TICKS_BIT_CMP :
            fin_ticks.next = Hi
        else :
            fin_ticks.next = Lo      


    # Unidad de control
    @always(clk_i.posedge)
    def FSM_estados() :
        """Logica del estado siguiente"""
        if rst_i :
            estado.next = e.ESPERA_INI

        else :
            ###########################
            if estado == e.ESPERA_INI :
                if ini_tx_i :
                    estado.next = e.TRANSIMITIR
            ###########################
            elif estado == e.TRANSIMITIR :
                if fin_envio and fin_ticks :
                    estado.next = e.FIN
            ###########################
            elif estado == e.FIN :
                estado.next = e.ESPERA_INI

            else :
                estado.next = e.ESPERA_INI


    @always(estado, ini_tx_i, fin_envio, fin_ticks)
    def FSM_salidas() :
        """Logica combinacional de salida"""
        ###########################
        if estado == e.ESPERA_INI :
            fin_tx_o.next = Lo
            idle.next = Hi
            contar_bits.next = Lo
            rst.next = Hi
            rst_ticks.next = Hi
            envia_bit.next = Lo
            if ini_tx_i :
                carga_dato.next = Hi
            else :
                carga_dato.next = Lo
        ###########################
        elif estado == e.TRANSIMITIR :
            fin_tx_o.next = Lo
            carga_dato.next = Lo
            idle.next = Lo
            rst.next = Lo
            if fin_ticks : 
                envia_bit.next = Hi
                contar_bits.next = Hi
                rst_ticks.next = Hi
            else :
                envia_bit.next = Lo
                contar_bits.next = Lo
                rst_ticks.next = Lo
        ###########################
        elif estado == e.FIN :
            fin_tx_o.next = Hi
            carga_dato.next = Lo
            idle.next = Hi
            contar_bits.next = Lo
            rst.next = Lo
            rst_ticks.next = Lo
            envia_bit.next = Lo

        else :
            fin_tx_o.next = Lo
            carga_dato.next = Lo
            idle.next = Hi
            contar_bits.next = Lo
            rst.next = Hi
            rst_ticks.next = Lo
            envia_bit.next = Lo

    return instances()    


###########################################################################


def UART_RX(clk_i, 
            rst_i, 
            rx_i, 
            dato_o, 
            fin_rx_o, 
            CLK_FREC_Hz, BAUDIOS) :
    """Modulo receptor de : 8 bits de datos, sin paridad y 1 bit de stop

    Unidad de control

    .. graphviz::
        digraph { node [ color=lightblue2, style=filled ];
                  ESPERA_START -> ESPERA_START ;
                  ESPERA_START -> VERIF_START [ label = "RX == 0" ];
                  VERIF_START -> RECIBIR [ label = "medio_bit == 0" ];
                  VERIF_START -> ESPERA_START
                  RECIBIR -> VERIF_STOP [ label = "leyo 8bits" ];
                  VERIF_STOP -> FIN [label = "medio_bit == 1" ];
                  FIN -> ESPERA_START; }


    """

    TICKS_BIT = int(round(CLK_FREC_Hz / BAUDIOS))       # Duracion de un bit en ciclos de reloj
    TICKS_MEDIO_BIT = int(round(CLK_FREC_Hz / BAUDIOS / 2))       # Duracion de medio bit en ciclos de reloj

    TICKS_BIT_CMP = TICKS_BIT - 1
    TICKS_MEDIO_BIT_CMP = TICKS_MEDIO_BIT - 1     

    n = len(dato_o)

    SIZE_DATO_CMP = n - 1

    rx = Signal(Lo)

    dato_leido = Signal(intbv(0)[n:])
    bits_leidos = Signal(intbv(0, 0, n+1))         # Cantidad de bits leidos

    ticks = Signal(intbv(0,0, TICKS_BIT + 1))

    e = enum("ESPERA_START", "VERIF_START", "RECIBIR", "VERIF_STOP", "FIN")
    estado = Signal(e.ESPERA_START)


    # Senales de control
    rst = Signal(Lo)
    rst_ticks = Signal(Lo)
    lee_bit = Signal(Lo)
    contar_bits = Signal(Lo)
    fin_ticks = Signal(Lo)
    ticks_medio_bit = Signal(Lo)
    rst_ticks = Signal(Lo)
    fin_recepcion = Signal(Lo)
    dato_ok = Signal(Lo)


    reg_in = FD(clk_i = clk_i, 
                d_i = rx_i, 
                q_o = rx)        # Para tener la entrada sincronizada
    

    rx_reg = SR_RE_SiPo_Der(clk_i = clk_i, 
                            rst_i = rst, 
                            ce_i = lee_bit, 
                            sr_i = rx, 
                            q_o = dato_leido)

    reg_out = FD_E(clk_i = clk_i, 
                   ce_i = dato_ok, 
                   d_i = dato_leido, 
                   q_o = dato_o)

    contador_bits = CB_RE(clk_i = clk_i, 
                          rst_i = rst, 
                          ce_i = contar_bits, 
                          q_o = bits_leidos)    # Cuenta los bits leidos 

    @always(bits_leidos)
    def comp_fin_recepcion() :
        if bits_leidos == SIZE_DATO_CMP :
            fin_recepcion.next = Hi
        else :
            fin_recepcion.next = Lo

    contador_ticks = CB_R(clk_i = clk_i, 
                          rst_i = rst_ticks, 
                          q_o = ticks)    # Cuenta ciclos de reloj para saber la duracion de un bit

    @always(ticks)
    def comp_ticks() :
        if ticks == TICKS_BIT_CMP :
            fin_ticks.next = Hi
        else :
            fin_ticks.next = Lo      

        if ticks == TICKS_MEDIO_BIT_CMP :
            ticks_medio_bit.next = Hi
        else :
            ticks_medio_bit.next = Lo


    # Unidad de control del modulo RX

    @always(clk_i.posedge)
    def FSM_estados() :
        """Logica de cambio de estados"""
        if rst_i :
            estado.next = e.ESPERA_START
        else :
            #############################
            if estado == e.ESPERA_START :
                if not rx :                               # Cuando la linea de Rx baja empieza el proceso
                    estado.next = e.VERIF_START
            #############################
            elif estado == e.VERIF_START :
                if ticks_medio_bit :                  # Me paro en la mitad del bit de start para chequear que no haya sido un falso start
                    if not rx :
                        estado.next = e.RECIBIR             # Start Bit OK
                    else :
                        estado.next = e.ESPERA_START        # Falso Start Bit
            #############################
            elif estado == e.RECIBIR :
                if fin_recepcion and fin_ticks :
                    estado.next = e.VERIF_STOP
            #############################
            elif estado == e.VERIF_STOP :
                if fin_ticks :
                    if rx :                         # Bit de stop OK
                        estado.next = e.FIN
                    else :
                        estado.next = e.ESPERA_START     # Error en el bit de stop, vuelve e empezar
            #############################
            elif estado == e.FIN :
                estado.next = e.ESPERA_START

            else :            
                estado.next = e.ESPERA_START

    @always(estado, ticks_medio_bit, fin_ticks, rx)
    def FSM_salidas() :
        """Logica combinacional de salida"""
        #############################
        if estado == e.ESPERA_START :
            contar_bits.next = Lo
            rst.next = Hi
            rst_ticks.next = Hi
            lee_bit.next = Lo
            fin_rx_o.next = Lo
            dato_ok.next = Lo
        #############################
        elif estado == e.VERIF_START :
            dato_ok.next = Lo
            fin_rx_o.next = Lo
            contar_bits.next = Lo
            rst.next = Lo
            lee_bit.next = Lo
            if ticks_medio_bit :
                rst_ticks.next = Hi
            else :
                rst_ticks.next = Lo
        #############################
        elif estado == e.RECIBIR :
            dato_ok.next = Lo
            fin_rx_o.next = Lo
            rst.next = Lo
            if fin_ticks :
                lee_bit.next = Hi
                contar_bits.next = Hi
                rst_ticks.next = Hi
            else :
                rst_ticks.next = Lo
                lee_bit.next = Lo
                contar_bits.next = Lo
        #############################
        elif estado == e.VERIF_STOP :
            dato_ok.next = Lo
            fin_rx_o.next = Lo
            contar_bits.next = Lo
            rst.next = Lo
            lee_bit.next = Lo
            if fin_ticks :
                rst_ticks.next = Hi
                if rx :
                    dato_ok.next = Hi
                else :
                    dato_ok.next = Lo
            else :
                rst_ticks.next = Lo
                dato_ok.next = Lo
        #############################
        elif estado == e.FIN :
            dato_ok.next = Lo
            contar_bits.next = Lo
            rst.next = Hi
            rst_ticks.next = Hi
            lee_bit.next = Lo
            fin_rx_o.next = Hi

        else :
            dato_ok.next = Lo
            contar_bits.next = Lo
            rst.next = Hi
            rst_ticks.next = Hi
            lee_bit.next = Lo
            fin_rx_o.next = Lo

    return instances()


#######################################################################################

def test() :

    def test_uart() :
        
        clk = Signal(Lo)
        ini = Signal(Lo)
        conexionTX_RX = Signal(Hi)
        dato = Signal(intbv(0xA0)[8:])
        dato_leido = Signal(intbv(0)[8:])
        fin_tx = Signal(Lo)
        fin_rx = Signal(Lo)
        rst = Signal(Lo)

        TX = UART_TX(clk, rst, ini, dato, conexionTX_RX, fin_tx, 27e6, 19200)
        RX = UART_RX(clk, rst, conexionTX_RX, dato_leido, fin_rx, 27e6, 19200)

        @always(delay(10))
        def gen_clk() :
            clk.next = not clk

        @instance
        def gen_ini() :
            yield delay(20)
            ini.next = Hi
            yield delay(20)
            ini.next = Lo

        @always(fin_rx.negedge)
        def final() :
            raise StopSimulation

        return instances()

    tb = traceSignals(test_uart)
    sim = Simulation(tb)
    sim.run()    

