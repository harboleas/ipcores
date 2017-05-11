"""
Aritmeticos
===========

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>
------------------------------------------------

"""

from myhdl import *
from FlipFlops import FD_RE, FD_E
from ShiftRegister import *
from Contadores import *

Hi = True       # Definicion de niveles logicos
Lo = False      

##########################################################

def ACC_RE(clk_i, 
           rst_i, 
           ce_i, 
           b_i, 
           q_o) :
    """Acumulador de n bits con reset sincronico 
    y clock enable::
          __________________________________________
         |  ______________________________________  |
         | |   _________                          | |
         | |__|         |            __________   | |
         |____| a       |___________|          |__| |__
              |       s |___________| d      q |_______ q_o
          ____|         |           |          |
      b_i ____| b       |  clk_i----|> clk     |
              |_________|           |          |
                sumador     ce_i----| ce       |
                                    |          |
                           rst_i----| rst      |     
                                    |__________|
                                      reg (FD)

    :Parametros:
        - `clk_i` : clock
        - `rst_i` : reset sincronico
        - `ce_i`  : clock enable
        - `b_i`   : entrada para acumular (m bits)
        - `q_o`   : salida del acumulador (n bits)

    """  
 
    n = len(q_o) 

    a = Signal(intbv(0)[n:])          # Entrada al sumador
    suma = Signal(intbv(0)[n:])       # Salida del sumador 

    # Descripcion mixta (comportamiento y estructural)

    @always_comb
    def sumador() :
        suma.next = a + b_i

    reg_suma = FD_RE(clk_i = clk_i, 
                     rst_i = rst_i, 
                     ce_i = ce_i, 
                     d_i = suma, 
                     q_o = a)          #Memoriza el valor de la suma y lo almacena en a

    @always_comb
    def conex_q() :
        q_o.next = a

    return instances()

############################################################################

def ACC_RLE(clk_i, 
            rst_i, 
            load_i, 
            d_i, 
            ce_i, 
            b_i, 
            q_o) :
    """Acumulador de n bits con reset y carga sincronicos 
    y clock enable::

             ____________________________________________________________
            |  ________________________________________________________  |
            | |   _________                                            | |
            | |__|         |    _________                 __________   | |
            |____| a       |___|         |_______________|          |__| |__
                 |       s |___| i0    o |_______________| d      q |_______ q_o
          _______|         |   |         |               |          |
      b_i _______| b       |   |         |        clk_i--|> clk     |
                 |_________|   |   mux   |               |          |
                   sumador     |         |     ----------| ce       |
             __________________|         |     |         |          |
      d_i    __________________| i1      |     |  rst_i--| rst      |     
                               |_________|     |         |__________|
                                    |          |           reg (FD)
                                    |   ____   |
      load_i -----------------------o--\    \  |
                                        | or |-- 
      ce_i ----------------------------/____/

    
    :Parametros:
        - `clk_i`  : clock
        - `rst_i`  : reset sincronico
        - `load_i` : carga sincronica
        - `d_i`    : entrada de datos para cargar (n bits)
        - `ce_i`   : clock enable
        - `b_i`    : entrada para acumular (m bits)
        - `q_o`    : salida del acumulador (n bits)

    """  

    n = len(q_o)  

    a = Signal(intbv(0)[n:])        # Entrada del sumador   
    suma = Signal(intbv(0)[n:])     # Salida del sumador 
    mux_out = Signal(intbv(0)[n:])  # Salida del mux
    load_or_ce = Signal(Lo)         # Or entre load_i y ce_i

    # Descripcion mixta (comportamiento y estructural)
       
    @always_comb
    def sumador() :
        suma.next = a + b_i

    @always(suma, d_i, load_i)
    def mux() :
        if load_i :
            mux_out.next = d_i
        else :
            mux_out.next = suma

    @always_comb
    def compuerta_or() :
        load_or_ce.next = load_i | ce_i

    reg = FD_RE(clk_i = clk_i, 
                rst_i = rst_i, 
                ce_i = load_or_ce, 
                d_i = mux_out, 
                q_o = a)         #Almacena en a la suma o el valor a cargar 

    @always_comb
    def conex_q() :
        q_o.next = a

    return instances()

############################################

