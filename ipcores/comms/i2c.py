"""
I2C
===

:Autores: Juan Gasulla <jgasulla@citedef.gob.ar>  Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------------------------------------------------

"""

from myhdl import *
from Contadores import CB_RE, CB_R
from FlipFlops import FD_E
from ShiftRegister import SR_LE_PiSo_Izq, SR_RE_SiPo_Izq

Hi = True
Lo = False

DATA_LENGTH = 8

##################################################################
### I2C MASTER
#

def i2c_bit_control(clk_i, 
                    rst_i, 
                    ctrl_reg_i, 
                    fin_op_o, 
                    tx_bit_i, 
                    rx_bit_o, 
                    sda_i, 
                    sda_o, 
                    scl_o, 
                    FREC_CLK, FREC_SCL) :
    """Controla el envio y recepcion de paquetes a nivel de bit
    
    clk_i : entrada de clock
    rst_i : reset sincronico
    ctrl_reg_i (4 bits) : gen_start | gen_stop | gen_tx_bit | gen_rx_bit
    fin_op_o : indica el fin de cada operacion de bit
    tx_bit_i : bit a enviar
    rx_bit_o : bit recibido

    """

    #####################################################
    # Senales y registros

    e = enum("IDLE", "START_A", "REP_START", "START_B", "START_C", "START_D", "STOP_A", "STOP_B", "STOP_C", "TX_A", "TX_B", "TX_C", "TX_D", "RX_A", "RX_B", "RX_C", "RX_D")
    estado_bit = Signal(e.IDLE)

    T = int(FREC_CLK / (2 * FREC_SCL))    # Ciclos de clock que debe esperar cada estado para pasar al siguiente

    cont = Signal(intbv(0, 0, T))
    rst_cont = Signal(True)

    gen_start = Signal(Lo)          # Comandos
    gen_stop = Signal(Lo)
    gen_tx_bit = Signal(Lo)
    gen_rx_bit = Signal(Lo)

    start_flag = Signal(Lo)  # Indica que se comenzo una transaccion, se resetea por un stop o un rst. Este flag sirve para determinar cuando se da el rep start

    leer_bit = Signal(Lo)
    
    #####################################################    
    # Datapath

    @always_comb
    def decodifica_cmd() :             
        gen_start.next = ctrl_reg_i[3]
        gen_stop.next = ctrl_reg_i[2]
        gen_tx_bit.next = ctrl_reg_i[1]
        gen_rx_bit.next = ctrl_reg_i[0]
    

    contador = CB_R(clk_i = clk_i, 
                    rst_i = rst_cont, 
                    q_o = cont)       # cuenta los ciclos de clock   

    reg = FD_E(clk_i = clk_i, 
               ce_i = leer_bit, 
               d_i = sda_i, 
               q_o = rx_bit_o)  # Guarda el dato en la transicion de RX_B a RX_C   


    ########################################################
    # FSM tipo Mealy
    #
    # Descripcion de los estados
    #
    #                       | A | B | C | D |
    #                       ____________
    #                SCL                |___
    #   START               ________
    #                SDA            |_______
    #
    #                       ____________
    #                SCL                |___
    #   REP START           ________
    #                SDA            |_______
    #
    #                            _______
    #                SCL    ____|       |___
    #   TX                   _______________
    #                SDA    |     DATO      | 
    #
    #                            _______
    #                SCL    ____|       |___
    #   RX                   _______________
    #                SDA    |     DATO      | 
    #                               |__ aqui leo el dato (transicion de B a C)
    #
    #                            ___________
    #                SCL    ____|       
    #   STOP                         _______
    #                SDA    ________|
    #
    #

    @always(clk_i.posedge)
    def FSM_seq() :
        if rst_i :
            estado_bit.next = e.IDLE
            start_flag.next = Lo
        else :
            ###########   IDLE   ############        
            if estado_bit == e.IDLE :                     

                if gen_start and (not start_flag) :
                    estado_bit.next = e.START_A    # envia el bit de start
                    start_flag.next = Hi           # y levanta el start_flag 

                elif gen_start and start_flag :
                    estado_bit.next = e.REP_START  # envia el bit de rep start   

                elif gen_stop :                   
                    estado_bit.next = e.STOP_A     # envia el bit de stop
                    start_flag.next = Lo           # y resetea el start_flag 

                elif gen_tx_bit :
                    estado_bit.next = e.TX_A       # envia el bit contenido en tx_bit_i

                elif gen_rx_bit :
                    estado_bit.next = e.RX_A       # recibe un bit y lo almacena en rx_bit_o 

                else :
                    estado_bit.next = e.IDLE

            ###########   START  ############
            elif estado_bit == e.START_A :
                if cont == T - 1 :
                    estado_bit.next = e.START_B
            #################################
            elif estado_bit == e.REP_START :
                if cont == T - 1 :
                    estado_bit.next = e.START_B
            #################################
            elif estado_bit == e.START_B :
                if cont == T - 1 :
                    estado_bit.next = e.START_C
            #################################
            elif estado_bit == e.START_C :
                if cont == T - 1 :
                    estado_bit.next = e.START_D
            #################################
            elif estado_bit == e.START_D :
                if cont == T - 1 :
                    if gen_tx_bit :
                        estado_bit.next = e.TX_A
                    else :
                        estado_bit.next = e.IDLE

            ###########     TX    ############
            elif estado_bit == e.TX_A :
                if cont == T - 1 :
                    estado_bit.next = e.TX_B
            #################################
            elif estado_bit == e.TX_B :
                if cont == T - 1 :
                    estado_bit.next = e.TX_C
            #################################
            elif estado_bit == e.TX_C :
                if cont == T - 1 :
                    estado_bit.next = e.TX_D
            #################################
            elif estado_bit == e.TX_D :
                if cont == T - 1 :
                    if gen_start :
                        estado_bit.next = e.REP_START
                    elif gen_tx_bit :
                        estado_bit.next = e.TX_A
                    elif gen_rx_bit :
                        estado_bit.next = e.RX_A
                    elif gen_stop :
                        estado_bit.next = e.STOP_A
                    else :
                        estado_bit.next = e.IDLE

            ###########     RX    ############
            elif estado_bit == e.RX_A :
                if cont == T - 1:
                    estado_bit.next = e.RX_B
            #################################
            elif estado_bit == e.RX_B :
                if cont == T - 1:
                    estado_bit.next = e.RX_C
            #################################
            elif estado_bit == e.RX_C :
                if cont == T - 1 :
                    estado_bit.next = e.RX_D
            #################################
            elif estado_bit == e.RX_D :
                if cont == T - 1 :
                    if gen_start :
                        estado_bit.next = e.REP_START
                    elif gen_tx_bit :
                        estado_bit.next = e.TX_A
                    elif gen_rx_bit :
                        estado_bit.next = e.RX_A
                    elif gen_stop :
                        estado_bit.next = e.STOP_A
                    else :
                        estado_bit.next = e.IDLE

            ###########    STOP   ############
            elif estado_bit == e.STOP_A :
                if cont == T - 1 :
                    estado_bit.next = e.STOP_B
            #################################
            elif estado_bit == e.STOP_B :
                if cont == T - 1 :
                    estado_bit.next = e.STOP_C
            #################################
            elif estado_bit == e.STOP_C :
                if cont == T - 1 :
                    if gen_start :
                        estado_bit.next = e.START_A
                    else :
                        estado_bit.next = e.IDLE

            else :
                estado_bit.next = e.IDLE
                             

    @always(estado_bit, start_flag, cont, tx_bit_i)               
    def FSM_comb() :
            ###########  IDLE   ############        
            if estado_bit == e.IDLE :
                rst_cont.next = Hi     # Mientras la maquina esta en IDLE el contador permanece reseteado
                fin_op_o.next = Lo
                leer_bit.next = Lo
                if start_flag :
                    scl_o.next = Lo
                    sda_o.next = Lo
                else :
                    scl_o.next = Hi
                    sda_o.next = Hi

            ###########   START  ############
            elif estado_bit == e.START_A :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi
                sda_o.next = Hi
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.REP_START :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Lo
                sda_o.next = Hi
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.START_B :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi                
                sda_o.next = Hi
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.START_C :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.START_D :
                leer_bit.next = Lo
                scl_o.next = Lo                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                    fin_op_o.next = Hi
                else :
                    rst_cont.next = Lo
                    fin_op_o.next = Lo

            ###########     TX    ############
            elif estado_bit == e.TX_A :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Lo                
                sda_o.next = tx_bit_i
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.TX_B :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi                
                sda_o.next = tx_bit_i
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.TX_C :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi                
                sda_o.next = tx_bit_i
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.TX_D :
                leer_bit.next = Lo
                scl_o.next = Lo                
                sda_o.next = tx_bit_i
                if cont == T - 1 :
                    rst_cont.next = Hi
                    fin_op_o.next = Hi
                else :
                    rst_cont.next = Lo
                    fin_op_o.next = Lo

            ###########     RX    ############
            elif estado_bit == e.RX_A :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Lo                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.RX_B :
                fin_op_o.next = Lo
                scl_o.next = Hi                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                    leer_bit.next = Hi
                else :
                    rst_cont.next = Lo
                    leer_bit.next = Lo
            #################################
            elif estado_bit == e.RX_C :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.RX_D :
                leer_bit.next = Lo
                scl_o.next = Lo                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                    fin_op_o.next = Hi
                else :
                    rst_cont.next = Lo
                    fin_op_o.next = Lo

            ###########    STOP   ############
            elif estado_bit == e.STOP_A :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Lo                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            elif estado_bit == e.STOP_B :
                fin_op_o.next = Lo
                leer_bit.next = Lo
                scl_o.next = Hi                
                sda_o.next = Lo
                if cont == T - 1 :
                    rst_cont.next = Hi
                else :
                    rst_cont.next = Lo
            #################################
            else :    # estado_bit == e.STOP_C :
                leer_bit.next = Lo
                scl_o.next = Hi               
                sda_o.next = Hi
                if cont == T - 1 :
                    rst_cont.next = Hi
                    fin_op_o.next = Hi
                else :
                    rst_cont.next = Lo
                    fin_op_o.next = Lo


    return instances()

