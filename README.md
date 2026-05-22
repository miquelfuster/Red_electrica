# Red Eléctrica Española Simplificada

Proyecto en Python que simula una red eléctrica simplificada mediante grafos.

El programa representa una red formada por generadores, ciudades y líneas de transmisión. A partir de esa red, calcula la distribución de energía, simula fallos o apagones y muestra los resultados tanto por terminal como mediante una visualización gráfica.

---

## Librerías necesarias

El proyecto utiliza las siguientes librerías:

```text
networkx
matplotlib
```

---

## Ejecución

Para ejecutar el programa, hay que abrir una terminal en la carpeta del proyecto y ejecutar:

```bash
python main.py
```

El archivo que debe ejecutarse es siempre:

```text
main.py
```

---

## Qué muestra el programa

Al ejecutar el programa se muestran dos tipos de salida:

1. Información por terminal.
2. Visualización gráfica de la red.

---

## Salida por terminal

La terminal muestra una explicación paso a paso de lo que ocurre en la simulación.

Primero se crea la red eléctrica y se muestra información general, como el número de nodos y líneas.

Después se calcula el estado normal de la red, indicando cómo se distribuye la energía desde los generadores hasta las ciudades.

También se comparan dos formas de distribución:

- Una distribución subóptima.
- Una distribución optimizada mediante Dijkstra.

Más adelante, el programa genera un fallo o apagón y muestra:

- El tipo de incidente.
- La gravedad del fallo.
- Las líneas o generadores afectados.
- Las ciudades que podrían verse afectadas.
- El impacto inicial antes de redistribuir la energía.
- El resultado después de recalcular las rutas.
- El diagnóstico final de la red.
- Posibles soluciones si alguna ciudad queda sin energía suficiente.

---

## Visualización gráfica

El programa abre ventanas gráficas con una representación de la red eléctrica sobre una silueta de España.

En el mapa aparecen:

- Generadores.
- Ciudades.
- Líneas de transmisión.
- Rutas activas de suministro.
- Líneas afectadas por fallos, si las hay.
- Nuevas rutas tras la redistribución.
- Posibles rutas de solución.

Debajo de cada ciudad o generador se muestran datos relacionados con la energía recibida, usada o disponible.

Para que el programa continúe, puede ser necesario cerrar la ventana gráfica que aparece en pantalla.

---

## Estructura del proyecto

```text
Red_electrica/
│
├── main.py
├── red.py
├── distribucion.py
├── fallos.py
├── diagnostico.py
├── visualizacion.py
├── utilidades.py
└── README.md
```

---

## Archivos principales

- `main.py`: ejecuta el programa y coordina la simulación.
- `red.py`: crea la red eléctrica con sus ciudades, generadores y líneas.
- `distribucion.py`: calcula la distribución de energía.
- `fallos.py`: genera fallos y apagones.
- `diagnostico.py`: analiza las causas de los problemas tras un fallo.
- `visualizacion.py`: muestra la información por terminal y genera los gráficos.
- `utilidades.py`: contiene funciones auxiliares usadas por varios módulos.

---

## Nota

Este proyecto es una simulacións implificada. No representa de forma exacta la red eléctrica real de España.