def ABS(a_i, 
        b_o) :
    """Calcula el valor absoluto de a_i::

                                     _________ 
             _______________________|         |
            |  _____________________|i0       |
            | |                     |   mux   |____
            | |   _        _____    |      out|____ b_o
          __| |__| \  ____|     |___|         |
      a_i _______|  |O____| + 1 |___|i1       |
            |    |_/      |_____|   |_________|
            |    inv                     |
            |____________________________|
                   msb de a_i (signo)

    :Parametros:
        - `a_i` : entrada (signed n bits)
        - `b_o` : salida (unsigned n-1 bits)
   
    """
    n = len(a_i)

    max_suma = 2**(n-1)

    inv_a = Signal(intbv(0)[n-1:])
    a_comp2 = Signal(intbv(0, 0, max_suma))

    # Calcula el complemento a 2 de a_i

    @always_comb
    def invertir_a() :
        inv_a.next = ~a_i[n-1:0]

    @always_comb
    def sumar_1() :
        a_comp2.next = (inv_a + 1) % max_suma

    # y luego elije segun el signo de a_i  

    @always(a_i, a_comp2)
    def mux() :
        if not a_i[n-1] :       # Signo positivo
            b_o.next = a_i[n-1:0]
        else :                    # Signo negativo
            b_o.next = a_comp2

    return instances()

############################################

def MULT_Sec(clk_i, 
             rst_i, 
             ini_i, 
             a_i, 
             b_i, 
             fin_o, 
             resul_o) :  
    """Multiplicador secuencial de numeros enteros no negativos 
    con reset y comienzo sincronico::
    
                                            a_i
                                            | |   
                       ---------         ----V----
                      | reg_AH  |<--    | reg_AL  |    
                       ----V----    |    ----V----
                          | |        -------| |
                          | |_______________| |
                          |________   ________|
         b_i                       | |
         | |                   ____|_|_____                _______
       ---V---                |            |      ini_i-->|       |-->
      | reg_B |               | acumulador |              |  U/C  |
       ---V---                |____________|           -->|_______|-->fin_o
         | |------>                | |
       -------                      V
      | == 0  |--->              resul_o
       ------- 
    

    Diagrama de estados de la unidad de control

    .. graphviz ::
        digraph { node [color=lightblue2, style=filled];
                  INI -> INI; 
                  INI -> ACUM_DESPL [ label = "ini" ];
                  ACUM_DESPL -> FIN [ label = "b_es_cero" ];
                  ACUM_DESPL -> ACUM_DESPL ;
                  FIN -> INI; }

    :Parametros:
        - `clk_i`   : clock
        - `rst_i`   : reset sincronico
        - `ini_i`   : comienzo
        - `a_i`     : 1er factor (n bits)
        - `b_i`     : 2do factor (m bits)
        - `fin_o`   : indica la finalizacion de la multiplicacion
        - `resul_o` : resultado de la multiplicacion (n+m bits)
  
    """
   
    n = len(a_i)             
    m = len(b_i)

    b = Signal(intbv(0)[m:0])
    al = Signal(intbv(0)[n:0])
    ah = Signal(intbv(0)[m:0])
    al_n = Signal(Lo)
    a = Signal(intbv(0)[n+m:0])

    # entradas a la maquina
    b_0 = Signal(Lo)
    b_es_cero = Signal(Lo)

    # salidas de la maquina
    acumula = Signal(Lo)
    carga = Signal(Lo)
    rst = Signal(Lo)
    desplaza = Signal(Lo)

    e = enum("INI", "ACUM_DESPL", "FIN")
    estado = Signal(e.INI) 

    # DATAPATH

    @always_comb
    def conex_al() :
        al_n.next = al[n-1]

    @always_comb
    def conex_a() :
        a.next = concat(ah, al)

    @always_comb
    def conex_b() :
        b_0.next = b[0] 
                   
    shreg_AL = SR_LE_PiPo_Izq(clk_i = clk_i, 
                              load_i = carga, 
                              d_i = a_i, 
                              ce_i = desplaza, 
                              q_o = al)
 
    shreg_AH = SR_RE_SiPo_Izq(clk_i = clk_i, 
                              rst_i = rst, 
                              ce_i = desplaza, 
                              sl_i = al_n, 
                              q_o = ah)

    acumulador = ACC_RE(clk_i = clk_i, 
                        rst_i = rst, 
                        ce_i = acumula, 
                        b_i = a, 
                        q_o = resul_o)

    shreg_B = SR_LE_PiPo_Der(clk_i = clk_i, 
                             load_i = carga, 
                             d_i = b_i, 
                             ce_i = desplaza, 
                             q_o = b)

    @always_comb
    def comparador() :
        if b == 0 :
            b_es_cero.next = Hi
        else :
            b_es_cero.next = Lo


    @always(clk_i.posedge)       
    def FSM_estados() :       
        "Unidad de control del multiplicador. FSM Mealy, parte secuencial"
        if rst_i :              # reset sincronico de la maquina
            estado.next = e.INI   
        else :
            ####################
            if estado == e.INI :
                if ini_i :
                    estado.next = e.ACUM_DESPL
                else :
                    estado.next = e.INI
            ####################
            elif estado == e.ACUM_DESPL :
                if b_es_cero :
                    estado.next = e.FIN 
                else :
                    estado.next = e.ACUM_DESPL
            ####################
            elif estado == e.FIN :
                estado.next = e.INI

            else :
                estado.next = e.INI

    @always(estado, ini_i, b_0)
    def FSM_salidas() :
        "Unidad de control del multiplicador. FSM Mealy, parte combinacional"
        ####################
        if estado == e.INI :
            fin_o.next = Lo
            acumula.next = Lo
            desplaza.next = Lo
            if ini_i :
                carga.next = Hi
                rst.next = Hi
            else :
                carga.next = Lo
                rst.next = Lo
        ####################
        elif estado == e.ACUM_DESPL :
            fin_o.next = Lo
            rst.next = Lo
            carga.next = Lo
            desplaza.next = Hi
            if b_0 :
               acumula.next = Hi
            else : 
               acumula.next = Lo
        ####################
        elif estado == e.FIN :         
            fin_o.next = Hi
            desplaza.next = Lo
            carga.next = Lo
            rst.next = Lo
            acumula.next = Lo
  

    return instances()

