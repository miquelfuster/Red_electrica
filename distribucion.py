"""
Algoritmos de distribucion energetica.

Incluye la distribucion optimizada con Dijkstra y la comparacion con un metodo suboptimo.
"""

import networkx as nx

from utilidades import calcular_distancia_ruta, ruta_corta


def calcular_perdida_ruta(G, ruta):
    perdida_total = 0.0

    for i in range(len(ruta) - 1):
        nodo_a = ruta[i]
        nodo_b = ruta[i + 1]

        datos_arista = G[nodo_a][nodo_b]

        perdida_tramo = (
            datos_arista["distancia_km"]
            * datos_arista["coeficiente"]
            * 100
        )

        perdida_total += perdida_tramo

    return min(perdida_total, 80.0)


def obtener_clave_arista(nodo_a, nodo_b):
    return tuple(sorted((nodo_a, nodo_b)))


def registrar_carga_ruta(ruta, energia_a_enviar, carga_aristas):

    for i in range(len(ruta) - 1):
        nodo_a = ruta[i]
        nodo_b = ruta[i + 1]

        clave = obtener_clave_arista(nodo_a, nodo_b)

        if clave not in carga_aristas:
            carga_aristas[clave] = 0

        carga_aristas[clave] += energia_a_enviar


def ruta_soporta_energia(G, ruta, energia_a_enviar, carga_aristas):
    for i in range(len(ruta) - 1):
        nodo_a = ruta[i]
        nodo_b = ruta[i + 1]

        capacidad = G[nodo_a][nodo_b]["capacidad_max_mw"]

        clave = obtener_clave_arista(nodo_a, nodo_b)
        carga_actual = carga_aristas.get(clave, 0)

        if carga_actual + energia_a_enviar > capacidad:
            return False

    return True


def asignar_suministro(estado, ciudad, generador, ruta, perdida_pct, energia_a_enviar):
    demanda = estado["ciudades"][ciudad]["demanda_min_mw"]
    factor_perdida = perdida_pct / 100.0
    energia_recibida = energia_a_enviar * (1 - factor_perdida)

    estado["ciudades"][ciudad]["energia_recibida_mw"] = round(energia_recibida, 1)
    estado["ciudades"][ciudad]["suministrada"] = energia_recibida >= demanda * 0.98
    estado["ciudades"][ciudad]["generador_asignado"] = generador
    estado["ciudades"][ciudad]["ruta"] = ruta
    estado["ciudades"][ciudad]["perdida_pct"] = round(perdida_pct, 1)
    estado["ciudades"][ciudad]["motivo"] = "suministro calculado con Dijkstra"

    energia_enviada_redondeada = round(energia_a_enviar, 1)

    estado["generadores"][generador]["energia_usada_mw"] += energia_enviada_redondeada
    estado["generadores"][generador]["energia_disponible_mw"] = max(
        0.0,
        estado["generadores"][generador]["energia_disponible_mw"] - energia_enviada_redondeada
    )


