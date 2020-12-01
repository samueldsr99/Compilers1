# Proyecto 1. Compilación 3er Año.

## Grammar Analyser.

### Índice
- Introducción
- Requerimientos
- Uso
- Detalles de Implementación
- TODO

### Introducción
El objetivo del proyecto es diseñar un programa que permita realizar el procesamiento de gramáticas en texto plano.

Los análisis que se realizan dada una gramática como entrada son los siguientes:
- Calcular los conjuntos _Firsts_ y _Follows_.
- Determinar si la gramática es _LL(1)_.
- En caso positivo muestra:
    - Tabla del método predictivo no recursivo.
    - Árbol de derivación para un conjunto de cadenas.
- En caso negativo:
    - Transforma la gramática para eliminar prefijos comunes y recursión izquierda inmediata.
- El análisis anterior además se realiza con los parsers _LR_ y _SLR_. Se muestra una visualización de los autómatas correspndientes en cada caso.
- En caso de que la gramática sea regular:
    - Mostrar autómata que la representa.
    - Mostrar expresión equivalente.
- Se muestra una versión de la gramática sin producciones innecesarias, recursión izquierda y prefijos comunes.

### Requerimientos
¿?
### Uso
Para iniciar la ejecución, una vez cumplidos los requerimientos, se usa el siguiente comando en la carpeta raíz del proyecto.

    streamlit run index2.py

El procesamiento de las gramáticas se realiza sobre una plataforma web. Hay 4 opciones disponibles:

<img src="images/options.png" width="200">

En la primera opcion es posible definir una gramatica insertando terminales, no terminales y producciones. El formato de las producciones es de la siguiente forma:

    E -> T X
    X -> + E | epsilon
    T -> int Y | ( E )
    Y -> * T | epsilon

En **Detalles de la Gramatica** se puede observar la gramática definida, así como la misma gramática simplificada (sin recursión izquierda inmediata, producciones innecesarias y prefijos comunes). Además se puede visualiar **si la gramática es regular** es el autómata finito determinista que reconoce el lenguaje que ella genera.

En el trecer punto, están disponible los _First_ y los _Follows_ calculados para la gramática.

Finalemente, en el apartado de **Parsing**, se puede seleccionar uno de los tipos de pasrers disponibles, _LL(1)_, _LR(1)_ y _SLR(1). Según el parser, y si la gramática puede ser parseada con dicho parser, se puede observar la tabla de parseo y el autómata correspondiente. Además está la opción de parsear una cadena provista con el método escogido.

### Detalles de Implementación