#############################################################

def nucleo_division(clk_i, 
                    rst_i, 
                    ini_i, 
                    dividendo_i,
                    divisor_i,
                    div0_o,
                    fin_o, 
                    cociente,
                    resto_q, 
                    CICLOS_DIVISION) :
    """Esta funcion es el nucleo de la operacion de division secuencial::

                                   divisor_i                       _______ 
                                      | |                 ini_i-->|       |-->
                                 ------V------                    |  U/C  |         
                                | reg_divisor |                -->|_______|-->fin_o     
                                 ------V------                                            
        _______________________       | |                                                 
       |  ____________________ \_____/ /                                         
       | |                    \   -   /                                          
       | |                     \_____/                                              
       | |   --------------      | |                       
       | |  | reg_cociente |<----| |              dividendo_i
       | |   ------V-------      | |                  | |                 |
       | |                   -----V-----        -------V-------       ----V-----
       | |                  | reg_resto |<----<| reg_dividendo |     | contador |
       | |                   -----V-----        ---------------       ----V-----
       | |                       | |                                     | |
       | |_______________________| |
       |___________________________|


    Diagrama de estados de la unidad de control

    .. graphviz ::
        digraph { node [color=lightblue2, style=filled];
                  INI -> INI; 
                  INI -> DESPLAZA [ label = "ini" ];
                  DESPLAZA -> FIN [ label = "divisor==0" ];
                  DESPLAZA -> RESTA;
                  RESTA -> DESPLAZA;
                  RESTA -> FIN [ label = "fin_contador" ]
                  FIN -> INI; }


    :Parametros:    
        - `clk_i`       : clock
        - `rst_i`       : reset sincronico
        - `ini_i`       : comienzo de la division
        - `dividendo_i` : dividendo (n bits)
        - `divisor_i`   : divisor (m bits)
        - `div0_o`      : division por cero
        - `fin_o`       : indica la finalizacion de la division
        - `cociente`    : salida del registro cociente
        - `resto_q`     : salida del registro resto
        - `CICLOS_DIVISION` : controla si la division es entera o con parte fraccionaria

    """

    n = len(dividendo_i)
    m = len(divisor_i)
    r = len(resto_q)

    divisor = Signal(intbv(0)[m:])      # salida del registro divisor

    resto = Signal(intbv(0, -(2**r), 2**r))  # salida del restador 

    resto_n = Signal(intbv(0)[r:])      # entrada del registro resto
    conex_dividendo_resto_q = Signal(Lo)                # conexion del dividendo al resto
    ciclos = Signal(intbv(0, 0, CICLOS_DIVISION + 1))   # ciclos de reloj utilizados para realizar la division    
   
    # Entradas de la maquina
    rmid = Signal(Lo)    # indica si el resto es mayor o igual que el divisor
    fin_contador = Signal(Lo)
    divisor_0 = Signal(Lo)

    # Salidas de la maquina de estados
    cargar = Signal(Lo)     # carga inicial del dividendo y divisor
    restar = Signal(Lo)     # habilitacion para restar
    desplazar = Signal(Lo)     # desplaza el dividendo y el resto
    rst_aux = Signal(Lo)     
    rst = Signal(Lo)     # reset del resto, cociente y el contador
    coc_0 = Signal(Lo)     # el bit menos significativo de cociente
    despl_coc = Signal(Lo)     # desplaza el cociente

    e = enum("INI", "DESPLAZA", "RESTA", "FIN")
    estado = Signal(e.INI) 

    # DATAPATH

    reg_divisor = FD_E(clk_i = clk_i, 
                       ce_i = cargar, 
                       d_i = divisor_i, 
                       q_o = divisor)

    reg_dividendo = SR_LE_PiSo_Izq(clk_i = clk_i, 
                                   load_i = cargar, 
                                   d_i = dividendo_i, 
                                   ce_i = desplazar, 
                                   q_o = conex_dividendo_resto_q)

    @always(divisor)
    def comp_divisor_0() :
        if divisor == 0 :
            divisor_0.next = Hi
        else :  
            divisor_0.next = Lo

    @always_comb
    def entrada_reg_resto() :
        resto_n.next = resto[r:0]
    
    reg_resto = SR_RLE_SiPo_Izq(clk_i = clk_i, 
                                rst_i = rst, 
                                load_i = restar, 
                                d_i = resto_n, 
                                ce_i = desplazar, 
                                sl_i = conex_dividendo_resto_q, 
                                q_o = resto_q)

    @always_comb
    def restador() :
        resto.next = resto_q - divisor

    @always_comb
    def comparador_rd() :        # compara si resto es mayor que divisor
        rmid.next = not resto[r]

    reg_cociente = SR_RE_SiPo_Izq(clk_i = clk_i, 
                                  rst_i = rst, 
                                  ce_i = despl_coc, 
                                  sl_i = coc_0, 
                                  q_o = cociente)

    contador = CB_RE(clk_i = clk_i, 
                     rst_i = rst, 
                     ce_i = desplazar, 
                     q_o = ciclos)  

    @always_comb
    def comparador_cont() :
        if ciclos == CICLOS_DIVISION :
            fin_contador.next = Hi
        else :
            fin_contador.next = Lo

    @always_comb
    def reset() :
        rst.next = rst_i | rst_aux

    # UNIDAD DE CONTROL: FSM

    @always(clk_i.posedge)       
    def FSM_estados() :       
        "Unidad de control. FSM Mealy, parte secuencial"
        if rst_i :              # reset sincronico de la maquina
            estado.next = e.INI   
        else :
            ####################
            if estado == e.INI :
                if ini_i :
                    estado.next = e.DESPLAZA
            ####################
            elif estado == e.DESPLAZA :
                if divisor_0 :
                    estado.next = e.FIN
                else :
                    estado.next = e.RESTA
            ####################
            elif estado == e.RESTA :
                if fin_contador :
                    estado.next = e.FIN 
                else :
                    estado.next = e.DESPLAZA
            ####################
            elif estado == e.FIN :
                estado.next = e.INI

            else :
                estado.next = e.INI

    @always(estado, ini_i, rmid, fin_contador, divisor_0)
    def FSM_salidas() :
        ####################
        if estado == e.INI :
            div0_o.next = Lo
            coc_0.next = Lo
            despl_coc.next = Lo
            restar.next = Lo
            desplazar.next = Lo
            fin_o.next = Lo
            if ini_i :
                rst_aux.next = Hi
                cargar.next = Hi
            else :
                rst_aux.next = Lo
                cargar.next = Lo
        ####################
        elif estado == e.DESPLAZA :
            cargar.next = Lo
            restar.next = Lo
            rst_aux.next = Lo
            coc_0.next = Lo
            despl_coc.next = Lo
            fin_o.next = Lo
            if divisor_0 :
                div0_o.next = Hi
            else :
                div0_o.next = Lo
            if not fin_contador :
                desplazar.next = Hi
            else :
                desplazar.next = Lo
        ##################### 
        elif estado == e.RESTA :
            div0_o.next = Lo
            cargar.next = Lo
            desplazar.next = Lo
            rst_aux.next = Lo
            despl_coc.next = Hi
            fin_o.next = Lo
            if rmid :
                restar.next = Hi
                coc_0.next = Hi
            else :
                restar.next = Lo
                coc_0.next = Lo
        #####################
        elif estado == e.FIN :
            div0_o.next = Lo
            cargar.next = Lo
            restar.next = Lo
            rst_aux.next = Lo
            coc_0.next = Lo
            despl_coc.next = Lo
            desplazar.next = Lo
            fin_o.next = Hi

        else :
            div0_o.next = Lo
            cargar.next = Lo
            restar.next = Lo
            rst_aux.next = Lo
            coc_0.next = Lo
            despl_coc.next = Lo
            desplazar.next = Lo
            fin_o.next = Lo

  
    return instances()