###############################################

def I2C_Control(clk_i, 
                rst_i, 
                ctrl_I2C_i, 
                fin_bit_i, 
                ctrl_bit_o, 
                desp_tx_o, 
                load_tx, 
                desp_rx_o, 
                rst_rx_o, 
                fin_op_I2C_o) :

    estado_control = enum("IDLE", "ESPERA_START", "ENVIA_DATO", "ESPERA_FIN_TX", "RECIBE_ACK","DECIDE_RX_TX", "RECIBE_DATO", "ESPERA_FIN_RX", "TRANSMITE_ACK", "ESPERA_ACK", "ESPERA_STOP")

    estado = Signal(estado_control.IDLE)
    
    start_ctrl = Signal(Lo)
    stop_ctrl = Signal(Lo)
    write_ctrl = Signal(Lo)
    read_ctrl = Signal(Lo)
    ack_ctrl = Signal(Lo)
    
    start_bit = Signal(Lo)
    stop_bit = Signal(Lo)
    write_bit = Signal(Lo)
    read_bit = Signal(Lo)

##################################################
############## Contador de Bits ##################    
##################################################
    rst_cont =  Signal(Lo)
    contar = Signal(Lo)    
    cuenta = Signal(intbv(0, 0, DATA_LENGTH ))
    
    cont_bits = CB_RE(clk_i = clk_i, 
                      rst_i = rst_cont, 
                      ce_i = contar, 
                      q_o = cuenta)  

