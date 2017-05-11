"""
Extrae la informacion del archivo de font, para generar la ROM de caracteres

:Autor: Hugo Arboleas <harboleas@citedef.gob.ar>

"""


archivo_font = open("Lat2-VGA16.psf", "rb")
 
#  Estructura de los archivos PSF1
#      magic[2]  Magic number   0x36, 0x04
#      mode      PSF font mode 
#      charsize  Character size 
#      data      Data de los caractares

magic = archivo_font.read(2)      # Leo el numero magico

if magic != "\x36\x04" :

    print "Error: no es un archivo PSF1"

    archivo_font.close()
 
else :
    
    archivo_font.read(1)      # Descarto el byte de modo

    charsize = ord(archivo_font.read(1))

    archivo_font.read(32*charsize) # Descarto los 32 primeros caracteres que son boludeces

    cant_char = 95  # Cantidad de caracteres para extraer

    font_data = archivo_font.read( cant_char * charsize ) # En estos 95 caracteres estan los numeros, las mayusculas, las minusculas y algunos simbolos

    archivo_font.close()

    archivo_rom = open("rom_font.py", "w")

    texto = "# Este archivo fue generado por extractor_font.py\n\nROM_FONT = (\n"

    for i in range(cant_char) :
        texto = texto + "\n# Caracter : " + chr(32+i) + "\n"

        for j in range(charsize) :
            dato = ord( font_data[ i * charsize + j ] )
            dato_bin = bin( dato )[2:]    # el dato en string binario   
            ceros = 8 - len(dato_bin)     # cantidad de ceros para agregar 
            dato_bin =  "0" * ceros + dato_bin
            if (i == cant_char - 1) and ( j == charsize - 1) :
                texto = texto + (" 0x%.2x )  # " % dato) + dato_bin + "\n"
            else :
                texto = texto + (" 0x%.2x,   # " % dato) + dato_bin + "\n"


    archivo_rom.write(texto)

    archivo_rom.close()

    print "Archivo generado con exito"

