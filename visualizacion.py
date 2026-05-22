"""
Funciones de salida del programa: informes por consola, narracion y graficos.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from diagnostico import diagnosticar_causa_concreta
from utilidades import (
    arista_ordenada,
    aristas_de_ruta,
    calcular_distancia_ruta,
    generadores_con_mas_sobrante,
    nombre_corto,
    resumen_lista,
    ruta_corta,
    pos_mapa,
)


from matplotlib.patches import Polygon

def dibujar_silueta_espana(ax):
    contorno_espana = [
        # --- COSTA DE GALICIA Y NORTE ---
        (-8.88, 41.89), (-8.87, 42.00), (-8.93, 42.12), (-8.90, 42.20), (-9.00, 42.25),
        (-9.06, 42.34), (-8.95, 42.45), (-9.16, 42.50), (-9.22, 42.58), (-9.29, 42.70),
        (-9.30, 42.85), (-9.28, 42.95), (-9.20, 43.10), (-9.25, 43.20), (-9.13, 43.25),
        (-8.87, 43.25), (-8.75, 43.30), (-8.68, 43.32), (-8.50, 43.34), (-8.43, 43.35),
        (-8.35, 43.43), (-8.32, 43.51), (-8.22, 43.52), (-8.14, 43.54), (-8.00, 43.70),
        (-7.84, 43.72), (-7.70, 43.73), (-7.60, 43.73), (-7.45, 43.68),
        # --- COSTA CANTÁBRICA ---
        (-7.35, 43.60), (-7.15, 43.55), (-6.87, 43.56), (-6.70, 43.55), (-6.55, 43.56),
        (-6.30, 43.57), (-6.06, 43.58), (-5.80, 43.62), (-5.67, 43.60), (-5.50, 43.55),
        (-5.29, 43.48), (-5.05, 43.45), (-4.81, 43.43), (-4.60, 43.40), (-4.34, 43.39),
        (-4.10, 43.42), (-3.92, 43.45), (-3.75, 43.45), (-3.50, 43.45), (-3.30, 43.40),
        (-3.11, 43.42), (-2.95, 43.40), (-2.76, 43.38), (-2.60, 43.35), (-2.42, 43.34),
        (-2.15, 43.32), (-1.96, 43.31), (-1.85, 43.34), (-1.77, 43.35), (-1.74, 43.38),
        # --- PIRINEOS (Frontera con Francia) ---
        (-1.65, 43.30), (-1.46, 43.26), (-1.30, 43.15), (-1.16, 43.11), (-1.00, 43.00),
        (-0.86, 42.92), (-0.70, 42.85), (-0.56, 42.80), (-0.40, 42.82), (-0.26, 42.84),
        (-0.10, 42.80), (0.01, 42.78), (0.15, 42.75), (0.28, 42.75), (0.45, 42.80),
        (0.57, 42.75), (0.70, 42.70), (0.83, 42.66), (0.95, 42.62), (1.10, 42.60),
        (1.25, 42.59), (1.42, 42.58), (1.55, 42.50), (1.71, 42.45), (1.85, 42.42),
        (1.98, 42.40), (2.15, 42.43), (2.29, 42.42), (2.45, 42.45), (2.59, 42.44),
        (2.80, 42.42), (2.95, 42.44), (3.10, 42.46), (3.18, 42.45), (3.25, 42.40),
        (3.32, 42.32),
        # --- COSTA MEDITERRÁNEA NORTE (Cataluña / Valencia) ---
        (3.20, 42.20), (3.17, 42.10), (3.15, 42.00), (3.11, 41.87), (3.00, 41.75),
        (2.89, 41.67), (2.75, 41.55), (2.61, 41.48), (2.45, 41.35), (2.27, 41.26),
        (2.10, 41.20), (1.95, 41.13), (1.80, 41.05), (1.61, 41.00), (1.45, 40.92),
        (1.31, 40.85), (1.15, 40.78), (0.97, 40.71), (0.85, 40.70), (0.83, 40.63),
        (0.75, 40.50), (0.64, 40.40), (0.55, 40.30), (0.42, 40.23), (0.30, 40.10),
        (0.20, 40.03), (0.10, 39.90), (-0.03, 39.81), (-0.10, 39.70), (-0.14, 39.63),
        (-0.22, 39.55), (-0.29, 39.46), (-0.35, 39.35), (-0.38, 39.26), (-0.36, 39.15),
        (-0.33, 39.06), (-0.25, 38.95), (-0.17, 38.86), (-0.05, 38.83), (0.08, 38.82),
        (0.20, 38.78), (0.22, 38.74), (0.15, 38.65), (0.03, 38.56), (-0.10, 38.48),
        (-0.20, 38.38), (-0.35, 38.25), (-0.45, 38.16), (-0.55, 38.00), (-0.66, 37.91),
        # --- COSTA MEDITERRÁNEA SUR (Murcia / Andalucía) ---
        (-0.72, 37.80), (-0.76, 37.74), (-0.88, 37.65), (-1.01, 37.58), (-1.20, 37.50),
        (-1.41, 37.40), (-1.60, 37.33), (-1.77, 37.24), (-1.95, 37.10), (-2.11, 36.96),
        (-2.30, 36.85), (-2.48, 36.75), (-2.65, 36.73), (-2.80, 36.72), (-3.00, 36.74),
        (-3.15, 36.75), (-3.35, 36.74), (-3.52, 36.73), (-3.70, 36.75), (-3.86, 36.76),
        (-4.00, 36.73), (-4.18, 36.71), (-4.35, 36.63), (-4.52, 36.56), (-4.70, 36.50),
        (-4.86, 36.46), (-5.00, 36.38), (-5.16, 36.32), (-5.35, 36.15), (-5.52, 36.05),
        (-5.70, 36.12), (-5.86, 36.19), (-5.98, 36.22), (-6.06, 36.25), (-6.18, 36.30),
        (-6.26, 36.35), (-6.35, 36.50), (-6.43, 36.63), (-6.55, 36.75), (-6.63, 36.83),
        (-6.75, 36.95), (-6.83, 37.03), (-6.95, 37.12), (-7.03, 37.16), (-7.15, 37.18),
        (-7.24, 37.19), (-7.35, 37.21), (-7.40, 37.22),
        # --- FRONTERA INTERIOR CON PORTUGAL (De Sur a Norte) ---
        (-7.41, 37.30), (-7.35, 37.40), (-7.26, 37.48), (-7.15, 37.60), (-7.00, 37.78),
        (-6.98, 37.90), (-7.06, 38.03), (-7.18, 38.15), (-7.26, 38.25), (-7.12, 38.40),
        (-7.00, 38.52), (-7.03, 38.68), (-7.10, 38.81), (-7.00, 39.00), (-6.94, 39.11),
        (-7.05, 39.28), (-7.14, 39.41), (-7.00, 39.58), (-6.86, 39.71), (-6.75, 39.88),
        (-6.64, 40.00), (-6.78, 40.12), (-6.90, 40.23), (-6.82, 40.40), (-6.75, 40.54),
        (-6.85, 40.70), (-6.94, 40.85), (-6.78, 41.00), (-6.63, 41.13), (-6.42, 41.25),
        (-6.25, 41.35), (-6.40, 41.52), (-6.55, 41.68), (-6.70, 41.80), (-6.84, 41.87),
        (-7.05, 41.85), (-7.22, 41.83), (-7.42, 41.84), (-7.62, 41.84), (-7.82, 41.83),
        (-8.02, 41.82), (-8.25, 41.83), (-8.46, 41.84), (-8.65, 41.85)
    ]

    contorno_mapa = [
        pos_mapa(lon, lat)
        for lon, lat in contorno_espana
    ]

    silueta = Polygon(
        contorno_mapa,
        closed=True,
        facecolor="#8fa6b8",
        edgecolor="#263445",
        linewidth=2.2,
        alpha=0.55,
        zorder=0.1
    )

    ax.add_patch(silueta)

def dibujar_dato_bajo_nodo(ax, x, y, texto, color):
    ax.annotate(
        texto,
        xy=(x, y),
        xytext=(0, -20),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=7.2,
        fontweight="bold",
        color=color,
        bbox=dict(
            boxstyle="round,pad=0.18",
            facecolor="#111827",
            edgecolor="none",
            alpha=0.78
        ),
        zorder=5,
        clip_on=False
    )


def narrar_estado_normal(G, estado_normal):
    print("\n" + "=" * 70)
    print("LECTURA DEL FUNCIONAMIENTO NORMAL")
    print("=" * 70)

    # Generador mas cargado y generador con mas margen.
    generador_mas_cargado = None
    porcentaje_mas_alto = -1

    for gen, datos in estado_normal["generadores"].items():
        total = datos["energia_disponible_mw"] + datos["energia_usada_mw"]

        if total > 0:
            porcentaje = datos["energia_usada_mw"] / total * 100
        else:
            porcentaje = 0

        if porcentaje > porcentaje_mas_alto:
            porcentaje_mas_alto = porcentaje
            generador_mas_cargado = gen

    generador_mas_sobrante, datos_sobrante = max(
        estado_normal["generadores"].items(),
        key=lambda item: item[1]["energia_disponible_mw"]
    )

    ciudad_mayor_perdida, datos_perdida = max(
        estado_normal["ciudades"].items(),
        key=lambda item: item[1]["perdida_pct"]
    )

    ciudad_ruta_larga = None
    distancia_mayor = -1

    for ciudad, datos in estado_normal["ciudades"].items():
        ruta = datos.get("ruta", [])

        if ruta:
            distancia = calcular_distancia_ruta(G, ruta)

            if distancia > distancia_mayor:
                distancia_mayor = distancia
                ciudad_ruta_larga = ciudad

    print("\nLa red funciona correctamente: todas las ciudades reciben energia suficiente.")
    print("Aun asi, el sistema puede analizar que partes trabajan mas y que rutas tienen mas perdida.")

    print(f"\nGenerador mas cargado: {nombre_corto(generador_mas_cargado)} ({porcentaje_mas_alto:.1f}% de uso).")
    print(
        f"Generador con mas energia sobrante: {nombre_corto(generador_mas_sobrante)} "
        f"({datos_sobrante['energia_disponible_mw']:.0f} MW disponibles)."
    )
    print(
        f"Ciudad con mayor perdida en su ruta: {ciudad_mayor_perdida} "
        f"({datos_perdida['perdida_pct']:.1f}%)."
    )

    if ciudad_ruta_larga is not None:
        datos_ruta = estado_normal["ciudades"][ciudad_ruta_larga]
        print(
            f"Ruta activa mas larga: {ciudad_ruta_larga}, con {distancia_mayor:.0f} km "
            f"por {ruta_corta(datos_ruta['ruta'])}."
        )

    print("\nEsto ayuda a saber que zonas tienen mas margen y que rutas serian mas delicadas ante un fallo.")


def narrar_fallo_absorbido(estado_impacto, estado_redistribuido, evento):
    print("\nEl sistema ha absorbido el fallo sin dejar ciudades en deficit.")

    if evento.get("lineas_cortadas"):
        print("La linea cortada no era imprescindible o existian rutas alternativas con capacidad suficiente.")

    if evento.get("generadores_afectados"):
        print("La perdida de generacion ha sido compensada por otros generadores con energia sobrante.")

    print("\nGeneradores con mas energia sobrante tras la redistribucion:")
    for gen, datos in generadores_con_mas_sobrante(estado_redistribuido, 3):
        print(f"- {nombre_corto(gen)}: {datos['energia_disponible_mw']:.0f} MW disponibles")


def imprimir_evento(evento):
    print("\n" + "=" * 70)
    print("INFORME DEL SISTEMA")
    print("=" * 70)

    print(f"\nTipo de evento: {evento['tipo'].upper()}")
    print(f"Subtipo: {evento['subtipo']}")
    print(f"Gravedad: {evento['gravedad'].upper()}")
    print(f"\nDescripcion general: {evento['descripcion']}")

    if evento["lineas_cortadas"]:
        print("\nLineas cortadas concretas:")
        for nodo_a, nodo_b in evento["lineas_cortadas"]:
            print(f"- Se ha cortado la linea {nombre_corto(nodo_a)} <-> {nombre_corto(nodo_b)}.")

    if evento["generadores_afectados"]:
        print("\nGeneradores afectados concretos:")
        for dato in evento["generadores_afectados"]:
            print(
                f"- {nombre_corto(dato['generador'])} pasa de "
                f"{dato['energia_original']:.0f} MW a {dato['energia_nueva']:.0f} MW "
                f"({dato['reduccion_pct']}% de reduccion)."
            )

    if evento["ciudades_potencialmente_afectadas"]:
        print("\nCiudades que dependian inicialmente de los elementos afectados:")
        print(resumen_lista(evento["ciudades_potencialmente_afectadas"]))
    else:
        print("\nNo se detectan ciudades directamente dependientes del elemento afectado en las rutas iniciales.")

    print("\nPrimero se mostrara el impacto inicial. Despues el sistema intentara redistribuir la energia con Dijkstra.")


def narrar_impacto_inicial(estado_impacto):
    print("\n" + "=" * 70)
    print("IMPACTO INICIAL DEL FALLO")
    print("=" * 70)

    afectadas = []

    for ciudad, datos in estado_impacto["ciudades"].items():
        if not datos["suministrada"]:
            afectadas.append(ciudad)

    if not afectadas:
        print("\nEl impacto inicial no deja ciudades sin suministro.")
        print("La red mantiene el servicio antes incluso de redistribuir la energia.")
        return afectadas

    print("\nCiudades afectadas antes de redistribuir energia:")

    for ciudad in afectadas:
        datos = estado_impacto["ciudades"][ciudad]
        print(
            f"- {ciudad}: recibe {datos['energia_recibida_mw']:.0f}/"
            f"{datos['demanda_min_mw']} MW. Motivo: {datos['motivo']}"
        )

    return afectadas


def narrar_redistribucion(estado_normal, estado_impacto, estado_redistribuido, evento, G_fallo):
    print("\n" + "=" * 70)
    print("REDISTRIBUCION AUTOMATICA")
    print("=" * 70)

    recuperadas = []
    siguen_afectadas = []
    cambios_ruta = []

    for ciudad, datos_finales in estado_redistribuido["ciudades"].items():
        datos_impacto = estado_impacto["ciudades"][ciudad]
        datos_normales = estado_normal["ciudades"][ciudad]

        if not datos_impacto["suministrada"] and datos_finales["suministrada"]:
            recuperadas.append(ciudad)

        if not datos_finales["suministrada"]:
            siguen_afectadas.append(ciudad)

        if datos_normales.get("ruta", []) != datos_finales.get("ruta", []) and datos_finales.get("ruta", []):
            cambios_ruta.append(ciudad)

    if recuperadas:
        print("\nCiudades recuperadas gracias a la redistribucion:")
        for ciudad in recuperadas:
            datos = estado_redistribuido["ciudades"][ciudad]
            print(
                f"- {ciudad}: vuelve a recibir energia por {ruta_corta(datos['ruta'])} "
                f"con una perdida del {datos['perdida_pct']:.1f}%."
            )
    else:
        print("\nNo habia ciudades que recuperar o ninguna ciudad ha podido recuperarse por completo.")

    if cambios_ruta:
        print("\nRutas nuevas o modificadas por Dijkstra:")
        for ciudad in cambios_ruta:
            antes = ruta_corta(estado_normal["ciudades"][ciudad].get("ruta", []))
            despues = ruta_corta(estado_redistribuido["ciudades"][ciudad].get("ruta", []))
            print(f"- {ciudad}: antes {antes}; ahora {despues}.")

    if siguen_afectadas:
        print("\nCiudades que siguen con deficit tras la redistribucion:")
        for ciudad in siguen_afectadas:
            datos = estado_redistribuido["ciudades"][ciudad]
            causa = diagnosticar_causa_concreta(G_fallo, estado_redistribuido, ciudad, evento)
            print(
                f"- {ciudad}: recibe {datos['energia_recibida_mw']:.0f}/"
                f"{datos['demanda_min_mw']} MW. Motivo concreto: {causa}."
            )
    else:
        print("\nResultado final: la red consigue mantener todas las ciudades suministradas.")

        if not recuperadas and not cambios_ruta:
            narrar_fallo_absorbido(estado_impacto, estado_redistribuido, evento)
        elif evento["gravedad"] == "leve":
            print("Al ser un fallo leve, la red ha tenido margen suficiente para compensarlo sin cortes finales.")
            narrar_fallo_absorbido(estado_impacto, estado_redistribuido, evento)


def visualizar_red(G, estado, titulo="Red electrica", evento=None, aristas_destacadas=None, rutas_solucion=None):
    if aristas_destacadas is None:
        aristas_destacadas = set()

    if rutas_solucion is None:
        rutas_solucion = {}

    aristas_solucion = set()
    ciudades_solucion = set(rutas_solucion.keys())

    for rutas in rutas_solucion.values():
        for ruta in rutas:
            aristas_solucion.update(aristas_de_ruta(ruta))

    fig, ax = plt.subplots(1, 1, figsize=(16, 9.5))
    fig.patch.set_facecolor("#1a1a2e")

    fig.subplots_adjust(left=0.20, right=0.985, top=0.91, bottom=0.06)

    ax.set_facecolor("#16213e")
    ax.set_title(titulo, color="white", fontsize=14, fontweight="bold", pad=15)

    # Se dibuja antes que nodos y aristas para que quede por debajo del grafo.
    dibujar_silueta_espana(ax)

    pos = nx.get_node_attributes(G, "pos")

    generadores_afectados = set()
    lineas_cortadas = []

    if evento is not None:
        generadores_afectados = {
            dato["generador"]
            for dato in evento.get("generadores_afectados", [])
        }
        lineas_cortadas = evento.get("lineas_cortadas", [])

    generadores = [
        n for n, d in G.nodes(data=True)
        if d["tipo"] == "generador" and n not in generadores_afectados
    ]

    generadores_fallo = [
        n for n in generadores_afectados
        if n in G.nodes
    ]

    ciudades_ok = [
        c for c, d in estado["ciudades"].items()
        if d["suministrada"] and c in G.nodes
    ]

    ciudades_ko = [
        c for c, d in estado["ciudades"].items()
        if not d["suministrada"] and c in G.nodes
    ]

    aristas_alta = [
        (u, v) for u, v, d in G.edges(data=True)
        if d["tipo"] == "alta_tension"
    ]

    aristas_normales = [
        (u, v) for u, v, d in G.edges(data=True)
        if d["tipo"] == "normal"
    ]

    rutas_activas = set()

    for datos in estado["ciudades"].values():
        ruta = datos.get("ruta", [])

        for i in range(len(ruta) - 1):
            rutas_activas.add(arista_ordenada(ruta[i], ruta[i + 1]))

    aristas_alta_activas = [
        (u, v) for u, v in aristas_alta
        if arista_ordenada(u, v) in rutas_activas
        and arista_ordenada(u, v) not in aristas_destacadas
        and arista_ordenada(u, v) not in aristas_solucion
    ]

    aristas_alta_inactivas = [
        (u, v) for u, v in aristas_alta
        if arista_ordenada(u, v) not in rutas_activas
    ]

    aristas_normales_activas = [
        (u, v) for u, v in aristas_normales
        if arista_ordenada(u, v) in rutas_activas
        and arista_ordenada(u, v) not in aristas_destacadas
        and arista_ordenada(u, v) not in aristas_solucion
    ]

    aristas_normales_inactivas = [
        (u, v) for u, v in aristas_normales
        if arista_ordenada(u, v) not in rutas_activas
    ]

    aristas_destacadas_existentes = [
        (u, v) for u, v in G.edges()
        if arista_ordenada(u, v) in aristas_destacadas
    ]

    aristas_solucion_existentes = [
        (u, v) for u, v in G.edges()
        if arista_ordenada(u, v) in aristas_solucion
    ]

    # Dibujar aristas normales de fondo.
    nx.draw_networkx_edges(
        G, pos,
        edgelist=aristas_alta_inactivas,
        width=1.5,
        edge_color="#2a6b8c",
        alpha=0.4,
        ax=ax
    )

    nx.draw_networkx_edges(
        G, pos,
        edgelist=aristas_normales_inactivas,
        width=1.0,
        edge_color="#404060",
        alpha=0.4,
        ax=ax
    )

    # Dibujar rutas activas normales.
    nx.draw_networkx_edges(
        G, pos,
        edgelist=aristas_alta_activas,
        width=3.5,
        edge_color="#00d4ff",
        alpha=0.9,
        ax=ax
    )

    nx.draw_networkx_edges(
        G, pos,
        edgelist=aristas_normales_activas,
        width=2.0,
        edge_color="#7ecfb0",
        alpha=0.8,
        ax=ax
    )

    # Dibujar rutas nuevas tras redistribucion por encima.
    if aristas_destacadas_existentes:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=aristas_destacadas_existentes,
            width=5.0,
            edge_color="#ffd166",
            alpha=1.0,
            ax=ax
        )

    if aristas_solucion_existentes:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=aristas_solucion_existentes,
            width=4.0,
            edge_color="#06d6a0",
            style="dashed",
            alpha=1.0,
            ax=ax
        )

    for nodo_a, nodo_b in lineas_cortadas:
        if nodo_a in pos and nodo_b in pos:
            x1, y1 = pos[nodo_a]
            x2, y2 = pos[nodo_b]
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="#e63946",
                linewidth=3,
                linestyle="--",
                alpha=0.95,
                zorder=1
            )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=generadores,
        node_color="#f4a261",
        node_size=700,
        ax=ax
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=generadores_fallo,
        node_color="#e63946",
        node_size=760,
        ax=ax
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=ciudades_ok,
        node_color="#2ec4b6",
        node_size=500,
        ax=ax
    )

    nx.draw_networkx_nodes(
        G, pos,
        nodelist=ciudades_ko,
        node_color="#e63946",
        node_size=500,
        ax=ax
    )

    # Borde especial para ciudades que siguen en deficit y tienen solucion propuesta.
    ciudades_deficit_con_solucion = [
        ciudad for ciudad in ciudades_ko
        if ciudad in ciudades_solucion
    ]

    if ciudades_deficit_con_solucion:
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=ciudades_deficit_con_solucion,
            node_color="none",
            edgecolors="#ffd166",
            linewidths=3.0,
            node_size=700,
            ax=ax
        )

    # Etiquetas de generadores y ciudades.
    etiquetas_gen = {
        n: nombre_corto(n).replace(" ", "\n")
        for n in generadores + generadores_fallo
    }

    etiquetas_ciudades = {
        n: n
        for n in ciudades_ok + ciudades_ko
        if n in G.nodes
    }

    nx.draw_networkx_labels(
        G, pos,
        labels=etiquetas_gen,
        font_size=7,
        font_color="white",
        font_weight="bold",
        ax=ax
    )

    nx.draw_networkx_labels(
        G, pos,
        labels=etiquetas_ciudades,
        font_size=8,
        font_color="white",
        ax=ax
    )

    
    # Mostrar carga usada/total debajo de cada generador.
    for generador, datos in estado["generadores"].items():
        if generador in pos:
            x, y = pos[generador]

            usada = datos["energia_usada_mw"]
            total = datos["energia_usada_mw"] + datos["energia_disponible_mw"]

            if generador in generadores_afectados:
                color_texto = "#e63946"
            else:
                color_texto = "#f4a261"

            dibujar_dato_bajo_nodo(
                ax,
                x,
                y,
                f"{usada:.0f}/{total:.0f} MW",
                color_texto
            )


    # Mostrar energía recibida/demanda debajo de cada ciudad.
    for ciudad, datos in estado["ciudades"].items():
        if ciudad in pos:
            x, y = pos[ciudad]

            recibida = datos["energia_recibida_mw"]
            demanda = datos["demanda_min_mw"]

            if datos["suministrada"]:
                color_texto = "#2ec4b6"
            else:
                color_texto = "#e63946"

            dibujar_dato_bajo_nodo(
                ax,
                x,
                y,
                f"{recibida:.0f}/{demanda} MW",
                color_texto
            )


    leyenda = [
        mpatches.Patch(color="#f4a261", label="Generador"),
        mpatches.Patch(color="#2ec4b6", label="Ciudad suministrada"),
        mpatches.Patch(color="#e63946", label="Ciudad/generador afectado"),
        Line2D([0], [0], color="#00d4ff", lw=3, label="Alta tension activa"),
        Line2D([0], [0], color="#7ecfb0", lw=3, label="Linea normal activa"),
        Line2D([0], [0], color="#404060", lw=2, label="Linea inactiva"),
    ]

    if aristas_destacadas_existentes:
        leyenda.append(Line2D([0], [0], color="#ffd166", lw=5, label="Ruta nueva tras redistribucion"))

    if aristas_solucion_existentes:
        leyenda.append(Line2D([0], [0], color="#06d6a0", lw=4, linestyle="--", label="Ruta solucion propuesta"))

    if ciudades_deficit_con_solucion:
        leyenda.append(Line2D([0], [0], marker="o", color="w", markerfacecolor="#e63946", markeredgecolor="#ffd166", markersize=10, label="Ciudad en deficit con solucion"))

    if lineas_cortadas:
        leyenda.append(Line2D([0], [0], color="#e63946", lw=3, linestyle="--", label="Linea cortada"))

    # Explicación adicional dentro de la leyenda.
    leyenda.append(
        Line2D(
            [0],
            [0],
            color="none",
            label="Ciudad: recibida/demanda MW"
        )
    )

    leyenda.append(
        Line2D(
            [0],
            [0],
            color="none",
            label="Generador: usada/total MW"
        )
    )

    fig.legend(
        handles=leyenda,
        loc="lower left",
        bbox_to_anchor=(0.015, 0.115),
        fontsize=9,
        title="Leyenda del sistema",
        title_fontsize=10,
        facecolor="#111827",
        edgecolor="#7a8497",
        labelcolor="white",
        framealpha=0.96,
        borderpad=1.1,
        labelspacing=0.8,
        handlelength=2.8
    )

    ax.set_xlim(0.04, 0.98)
    ax.set_ylim(0.05, 0.86)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    plt.show()


def imprimir_informe(estado, titulo="ESTADO DE LA RED"):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)

    print("\nGENERADORES:")
    print(f"{'Generador':<30} {'Disponible':>12} {'Usado':>10} {'% Uso':>8}")
    print("-" * 65)

    for gen, datos in estado["generadores"].items():

        total = datos["energia_disponible_mw"] + datos["energia_usada_mw"]

        if total > 0:
            porcentaje_uso = datos["energia_usada_mw"] / total * 100
        else:
            porcentaje_uso = 0

        print(
            f"{nombre_corto(gen):<30} "
            f"{datos['energia_disponible_mw']:>10.0f} MW "
            f"{datos['energia_usada_mw']:>8.0f} MW "
            f"{porcentaje_uso:>7.1f}%"
        )

    print("\nCIUDADES:")
    print(
        f"{'Ciudad':<14} "
        f"{'Demanda':>9} "
        f"{'Recibida':>10} "
        f"{'Perdida':>9} "
        f"{'Estado':>12} "
        f"Ruta"
    )
    print("-" * 95)

    for ciudad, datos in estado["ciudades"].items():

        if datos["suministrada"]:
            estado_str = "OK"
        else:
            estado_str = "DEFICIT"

        print(
            f"{ciudad:<14} "
            f"{datos['demanda_min_mw']:>7} MW "
            f"{datos['energia_recibida_mw']:>8.0f} MW "
            f"{datos['perdida_pct']:>7.1f}% "
            f"{estado_str:>12} "
            f"{ruta_corta(datos['ruta'])}"
        )

    ciudades_ok = sum(
        1 for datos in estado["ciudades"].values()
        if datos["suministrada"]
    )

    total_ciudades = len(estado["ciudades"])

    print(f"\nRESUMEN: {ciudades_ok}/{total_ciudades} ciudades suministradas correctamente")

    if ciudades_ok < total_ciudades:
        print(f"Hay {total_ciudades - ciudades_ok} ciudad(es) con deficit energetico.")