##################################################
######### Decodifica la senal de ctrl ############    
##################################################

    @always_comb
    def decodificador() :
        start_ctrl.next = ctrl_I2C_i[4]
        stop_ctrl.next = ctrl_I2C_i[3]
        write_ctrl.next = ctrl_I2C_i[2]
        read_ctrl.next = ctrl_I2C_i[1]
        ack_ctrl.next = ctrl_I2C_i[0]    
##################################################
######### Codifica la senal de ctrl_ bit #########    
##################################################

    @always_comb
    def codificador() :
        ctrl_bit_o.next[3] = start_bit 
        ctrl_bit_o.next[2] = stop_bit
        ctrl_bit_o.next[1] = write_bit
        ctrl_bit_o.next[0] = read_bit

##################################################
############# FSM de control de I2C ##############    
##################################################
    @always(clk_i.posedge)
    def FSM() :
        if rst_i :
            start_bit.next = Lo
            stop_bit.next = Lo
            write_bit.next = Lo
            read_bit.next = Lo
            estado.next = estado_control.IDLE

        ######################################
        elif estado == estado_control.IDLE :
            stop_bit.next = Lo 
            fin_op_I2C_o.next = Lo           
            if start_ctrl :
                start_bit.next = Hi
                estado.next = estado_control.ESPERA_START
        #######################################
        elif estado == estado_control.ESPERA_START :
            start_bit.next = Lo
            if fin_bit_i :
                load_tx.next = Hi
                write_bit.next = Hi
                rst_cont.next = Hi
                estado.next = estado_control.ESPERA_FIN_TX
        ############################################        
        elif estado == estado_control.ESPERA_FIN_TX :
            load_tx.next = Lo             
            write_bit.next = Lo            
            contar.next = Lo
            desp_tx_o.next = Lo 
            rst_cont.next = Lo             
            if fin_bit_i :
               estado.next = estado_control.ENVIA_DATO
        ############################################
        elif estado == estado_control.ENVIA_DATO :                     
            if cuenta == DATA_LENGTH - 1 :
                read_bit.next = Hi
                rst_rx_o.next = Hi
                estado.next = estado_control.RECIBE_ACK
            else :
                write_bit.next = Hi                
                contar.next = Hi
                desp_tx_o.next = Hi                 
                estado.next = estado_control.ESPERA_FIN_TX     
        ############################################
        elif estado == estado_control.RECIBE_ACK : 
            read_bit.next = Lo
            rst_rx_o.next = Lo
            if fin_bit_i :
                fin_op_I2C_o.next = Hi  
                desp_rx_o.next = Hi
                estado.next = estado_control.DECIDE_RX_TX   
        ############################################
        elif estado == estado_control.DECIDE_RX_TX :               
            desp_rx_o.next = Lo
            fin_op_I2C_o.next = Lo       
            if start_ctrl :
                start_bit.next = Hi
                estado.next = estado_control.ESPERA_START
            
            elif stop_ctrl :
                stop_bit.next = Hi
                estado.next = estado_control.ESPERA_STOP

            elif write_ctrl :
                load_tx.next = Hi
                write_bit.next = Hi
                rst_cont.next = Hi
                estado.next = estado_control.ESPERA_FIN_TX        
        
            elif read_ctrl :
                rst_rx_o.next = Hi
                read_bit.next = Hi
                rst_cont.next = Hi
                estado.next = estado_control.ESPERA_FIN_RX
            
        ##############################################        
        elif estado == estado_control.ESPERA_FIN_RX :
            rst_rx_o.next = Lo             
            read_bit.next = Lo            
            contar.next = Lo
            rst_cont.next = Lo             
            if fin_bit_i :
               desp_rx_o.next = Hi 
               estado.next = estado_control.RECIBE_DATO
        ############################################
        elif estado == estado_control.RECIBE_DATO :                     
            desp_rx_o.next = Lo 
            if cuenta == DATA_LENGTH - 1 :
                fin_op_I2C_o.next = Hi
                estado.next = estado_control.TRANSMITE_ACK
            else :
                read_bit.next = Hi                
                contar.next = Hi
                estado.next = estado_control.ESPERA_FIN_RX 
        #######################################
        elif estado == estado_control.TRANSMITE_ACK :
            fin_op_I2C_o.next = Lo
            if ack_ctrl :
                load_tx.next = Hi
                write_bit.next = Hi
                estado.next = estado_control.ESPERA_ACK
        #######################################
        elif estado == estado_control.ESPERA_ACK :
            load_tx.next = Lo
            write_bit.next = Lo
            if fin_bit_i :
                fin_op_I2C_o.next = Hi
                estado.next = estado_control.DECIDE_RX_TX

        #######################################
        elif estado == estado_control.ESPERA_STOP :
            stop_bit.next = Lo
            if fin_bit_i :
                fin_op_I2C_o.next = Hi
                estado.next = estado_control.IDLE

    return instances()   

