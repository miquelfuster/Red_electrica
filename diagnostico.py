"""
Diagnostico de fallos y propuesta de soluciones alternativas.
"""

import networkx as nx

from distribucion import calcular_perdida_ruta
from utilidades import nombre_corto, ruta_corta


TIEMPOS_RECUPERACION = {
    "linea_normal": "4-8 horas",
    "generador_reducido": "1-3 horas",
    "generador_caido": "12-48 horas",
    "aislamiento": "varios dias o semanas",
    "capacidad": "varios dias o semanas si hay que ampliar infraestructura",
    "energia": "1-3 horas si se puede activar generacion de apoyo"
}


def buscar_linea_limitante(G, ruta, energia_a_enviar):
    for i in range(len(ruta) - 1):
        nodo_a = ruta[i]
        nodo_b = ruta[i + 1]
        capacidad = G[nodo_a][nodo_b]["capacidad_max_mw"]

        if energia_a_enviar > capacidad:
            return nodo_a, nodo_b, capacidad

    return None


def evaluar_ruta_generador_ciudad(G_fallo, estado_fallo, generador, ciudad):
    try:
        ruta = nx.dijkstra_path(G_fallo, generador, ciudad, weight="peso")
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None

    demanda = estado_fallo["ciudades"][ciudad]["demanda_min_mw"]
    perdida = calcular_perdida_ruta(G_fallo, ruta)
    factor_perdida = perdida / 100.0
    energia_necesaria = demanda / max(1 - factor_perdida, 0.05)
    disponible = estado_fallo["generadores"][generador]["energia_disponible_mw"]

    capacidad_minima = float("inf")
    linea_minima = None

    for i in range(len(ruta) - 1):
        nodo_a = ruta[i]
        nodo_b = ruta[i + 1]
        capacidad = G_fallo[nodo_a][nodo_b]["capacidad_max_mw"]

        if capacidad < capacidad_minima:
            capacidad_minima = capacidad
            linea_minima = (nodo_a, nodo_b)

    if capacidad_minima == float("inf"):
        capacidad_minima = disponible

    linea_limitante = None
    if capacidad_minima < energia_necesaria and linea_minima is not None:
        linea_limitante = (linea_minima[0], linea_minima[1], capacidad_minima)

    energia_maxima_enviable = min(disponible, capacidad_minima)
    energia_maxima_recibida = energia_maxima_enviable * (1 - factor_perdida)

    return {
        "generador": generador,
        "ruta": ruta,
        "perdida": perdida,
        "factor_perdida": factor_perdida,
        "energia_necesaria": energia_necesaria,
        "disponible": disponible,
        "linea_limitante": linea_limitante,
        "capacidad_minima": capacidad_minima,
        "linea_minima": linea_minima,
        "energia_maxima_enviable": energia_maxima_enviable,
        "energia_maxima_recibida": energia_maxima_recibida
    }


def recopilar_opciones_generadores(G_fallo, estado_fallo, ciudad):
    opciones = []

    for generador in estado_fallo["generadores"]:
        opcion = evaluar_ruta_generador_ciudad(G_fallo, estado_fallo, generador, ciudad)

        if opcion is not None:
            opciones.append(opcion)

    return opciones


def estimar_tiempo_recuperacion(evento, tipo_causa):
    tipo = tipo_causa.lower()

    if "aislamiento" in tipo:
        return TIEMPOS_RECUPERACION["aislamiento"]

    if "capacidad" in tipo:
        if evento.get("lineas_cortadas"):
            return TIEMPOS_RECUPERACION["linea_normal"]
        return TIEMPOS_RECUPERACION["capacidad"]

    if "energia" in tipo:
        for dato in evento.get("generadores_afectados", []):
            if dato["reduccion_pct"] == 100:
                return TIEMPOS_RECUPERACION["generador_caido"]

        for dato in evento.get("generadores_afectados", []):
            if dato["reduccion_pct"] < 100:
                return TIEMPOS_RECUPERACION["generador_reducido"]

        return TIEMPOS_RECUPERACION["energia"]

    if evento.get("lineas_cortadas"):
        return TIEMPOS_RECUPERACION["linea_normal"]

    return "tiempo no estimado"