def distribuir_energia(G, estado):
    carga_aristas = {}

    # FASE 1: ciudades con generador conectado directamente
    for ciudad in estado["ciudades"]:

        demanda = estado["ciudades"][ciudad]["demanda_min_mw"]

        mejor_gen = None
        mejor_ruta = None
        mejor_perdida = float("inf")
        mejor_energia_a_enviar = 0

        vecinos = list(G.neighbors(ciudad))

        for gen in vecinos:

            if gen not in estado["generadores"]:
                continue

            ruta = [gen, ciudad]

            perdida_pct = calcular_perdida_ruta(G, ruta)
            factor_perdida = perdida_pct / 100.0

            energia_a_enviar = demanda / max(1 - factor_perdida, 0.05)
            disponible = estado["generadores"][gen]["energia_disponible_mw"]

            if not ruta_soporta_energia(G, ruta, energia_a_enviar, carga_aristas):
                continue

            if disponible >= energia_a_enviar and perdida_pct < mejor_perdida:
                mejor_gen = gen
                mejor_ruta = ruta
                mejor_perdida = perdida_pct
                mejor_energia_a_enviar = energia_a_enviar

        if mejor_gen is not None:
            asignar_suministro(
                estado,
                ciudad,
                mejor_gen,
                mejor_ruta,
                mejor_perdida,
                mejor_energia_a_enviar
            )
            
            registrar_carga_ruta(mejor_ruta, mejor_energia_a_enviar, carga_aristas)

            estado["ciudades"][ciudad]["motivo"] = "suministro local desde generador cercano"


    # FASE 2: resto de ciudades usando Dijkstra
    for ciudad in estado["ciudades"]:

        if estado["ciudades"][ciudad]["suministrada"]:
            continue

        demanda = estado["ciudades"][ciudad]["demanda_min_mw"]

        mejor_gen = None
        mejor_ruta = None
        mejor_perdida = float("inf")
        mejor_energia_a_enviar = 0

        for gen in estado["generadores"]:

            try:
                ruta = nx.dijkstra_path(G, gen, ciudad, weight="peso")
                perdida_pct = calcular_perdida_ruta(G, ruta)

                factor_perdida = perdida_pct / 100.0
                energia_a_enviar = demanda / max(1 - factor_perdida, 0.05)

                disponible = estado["generadores"][gen]["energia_disponible_mw"]

                if not ruta_soporta_energia(G, ruta, energia_a_enviar, carga_aristas):
                    continue

                if disponible >= energia_a_enviar and perdida_pct < mejor_perdida:
                    mejor_gen = gen
                    mejor_ruta = ruta
                    mejor_perdida = perdida_pct
                    mejor_energia_a_enviar = energia_a_enviar

            except nx.NetworkXNoPath:
                continue

        if mejor_gen is not None:
            asignar_suministro(
                estado,
                ciudad,
                mejor_gen,
                mejor_ruta,
                mejor_perdida,
                mejor_energia_a_enviar
            )

            registrar_carga_ruta(mejor_ruta, mejor_energia_a_enviar, carga_aristas)

        else:
            estado["ciudades"][ciudad]["motivo"] = "sin generador o ruta viable"

    return estado


def distribuir_energia_suboptima(G, estado):
    carga_aristas = {}

    for ciudad in estado["ciudades"]:

        demanda = estado["ciudades"][ciudad]["demanda_min_mw"]

        mejor_gen = None
        mejor_ruta = None
        mejor_distancia = float("inf")
        mejor_perdida = 0
        mejor_energia_a_enviar = 0

        for gen in estado["generadores"]:

            try:
                # Metodo suboptimo: se minimizan kilometros, no perdida energetica.
                ruta = nx.dijkstra_path(G, gen, ciudad, weight="distancia_km")
                distancia = calcular_distancia_ruta(G, ruta)
                perdida_pct = calcular_perdida_ruta(G, ruta)

                factor_perdida = perdida_pct / 100.0
                energia_a_enviar = demanda / max(1 - factor_perdida, 0.05)
                disponible = estado["generadores"][gen]["energia_disponible_mw"]

                if not ruta_soporta_energia(G, ruta, energia_a_enviar, carga_aristas):
                    continue

                if disponible >= energia_a_enviar and distancia < mejor_distancia:
                    mejor_gen = gen
                    mejor_ruta = ruta
                    mejor_distancia = distancia
                    mejor_perdida = perdida_pct
                    mejor_energia_a_enviar = energia_a_enviar

            except nx.NetworkXNoPath:
                continue
            except nx.NodeNotFound:
                continue

        if mejor_gen is not None:
            asignar_suministro(
                estado,
                ciudad,
                mejor_gen,
                mejor_ruta,
                mejor_perdida,
                mejor_energia_a_enviar
            )

            registrar_carga_ruta(mejor_ruta, mejor_energia_a_enviar, carga_aristas)

            estado["ciudades"][ciudad]["motivo"] = "distribucion suboptima por ruta mas corta en km"
        else:
            estado["ciudades"][ciudad]["motivo"] = "sin ruta viable en el metodo suboptimo"

    return estado


def calcular_metricas_estado(estado):
    ciudades = estado["ciudades"]
    generadores = estado["generadores"]

    ciudades_ok = sum(1 for datos in ciudades.values() if datos["suministrada"])
    total_ciudades = len(ciudades)

    perdidas = [
        datos["perdida_pct"]
        for datos in ciudades.values()
        if datos["suministrada"] and datos.get("ruta")
    ]

    if perdidas:
        perdida_media = sum(perdidas) / len(perdidas)
        perdida_maxima = max(perdidas)
    else:
        perdida_media = 0
        perdida_maxima = 0

    energia_usada = sum(datos["energia_usada_mw"] for datos in generadores.values())
    energia_sobrante = sum(datos["energia_disponible_mw"] for datos in generadores.values())

    return {
        "ciudades_ok": ciudades_ok,
        "total_ciudades": total_ciudades,
        "perdida_media": perdida_media,
        "perdida_maxima": perdida_maxima,
        "energia_usada": energia_usada,
        "energia_sobrante": energia_sobrante
    }


