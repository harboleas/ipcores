    mov r0, 5       # Estado de los leds en r0
    mov [1], r0

espera_boton_abajo :  

    mov r1, [0]      # Guardo en r1 el estado de los botones
    and r1, 1
    jz espera_boton_abajo

    call delay

espera_boton_arriba :  
    mov r1, [0]      # Guardo en r1 el estado de los botones
    and r1, 1
    jz deboun   
    jmp espera_boton_arriba

deboun:

    call delay

    add r0, 1
    mov [1], r0

    jmp espera_boton_abajo

#########################################

delay :

    mov r2, 100
    mov r3, 100

resta :
    sub r3, 1
    jz no_res
    jmp resta

no_res :

    mov r3, 100
    sub r2, 1
    jz fin
    jmp resta

fin :
    ret

    

    
    

  