def diagnosticar_causa_detallada(G_fallo, estado_fallo, ciudad, evento):
    demanda = estado_fallo["ciudades"][ciudad]["demanda_min_mw"]
    opciones = recopilar_opciones_generadores(G_fallo, estado_fallo, ciudad)

    lineas_cortadas = set(evento.get("lineas_cortadas", []))

    detalle_previo = ""
    for nodo_a, nodo_b in lineas_cortadas:
        if ciudad not in (nodo_a, nodo_b):
            continue

        otro_nodo = nodo_b if nodo_a == ciudad else nodo_a

        if otro_nodo in estado_fallo["generadores"]:
            detalle_previo = (
                f"La ciudad ha perdido su conexion directa con el generador "
                f"{nombre_corto(otro_nodo)} por el corte de "
                f"{nombre_corto(nodo_a)} <-> {nombre_corto(nodo_b)}. "
            )
            break

    if not opciones:
        tipo = "aislamiento estructural"
        mensaje = (
            f"AISLAMIENTO ESTRUCTURAL: no existe ningun camino fisico desde los generadores "
            f"hasta {ciudad}. {detalle_previo}La solucion no es solo redistribuir energia: "
            f"harian falta nuevas conexiones o reparar la infraestructura cortada."
        )
        return {
            "tipo": tipo,
            "mensaje": mensaje,
            "tiempo": estimar_tiempo_recuperacion(evento, tipo)
        }

    problemas_capacidad = []
    opciones_sin_saturacion = []

    for opcion in opciones:
        linea_limitante = opcion["linea_limitante"]

        if linea_limitante is not None:
            nodo_a, nodo_b, capacidad = linea_limitante
            energia_necesaria = opcion["energia_necesaria"]
            falta = energia_necesaria - capacidad
            porcentaje = (falta / capacidad * 100) if capacidad > 0 else 0
            problemas_capacidad.append({
                "opcion": opcion,
                "nodo_a": nodo_a,
                "nodo_b": nodo_b,
                "capacidad": capacidad,
                "energia_necesaria": energia_necesaria,
                "falta": falta,
                "porcentaje": porcentaje
            })
        else:
            opciones_sin_saturacion.append(opcion)

    if problemas_capacidad and not any(
        opcion["disponible"] >= opcion["energia_necesaria"]
        for opcion in opciones_sin_saturacion
    ):
        problema = max(problemas_capacidad, key=lambda item: item["falta"])
        opcion = problema["opcion"]
        tipo = "capacidad insuficiente"
        mensaje = (
            f"CAPACIDAD INSUFICIENTE: existe una ruta desde "
            f"{nombre_corto(opcion['generador'])} por {ruta_corta(opcion['ruta'])}, "
            f"pero la linea {nombre_corto(problema['nodo_a'])} <-> "
            f"{nombre_corto(problema['nodo_b'])} solo soporta {problema['capacidad']:.0f} MW "
            f"y harian falta {problema['energia_necesaria']:.1f} MW. "
            f"Faltan {problema['falta']:.1f} MW de capacidad, es decir, habria que ampliarla "
            f"aproximadamente un {problema['porcentaje']:.1f}%."
        )
        return {
            "tipo": tipo,
            "mensaje": mensaje,
            "tiempo": estimar_tiempo_recuperacion(evento, tipo)
        }

    energia_total_posible = sum(
        opcion["energia_maxima_recibida"]
        for opcion in opciones_sin_saturacion
    )
    falta_total = max(demanda - energia_total_posible, 0)

    detalles = []
    for opcion in opciones_sin_saturacion[:3]:
        max_recibida = opcion["energia_maxima_recibida"]
        detalles.append(
            f"desde {nombre_corto(opcion['generador'])} podrian llegar como maximo "
            f"{max_recibida:.1f} MW por {ruta_corta(opcion['ruta'])} "
            f"(disponibles {opcion['disponible']:.1f} MW)"
        )

    if not detalles and problemas_capacidad:
        # Hay rutas, pero todas tienen una linea saturada.
        problema = max(problemas_capacidad, key=lambda item: item["falta"])
        tipo = "capacidad insuficiente"
        mensaje = (
            f"CAPACIDAD INSUFICIENTE: todas las alternativas hacia {ciudad} quedan limitadas "
            f"por la capacidad de alguna linea. El cuello de botella mas claro es "
            f"{nombre_corto(problema['nodo_a'])} <-> {nombre_corto(problema['nodo_b'])}: "
            f"soporta {problema['capacidad']:.0f} MW y harian falta "
            f"{problema['energia_necesaria']:.1f} MW."
        )
        return {
            "tipo": tipo,
            "mensaje": mensaje,
            "tiempo": estimar_tiempo_recuperacion(evento, tipo)
        }

    tipo = "energia insuficiente"
    mensaje = (
        f"ENERGIA DISPONIBLE INSUFICIENTE: hay caminos fisicos y las lineas no son el problema principal, "
        f"pero la energia disponible no alcanza para cubrir los {demanda} MW de demanda. "
        f"Sumando las mejores alternativas sin saturar lineas solo podrian llegar unos "
        f"{energia_total_posible:.1f} MW; faltan aproximadamente {falta_total:.1f} MW. "
        + "; ".join(detalles) + "."
    )
    return {
        "tipo": tipo,
        "mensaje": mensaje,
        "tiempo": estimar_tiempo_recuperacion(evento, tipo)
    }