##################################################################################

def I2C_Master(clk_i, 
               rst_i, 
               tx_reg_i, 
               rx_reg_o, 
               ctrl_i, 
               fin_op_o, 
               sda_i, 
               sda_o, 
               scl_o, 
               FREC_CLK, FREC_SCL) : 
    """I2C Master ( Single-Master )

    ::
                        ___________________                  
                   ____|                   |
        tx_reg_i   ____|  SR_LE_PiSo_Izq   |--------------------------          
                       |___________________|                         |  
                           ^           ^                             |
                           |           |                             |
                   load_tx |           | desp_tx                     | tx_bit 
                           |           |                     ________v_________
                      _____|___________|_____               |                  |
                     |                       |   ctrl_bit   |                  |
                 ____|                       |______________|                  | 
        ctrl_i   ____|                       |______________|                  |---- sda_o
                     |      I2C Control      |              |       I2C        |     
                     |                       |              |    bit control   |---- sda_i
        fin_op_o ----|                       |<-------------|                  |
                     |                       |   fin_bit    |                  |---- scl_o
                     |_______________________|              |                  |
                           |           |                    |                  |
                           |           |                    |__________________|
                           |           |                             |   
                    rst_rx |           | desp_rx                     | rx_bit
                        ___v___________v___                          |
                   ____|                   |                         |
        rx_reg_o   ____|  SR_RE_SiPo_Izq   |<-------------------------          
                       |___________________|                           



        clk_i : entrada de clock
        rst_i : reset sincronico
        tx_reg_i : registro de transmision
        rx_reg_i : registro de recepcion
        ctrl_i : registro de control (5 bits) --------> start | stop | write | read | ack
        fin_op_o : indica el fin de cada operacion
        sda_i : linea de entrada de datos I2C
        sda_o : linea de salida de datos I2C
        scl_o : salida de clock I2C

    """

    ###### Senales y registros auxiliares

    ctrl_bit = Signal(intbv(0)[5:])
    fin_bit = Signal(Lo)
    load_tx = Signal(Lo)
    rst_rx = Signal(Lo)
    desp_tx = Signal(Lo)
    desp_rx = Signal(Lo)
    tx_bit = Signal(Lo)
    rx_bit = Signal(Lo)

    #################################
    # Datapath
    
    Tx_reg = SR_LE_PiSo_Izq(clk_i = clk_i, 
                            load_i = load_tx, 
                            d_i = tx_reg_i, 
                            ce_i = desp_tx, 
                            q_o = tx_bit)

    Rx_reg = SR_RE_SiPo_Izq(clk_i = clk_i, 
                            rst_i = rst_rx, 
                            ce_i = desp_rx, 
                            sl_i = rx_bit, 
                            q_o = rx_reg_o)

    I2C_bit_ctrl = i2c_bit_control(clk_i = clk_i, 
                                   rst_i = rst_i, 
                                   ctrl_reg_i = ctrl_bit, 
                                   fin_op_o = fin_bit, 
                                   tx_bit_i = tx_bit, 
                                   rx_bit_o = rx_bit, 
                                   sda_i = sda_i, 
                                   sda_o = sda_o, 
                                   scl_o = scl_o, 
                                   FREC_CLK = FREC_CLK, FREC_SCL = FREC_SCL)

    I2C_ctrl = I2C_Control(clk_i = clk_i, 
                           rst_i = rst_i, 
                           ctrl_I2C_i = ctrl_i, 
                           fin_bit_i = fin_bit, 
                           ctrl_bit_o = ctrl_bit, 
                           desp_tx_o = desp_tx, 
                           load_tx = load_tx, 
                           desp_rx_o = desp_rx, 
                           rst_rx_o = rst_rx, 
                           fin_op_I2C_o = fin_op_o)


    return instances()