def comparar_distribucion_suboptima_vs_dijkstra(G, estado_suboptimo, estado_dijkstra):
    print("\n" + "=" * 70)
    print("COMPARACION: DISTRIBUCION SUBOPTIMA VS DIJKSTRA")
    print("=" * 70)

    print("\nMetodo suboptimo: busca rutas fisicamente mas cortas en kilometros.")
    print("Metodo optimizado: usa Dijkstra minimizando la perdida energetica de cada linea.")

    m_sub = calcular_metricas_estado(estado_suboptimo)
    m_dij = calcular_metricas_estado(estado_dijkstra)

    print("\nResumen general:")
    print(
        f"- Suboptimo: {m_sub['ciudades_ok']}/{m_sub['total_ciudades']} ciudades suministradas, "
        f"perdida media {m_sub['perdida_media']:.2f}%, energia usada {m_sub['energia_usada']:.1f} MW."
    )
    print(
        f"- Dijkstra:  {m_dij['ciudades_ok']}/{m_dij['total_ciudades']} ciudades suministradas, "
        f"perdida media {m_dij['perdida_media']:.2f}%, energia usada {m_dij['energia_usada']:.1f} MW."
    )

    ahorro_energia = m_sub["energia_usada"] - m_dij["energia_usada"]
    mejora_perdida = m_sub["perdida_media"] - m_dij["perdida_media"]

    if ahorro_energia > 0:
        print(f"\nDijkstra necesita {ahorro_energia:.1f} MW menos para cubrir la red.")
    elif ahorro_energia < 0:
        print(f"\nEn este caso Dijkstra usa {-ahorro_energia:.1f} MW mas, pero prioriza menor perdida por ruta.")
    else:
        print("\nAmbos metodos usan practicamente la misma energia total.")

    if mejora_perdida > 0:
        print(f"La perdida media baja {mejora_perdida:.2f} puntos porcentuales con Dijkstra.")

    diferencias = []

    for ciudad in estado_dijkstra["ciudades"]:
        datos_sub = estado_suboptimo["ciudades"][ciudad]
        datos_dij = estado_dijkstra["ciudades"][ciudad]

        ruta_sub = datos_sub.get("ruta", [])
        ruta_dij = datos_dij.get("ruta", [])

        if ruta_sub != ruta_dij:
            mejora = datos_sub["perdida_pct"] - datos_dij["perdida_pct"]
            diferencias.append((mejora, ciudad, ruta_sub, ruta_dij, datos_sub, datos_dij))

    diferencias.sort(reverse=True, key=lambda item: item[0])

    if diferencias:
        print("\nCiudades donde Dijkstra cambia la ruta respecto al metodo suboptimo:")
        for mejora, ciudad, ruta_sub, ruta_dij, datos_sub, datos_dij in diferencias[:5]:
            print(f"\n- {ciudad}")
            print(f"  Suboptimo: {ruta_corta(ruta_sub)} | perdida {datos_sub['perdida_pct']:.1f}%")
            print(f"  Dijkstra:  {ruta_corta(ruta_dij)} | perdida {datos_dij['perdida_pct']:.1f}%")

            if mejora > 0:
                print(f"  Mejora aproximada: {mejora:.1f} puntos porcentuales menos de perdida.")
            elif mejora < 0:
                print("  La ruta cambia por disponibilidad/capacidad, aunque la perdida no mejore directamente.")
            else:
                print("  La ruta cambia, pero la perdida es practicamente igual.")
    else:
        print("\nEn esta red concreta ambos metodos eligen las mismas rutas activas.")
        print("Aun asi, Dijkstra queda justificado porque garantiza la ruta de menor perdida segun el peso definido.")

    print("\nConclusion: esta comparacion muestra que no basta con encontrar una ruta que funcione; "
          "tambien interesa optimizar la perdida energetica.")