def diagnosticar_causa_concreta(G_fallo, estado_fallo, ciudad, evento):
    return diagnosticar_causa_detallada(G_fallo, estado_fallo, ciudad, evento)["mensaje"]


def diagnosticar_red(estado_normal, estado_fallo, G_fallo, evento=None):
    print("\n" + "=" * 60)
    print("DIAGNOSTICO DE LA RED TRAS LA REDISTRIBUCION")
    print("=" * 60)

    ciudades_ok_antes = sum(
        1 for c in estado_normal["ciudades"].values()
        if c["suministrada"]
    )

    ciudades_ok_despues = sum(
        1 for c in estado_fallo["ciudades"].values()
        if c["suministrada"]
    )

    total_ciudades = len(estado_normal["ciudades"])

    print(f"\nCiudades suministradas antes del fallo: {ciudades_ok_antes}/{total_ciudades}")
    print(f"Ciudades suministradas despues de redistribuir: {ciudades_ok_despues}/{total_ciudades}")
    print(f"Impacto final: {ciudades_ok_antes - ciudades_ok_despues} ciudad(es) afectada(s)")

    afectadas = []

    for ciudad, datos in estado_fallo["ciudades"].items():

        antes = estado_normal["ciudades"][ciudad]["suministrada"]
        despues = datos["suministrada"]

        if antes and not despues:
            afectadas.append(ciudad)

            demanda = datos["demanda_min_mw"]
            recibida = datos["energia_recibida_mw"]

            if evento is not None:
                diagnostico = diagnosticar_causa_detallada(G_fallo, estado_fallo, ciudad, evento)
                causa = diagnostico["mensaje"]
                tiempo = diagnostico["tiempo"]
            else:
                existe_camino = any(
                    nx.has_path(G_fallo, gen, ciudad)
                    for gen in estado_fallo["generadores"]
                )

                if not existe_camino:
                    causa = "AISLAMIENTO ESTRUCTURAL: sin camino posible desde ningun generador"
                    tiempo = TIEMPOS_RECUPERACION["aislamiento"]
                else:
                    causa = "deficit por energia disponible o capacidad insuficiente"
                    tiempo = "tiempo no estimado"

            print(f"\nCiudad afectada: {ciudad}")
            print(f"Demanda: {demanda} MW")
            print(f"Energia recibida: {recibida} MW")
            print(f"Causa concreta: {causa}")
            print(f"Tiempo estimado de recuperacion: {tiempo}")

    if not afectadas:
        print("\nLa red aguanta el fallo tras redistribuir la energia.")

    return afectadas


