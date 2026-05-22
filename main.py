"""
Punto de entrada del simulador de red electrica.

Ejecuta el escenario completo usando los modulos del proyecto.
"""

import random

from diagnostico import diagnosticar_red, proponer_solucion
from distribucion import (
    comparar_distribucion_suboptima_vs_dijkstra,
    distribuir_energia,
    distribuir_energia_suboptima,
)
from fallos import (
    analizar_uso_aristas,
    crear_estado_impacto_inicial,
    generar_apagon_nacional_variable,
    generar_fallo_impactante,
)
from red import construir_red, inicializar_estado
from utilidades import calcular_aristas_nuevas
from visualizacion import (
    imprimir_evento,
    imprimir_informe,
    narrar_estado_normal,
    narrar_impacto_inicial,
    narrar_redistribucion,
    visualizar_red,
)


def ejecutar_evento_con_redistribucion(G, estado_normal, G_evento, evento, titulo_base):
    imprimir_evento(evento)

    estado_impacto = crear_estado_impacto_inicial(estado_normal, evento)
    narrar_impacto_inicial(estado_impacto)

    imprimir_informe(
        estado_impacto,
        "ESTADO JUSTO DESPUES DEL FALLO, ANTES DE REDISTRIBUIR"
    )

    visualizar_red(
        G_evento,
        estado_impacto,
        f"{titulo_base} - impacto inicial",
        evento
    )

    print("\nEl sistema recalcula rutas usando Dijkstra y prioridad a generadores cercanos...")

    estado_redistribuido = inicializar_estado(G_evento)
    estado_redistribuido = distribuir_energia(G_evento, estado_redistribuido)

    aristas_nuevas = calcular_aristas_nuevas(estado_impacto, estado_redistribuido)

    narrar_redistribucion(
        estado_normal,
        estado_impacto,
        estado_redistribuido,
        evento,
        G_evento
    )

    imprimir_informe(
        estado_redistribuido,
        "ESTADO TRAS LA REDISTRIBUCION"
    )

    afectadas = diagnosticar_red(
        estado_normal,
        estado_redistribuido,
        G_evento,
        evento
    )

    rutas_solucion = proponer_solucion(
        G_evento,
        estado_redistribuido,
        afectadas
    )

    visualizar_red(
        G_evento,
        estado_redistribuido,
        f"{titulo_base} - red redistribuida y solucion propuesta",
        evento,
        aristas_nuevas,
        rutas_solucion
    )


if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("SIMULADOR DE RED ELECTRICA ESPAÑOLA SIMPLIFICADA")
    print("=" * 70)

    # Creamos la red.
    G = construir_red()

    print("\nRed creada correctamente.")
    print(f"Nodos: {G.number_of_nodes()}")
    print(f"Aristas: {G.number_of_edges()}")

    # Calculamos primero dos versiones del estado normal:
    # 1) una distribucion suboptima por distancia,
    # 2) la distribucion optimizada con Dijkstra por perdida energetica.
    estado_suboptimo = inicializar_estado(G)
    estado_suboptimo = distribuir_energia_suboptima(G, estado_suboptimo)

    estado_normal = inicializar_estado(G)
    estado_normal = distribuir_energia(G, estado_normal)

    # El estado normal se muestra siempre porque es la referencia para entender
    # cualquier fallo o apagon posterior.
    print("\nLa red se analiza primero en funcionamiento normal.")
    print("Se compara una distribucion suboptima con la distribucion optimizada por Dijkstra.")

    comparar_distribucion_suboptima_vs_dijkstra(G, estado_suboptimo, estado_normal)

    imprimir_informe(
        estado_normal,
        "ESTADO NORMAL DE LA RED OPTIMIZADO CON DIJKSTRA"
    )

    narrar_estado_normal(G, estado_normal)

    visualizar_red(
        G,
        estado_normal,
        "Red electrica - estado normal optimizado"
    )

    # Calculamos una sola vez el uso de aristas en el estado normal.
    # Este analisis se reutiliza para fallos y apagones, evitando repetir trabajo.
    analisis_aristas_normal = analizar_uso_aristas(estado_normal)

    # Despues del estado base, el programa elige el tipo de incidente.
    # Ya no decide entre normal/fallo/apagon porque el normal se muestra siempre.
    escenario = random.choices(
        ["fallo", "apagon"],
        weights=[60, 40]
    )[0]

    print("\nIncidente elegido por el programa:", escenario.upper())


    # CASO 1: FALLO VARIADO E IMPACTANTE
    if escenario == "fallo":

        print("\nSe va a simular un fallo variable en la red.")
        print("El fallo puede ser leve, moderado o critico.")

        G_fallo, evento = generar_fallo_impactante(G, estado_normal, analisis_aristas_normal)

        ejecutar_evento_con_redistribucion(
            G,
            estado_normal,
            G_fallo,
            evento,
            "Red electrica - fallo variable"
        )

    
    # CASO 2: APAGON NACIONAL VARIABLE
    elif escenario == "apagon":

        print("\nSe va a simular un apagon nacional variable.")
        print("Puede ser una linea critica, un apagon regional, una caida de generador o un fallo combinado.")

        G_apagon, evento = generar_apagon_nacional_variable(G, estado_normal, analisis_aristas_normal)

        ejecutar_evento_con_redistribucion(
            G,
            estado_normal,
            G_apagon,
            evento,
            "Red electrica - apagon nacional variable"
        )

    print("\n" + "=" * 70)
    print("SIMULACION FINALIZADA")
    print("=" * 70)    