###################################################################

def DIV_Sec(clk_i, 
            rst_i, 
            ini_i, 
            dividendo_i, 
            divisor_i, 
            div0_o, 
            fin_o,
            cociente_o) :
    """Divisor secuencial de numeros enteros no negativos
    con reset e inicio sincronico 

    :Parametros:    
        - `clk_i`       : clock
        - `rst_i`       : reset sincronico
        - `ini_i`       : comienzo de la division
        - `dividendo_i` : dividendo (n bits)
        - `divisor_i`   : divisor (m bits)
        - `div0_o`      : division por cero
        - `fin_o`       : indica la finalizacion de la division
        - `cociente_o`  : cociente (n o p bits, si se estima el resultado)   

    """

    n = len(dividendo_i)
    m = len(divisor_i)
    p = len(cociente_o)    # Si es posible estimar el resultado de la division, es mejor no gastar bits  (p <= n)                            

    cociente = Signal(intbv(0)[p:])      # salida del cociente
    resto_q = Signal(intbv(0)[m+1:])      # salida del registro resto 

    nucleo = nucleo_division(clk_i, rst_i, ini_i, dividendo_i, divisor_i, div0_o, fin_o, cociente, resto_q, n)        

    @always_comb
    def salida() :
        cociente_o.next = cociente

    return instances()
    
