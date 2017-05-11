        mov r0, 1
        mov r1, 1
suma5:  add r0, r1  
        mov r2, r0   #intercambia R0 por R1 para que la suma quede en R1 y el anterior en R0
        mov r0, r1
        mov r1, r2
salto : jmp suma5