#####################################################################################################

def testbench() :

    def test_i2c() :
        
        clk = Signal(Lo)
        tx_reg = Signal(intbv(0)[8:])
        rx_reg = Signal(intbv(0)[8:])
        ctrl = Signal(intbv(0)[5:])
        fin_op = Signal(Lo)
        fin = Signal(Lo)
        rst = Signal(Lo)
        sda_i = Signal(Hi)
        sda_o = Signal(Hi)
        scl_o = Signal(Hi)

        e = enum("INICIO", "A", "B", "FIN")
        estado = Signal(e.INICIO)

        I2C = I2C_Master(clk, rst, tx_reg, rx_reg, ctrl, fin_op, sda_i, sda_o, scl_o, 27e6, 400e3)

        @always(delay(10))
        def gen_clk() :
            clk.next = not clk

        @always(clk.posedge)
        def FSM() :
            if estado == e.INICIO :
                tx_reg.next = 0xA0
                ctrl.next = 0b10000
                estado.next = e.A

            elif estado == e.A :
                ctrl.next = 0
                if fin_op :
                    ctrl.next = 0b01000
                    estado.next = e.B 

            elif estado == e.B :
                ctrl.next = 0
                if fin_op :
                    estado.next = e.FIN
                    fin.next = Hi

            else :     # estado = FIN
                estado.next = e.FIN                


        @always(fin.posedge)
        def final() :
            raise StopSimulation

        return instances()

    tb = traceSignals(test_i2c)
    sim = Simulation(tb)
    sim.run()    