#############################################################


def DIV_Sec_resto(clk_i, 
                  rst_i, 
                  ini_i, 
                  dividendo_i, 
                  divisor_i, 
                  div0_o, 
                  fin_o, 
                  cociente_o, 
                  resto_o) :
    """Divisor secuencial de numeros enteros no negativos
    con reset e inicio sincronico (y salida de resto) 
    
    :Parametros:    
        - `clk_i`       : clock
        - `rst_i`       : reset sincronico
        - `ini_i`       : comienzo de la division
        - `dividendo_i` : dividendo (n bits)
        - `divisor_i`   : divisor (m bits)
        - `div0_o`      : division por cero
        - `fin_o`       : indica la finalizacion de la division
        - `cociente_o`  : cociente (n o p bits, si se estima el resultado)   
        - `resto_o`     : resto (m bits)
  
    """


    n = len(dividendo_i)
    m = len(divisor_i)
    p = len(cociente_o)    # Si es posible estimar el resultado de la division, es mejor no gastar bits  (p <= n)                            

    cociente = Signal(intbv(0)[p:])      # salida del cociente
    resto_q = Signal(intbv(0)[m+1:])       # salida del registro resto 

    nucleo = nucleo_division(clk_i, rst_i, ini_i, dividendo_i, divisor_i, div0_o, fin_o, cociente, resto_q, n)        

    @always_comb
    def salida() :
        cociente_o.next = cociente
        resto_o.next = resto_q[m:]

    return instances()
    
#############################################################

def DIVQ_Sec(clk_i, 
             rst_i, 
             ini_i, 
             dividendo_i, 
             divisor_i, 
             div0_o, 
             fin_o, 
             coc_entero_o, 
             coc_frac_o) :
    """Divisor secuencial de numeros enteros no negativos
    con resultado racional. Reset e inicio sincronico 
    
    :Parametros:
        - `clk_i`         : clock
        - `rst_i`         : reset sincronico
        - `ini_i`         : comienzo
        - `dividendo_i`   : dividendo (n bits)
        - `divisor_i`     : divisor (m bits)
        - `div0_o`        : division por 0
        - `fin_o`         : indica la finalizacion de la division
        - `coc_entero_o`  : parte entera del cociente (n o p bits, si se estima el resultado)
        - `coc_frac_o`    : parte fraccionaria del cociente de s bits

    """

    n = len(dividendo_i)
    m = len(divisor_i)
    p = len(coc_entero_o)    #Si se estima el resultado de la div, es mejor no gastar bits (p <= n)
    s = len(coc_frac_o)
    CICLOS = n + s

    resto_q = Signal(intbv(0)[m+1:])             # salida del registro resto 
    cociente = Signal(intbv(0)[p+s:0])

    nucleo = nucleo_division(clk_i, rst_i, ini_i, dividendo_i, divisor_i, div0_o, fin_o, cociente, resto_q, CICLOS)        

    @always_comb
    def salida() :
        coc_entero_o.next = cociente[p+s:s]
        coc_frac_o.next = cociente[s:0]

    return instances()

###########################################