def imprimir_cuellos_botella(cuellos_botella):
    if not cuellos_botella:
        return

    print("\nCuellos de botella detectados como dato tecnico:")
    for cuello in cuellos_botella[:4]:
        print(
            f"- Ruta desde {nombre_corto(cuello['generador'])}: la linea "
            f"{nombre_corto(cuello['nodo_a'])} <-> {nombre_corto(cuello['nodo_b'])} "
            f"soporta {cuello['capacidad']:.0f} MW, pero harian falta "
            f"{cuello['energia_necesaria']:.1f} MW. Faltan {cuello['faltan']:.1f} MW; "
            f"habria que ampliarla un {cuello['porcentaje']:.1f}%."
        )


def proponer_solucion(G_fallo, estado_fallo, afectadas):
    print("\n" + "=" * 60)
    print("SOLUCION ALTERNATIVA PROPUESTA")
    print("=" * 60)

    rutas_solucion = {}

    if not afectadas:
        print("\nNo hace falta proponer una obra nueva: la redistribucion ha sido suficiente.")
        return rutas_solucion

    afectadas_ordenadas = sorted(
        afectadas,
        key=lambda c: estado_fallo["ciudades"][c]["demanda_min_mw"],
        reverse=True
    )

    for ciudad in afectadas_ordenadas:

        demanda = estado_fallo["ciudades"][ciudad]["demanda_min_mw"]

        print(f"\nSolucion para {ciudad}")
        print(f"Demanda: {demanda} MW")

        opciones = recopilar_opciones_generadores(G_fallo, estado_fallo, ciudad)
        cuellos_botella = []
        opciones_sin_saturacion = []
        opciones_individuales = []

        for opcion in opciones:
            linea_limitante = opcion["linea_limitante"]

            if linea_limitante is not None:
                nodo_a, nodo_b, capacidad = linea_limitante
                energia_necesaria = opcion["energia_necesaria"]
                faltan = energia_necesaria - capacidad
                porcentaje = (faltan / capacidad * 100) if capacidad > 0 else 0
                cuellos_botella.append({
                    "generador": opcion["generador"],
                    "ruta": opcion["ruta"],
                    "nodo_a": nodo_a,
                    "nodo_b": nodo_b,
                    "capacidad": capacidad,
                    "energia_necesaria": energia_necesaria,
                    "faltan": faltan,
                    "porcentaje": porcentaje
                })
                continue

            # Solo se consideran generadores con energia sobrante real tras la redistribucion.
            if opcion["energia_maxima_recibida"] <= 0:
                continue

            opciones_sin_saturacion.append(opcion)

            if opcion["disponible"] >= opcion["energia_necesaria"]:
                opciones_individuales.append(opcion)

        if opciones_individuales:
            mejor_opcion = min(opciones_individuales, key=lambda item: item["perdida"])
            energia_recibida = mejor_opcion["energia_necesaria"] * (1 - mejor_opcion["factor_perdida"])

            print("\nSolucion individual viable usando energia sobrante tras la redistribucion:")
            print(f"Ruta alternativa posible: {ruta_corta(mejor_opcion['ruta'])}")
            print(f"Generador alternativo: {nombre_corto(mejor_opcion['generador'])}")
            print(f"Perdida de la ruta: {mejor_opcion['perdida']:.1f}%")
            print(f"Energia que habria que enviar: {mejor_opcion['energia_necesaria']:.1f} MW")
            print(f"Energia que llegaria: {energia_recibida:.1f} MW")

            rutas_solucion[ciudad] = [mejor_opcion["ruta"]]
            imprimir_cuellos_botella(cuellos_botella)
            continue

        # Si ningun generador individual puede cubrir la ciudad, probamos dos juntos.
        mejor_combinacion = None
        opciones_ordenadas = sorted(
            opciones_sin_saturacion,
            key=lambda item: item["energia_maxima_recibida"],
            reverse=True
        )

        for i in range(len(opciones_ordenadas)):
            for j in range(i + 1, len(opciones_ordenadas)):
                op1 = opciones_ordenadas[i]
                op2 = opciones_ordenadas[j]

                max_recibida1 = op1["energia_maxima_recibida"]
                max_recibida2 = op2["energia_maxima_recibida"]
                total_maximo = max_recibida1 + max_recibida2

                if total_maximo < demanda * 0.98:
                    continue

                # Reparto proporcional al margen real de cada generador.
                objetivo = demanda
                recibida1_objetivo = objetivo * (max_recibida1 / total_maximo)
                recibida1_objetivo = min(recibida1_objetivo, max_recibida1)
                recibida2_objetivo = objetivo - recibida1_objetivo

                if recibida2_objetivo > max_recibida2:
                    recibida2_objetivo = max_recibida2
                    recibida1_objetivo = objetivo - recibida2_objetivo

                if recibida1_objetivo > max_recibida1 or recibida2_objetivo > max_recibida2:
                    continue

                envio1 = recibida1_objetivo / max(1 - op1["factor_perdida"], 0.05)
                envio2 = recibida2_objetivo / max(1 - op2["factor_perdida"], 0.05)
                recibida_total = recibida1_objetivo + recibida2_objetivo

                mejor_combinacion = {
                    "op1": op1,
                    "op2": op2,
                    "envio1": envio1,
                    "envio2": envio2,
                    "recibida1": recibida1_objetivo,
                    "recibida2": recibida2_objetivo,
                    "recibida_total": recibida_total
                }
                break

            if mejor_combinacion is not None:
                break

        if mejor_combinacion is not None:
            op1 = mejor_combinacion["op1"]
            op2 = mejor_combinacion["op2"]

            print("\nNingun generador individual cubre toda la demanda con la energia sobrante, pero si existe una solucion combinada:")
            print(
                f"- {nombre_corto(op1['generador'])} enviaria {mejor_combinacion['envio1']:.1f} MW "
                f"por {ruta_corta(op1['ruta'])}; llegarian {mejor_combinacion['recibida1']:.1f} MW."
            )
            print(
                f"- {nombre_corto(op2['generador'])} enviaria {mejor_combinacion['envio2']:.1f} MW "
                f"por {ruta_corta(op2['ruta'])}; llegarian {mejor_combinacion['recibida2']:.1f} MW."
            )
            print(f"Energia total recibida con suministro combinado: {mejor_combinacion['recibida_total']:.1f} MW")

            rutas_solucion[ciudad] = [op1["ruta"], op2["ruta"]]
            imprimir_cuellos_botella(cuellos_botella)
        else:
            energia_total_posible = sum(
                opcion["energia_maxima_recibida"]
                for opcion in opciones_sin_saturacion
            )
            faltante_total = max(demanda - energia_total_posible, 0)

            print("\nNo hay una ruta alternativa viable con la red actual.")

            if opciones_sin_saturacion:
                print(
                    f"Aunque se combinaran los generadores accesibles sin saturar lineas, "
                    f"solo se podrian recibir unos {energia_total_posible:.1f} MW. "
                    f"Faltarian aproximadamente {faltante_total:.1f} MW."
                )

            imprimir_cuellos_botella(cuellos_botella)
            print("Solucion tecnica propuesta: crear una nueva linea o aumentar la capacidad de una linea existente.")

    return rutas_solucion
