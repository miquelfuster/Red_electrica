"""
Simulacion de fallos, apagones y estados de impacto inicial.
"""

import copy
import random

from utilidades import arista_ordenada, aristas_de_ruta


def crear_evento(tipo, subtipo, gravedad, descripcion):
    return {
        "tipo": tipo,
        "subtipo": subtipo,
        "gravedad": gravedad,
        "descripcion": descripcion,
        "lineas_cortadas": [],
        "generadores_afectados": [],
        "ciudades_potencialmente_afectadas": []
    }


def analizar_uso_aristas(estado):
    uso_aristas = {}
    ciudades_por_arista = {}

    for ciudad, datos in estado["ciudades"].items():
        ruta = datos.get("ruta", [])

        for i in range(len(ruta) - 1):
            arista = arista_ordenada(ruta[i], ruta[i + 1])

            if arista not in uso_aristas:
                uso_aristas[arista] = 0
                ciudades_por_arista[arista] = []

            uso_aristas[arista] += 1

            if ciudad not in ciudades_por_arista[arista]:
                ciudades_por_arista[arista].append(ciudad)

    return uso_aristas, ciudades_por_arista


def completar_ciudades_potenciales(evento, estado_normal):
    lineas_cortadas = set(evento["lineas_cortadas"])
    generadores_afectados = {
        dato["generador"]: dato["reduccion_pct"]
        for dato in evento["generadores_afectados"]
    }

    ciudades = []

    for ciudad, datos in estado_normal["ciudades"].items():
        ruta = datos.get("ruta", [])
        gen_asignado = datos.get("generador_asignado")

        usa_linea_cortada = len(aristas_de_ruta(ruta).intersection(lineas_cortadas)) > 0
        usa_generador_afectado = gen_asignado in generadores_afectados

        if usa_linea_cortada or usa_generador_afectado:
            ciudades.append(ciudad)

    evento["ciudades_potencialmente_afectadas"] = ciudades


def cortar_linea(G_fallo, nodo_a, nodo_b, evento):
    if G_fallo.has_edge(nodo_a, nodo_b):
        G_fallo.remove_edge(nodo_a, nodo_b)
        evento["lineas_cortadas"].append(arista_ordenada(nodo_a, nodo_b))
        return True

    return False


def reducir_generador(G_fallo, generador, reduccion_pct, evento):
    if generador not in G_fallo.nodes:
        return False

    energia_original = G_fallo.nodes[generador]["energia_mw"]
    nueva_energia = energia_original * (1 - reduccion_pct / 100)
    G_fallo.nodes[generador]["energia_mw"] = nueva_energia

    evento["generadores_afectados"].append({
        "generador": generador,
        "reduccion_pct": reduccion_pct,
        "energia_original": energia_original,
        "energia_nueva": nueva_energia
    })

    return True


def generar_fallo_impactante(G, estado_normal, analisis_aristas=None):
    G_fallo = copy.deepcopy(G)
    gravedad = random.choices(
        ["leve", "moderado", "critico"],
        weights=[25, 45, 30]
    )[0]

    if analisis_aristas is None:
        uso_aristas, ciudades_por_arista = analizar_uso_aristas(estado_normal)
    else:
        uso_aristas, ciudades_por_arista = analisis_aristas

    aristas_activas = list(uso_aristas.keys())
    generadores = [n for n, d in G.nodes(data=True) if d["tipo"] == "generador"]

    if gravedad == "leve":
        evento = crear_evento(
            "fallo",
            "fallo leve",
            gravedad,
            "Fallo leve en una parte secundaria de la red. El sistema deberia poder absorberlo."
        )

        # Fallo leve: una linea normal o una reduccion pequeña de un generador.
        if random.random() < 0.65:
            lineas_normales = [
                arista_ordenada(u, v)
                for u, v, d in G.edges(data=True)
                if d["tipo"] == "normal"
            ]
            linea = random.choice(lineas_normales)
            cortar_linea(G_fallo, linea[0], linea[1], evento)
        else:
            generador = random.choice(generadores)
            reducir_generador(G_fallo, generador, 50, evento)

    elif gravedad == "moderado":
        evento = crear_evento(
            "fallo",
            "fallo moderado",
            gravedad,
            "Fallo moderado. El sistema tendra que buscar rutas alternativas y puede aparecer algun deficit."
        )

        if random.random() < 0.6 and aristas_activas:
            # Cortamos una linea que estaba siendo usada realmente.
            linea = random.choice(aristas_activas)
            cortar_linea(G_fallo, linea[0], linea[1], evento)
        else:
            generador = random.choice(generadores)
            reduccion = random.choice([50, 80])
            reducir_generador(G_fallo, generador, reduccion, evento)

    else:
        evento = crear_evento(
            "fallo",
            "fallo critico",
            gravedad,
            "Fallo critico. Se pierde mas de un recurso importante y la red puede quedar claramente afectada."
        )

        opcion = random.choice(["varias_lineas", "generador_y_linea"])

        if opcion == "varias_lineas" and aristas_activas:
            numero_lineas = min(random.choice([2, 3]), len(aristas_activas))
            lineas = random.sample(aristas_activas, numero_lineas)

            for linea in lineas:
                cortar_linea(G_fallo, linea[0], linea[1], evento)
        else:
            generador = random.choice(generadores)
            reduccion = random.choice([80, 100])
            reducir_generador(G_fallo, generador, reduccion, evento)

            if aristas_activas:
                linea = random.choice(aristas_activas)
                cortar_linea(G_fallo, linea[0], linea[1], evento)

    completar_ciudades_potenciales(evento, estado_normal)
    return G_fallo, evento


def seleccionar_arista_critica_variable(estado_normal, analisis_aristas=None):
    if analisis_aristas is None:
        uso_aristas, ciudades_por_arista = analizar_uso_aristas(estado_normal)
    else:
        uso_aristas, ciudades_por_arista = analisis_aristas

    if not uso_aristas:
        return None, []

    aristas_ordenadas = sorted(
        uso_aristas.keys(),
        key=lambda arista: uso_aristas[arista],
        reverse=True
    )

    candidatas = aristas_ordenadas[:min(3, len(aristas_ordenadas))]
    arista_elegida = random.choice(candidatas)

    return arista_elegida, ciudades_por_arista[arista_elegida]


def generar_apagon_nacional_variable(G, estado_normal, analisis_aristas=None):
    G_apagon = copy.deepcopy(G)
    tipo_apagon = random.choice([
        "linea_critica",
        "regional",
        "generador_principal",
        "combinado"
    ])

    if tipo_apagon == "linea_critica":
        evento = crear_evento(
            "apagon",
            "corte de linea critica",
            "critico",
            "El sistema ha detectado una linea con muchas rutas dependientes. Su caida puede provocar un apagon parcial."
        )

        arista, ciudades_dependientes = seleccionar_arista_critica_variable(estado_normal, analisis_aristas)

        if arista is not None:
            cortar_linea(G_apagon, arista[0], arista[1], evento)
            evento["ciudades_potencialmente_afectadas"] = ciudades_dependientes

    elif tipo_apagon == "regional":
        zonas = {
            "norte": [
                "G_Eolica_Galicia", "G_Eolica_Cantabrico",
                "Oviedo", "Valladolid", "Bilbao"
            ],
            "centro_oeste": [
                "G_Nuclear_Almaraz", "G_Hidro_Duero",
                "Salamanca", "Madrid", "Valladolid", "Zaragoza"
            ],
            "sur": [
                "G_Solar_Sevilla",
                "Sevilla", "Malaga", "Granada"
            ],
            "este": [
                "G_Gas_Barcelona", "G_Hidro_Pirineos", "G_Solar_Murcia",
                "Barcelona", "Valencia", "Alicante", "Murcia", "Zaragoza"
            ]
        }

        zona = random.choice(list(zonas.keys()))
        nodos_zona = zonas[zona]

        evento = crear_evento(
            "apagon",
            f"apagon regional en zona {zona}",
            "critico",
            f"Se produce un fallo regional en la zona {zona}. Varias conexiones cercanas quedan fuera de servicio."
        )

        candidatas = []
        for u, v in G.edges():
            if u in nodos_zona or v in nodos_zona:
                candidatas.append(arista_ordenada(u, v))

        if analisis_aristas is None:
            uso_aristas, _ = analizar_uso_aristas(estado_normal)
        else:
            uso_aristas, _ = analisis_aristas
        activas_zona = [linea for linea in candidatas if linea in uso_aristas]

        if activas_zona:
            candidatas = activas_zona

        numero_lineas = min(random.choice([2, 3]), len(candidatas))
        lineas = random.sample(candidatas, numero_lineas)

        for linea in lineas:
            cortar_linea(G_apagon, linea[0], linea[1], evento)

    elif tipo_apagon == "generador_principal":
        evento = crear_evento(
            "apagon",
            "caida de generador principal",
            "critico",
            "Uno de los generadores principales pierde gran parte de su produccion. La red debe compensarlo con otras centrales."
        )

        generadores_ordenados = sorted(
            [n for n, d in G.nodes(data=True) if d["tipo"] == "generador"],
            key=lambda n: G.nodes[n]["energia_mw"],
            reverse=True
        )

        generador = random.choice(generadores_ordenados[:3])
        reduccion = random.choice([80, 100])
        reducir_generador(G_apagon, generador, reduccion, evento)

    else:
        evento = crear_evento(
            "apagon",
            "fallo combinado nacional",
            "critico",
            "Fallo combinado: se pierde parte de la generacion y tambien una linea importante de transporte."
        )

        generadores_ordenados = sorted(
            [n for n, d in G.nodes(data=True) if d["tipo"] == "generador"],
            key=lambda n: G.nodes[n]["energia_mw"],
            reverse=True
        )

        generador = random.choice(generadores_ordenados[:3])
        reduccion = random.choice([50, 80, 100])
        reducir_generador(G_apagon, generador, reduccion, evento)

        arista, ciudades_dependientes = seleccionar_arista_critica_variable(estado_normal, analisis_aristas)
        if arista is not None:
            cortar_linea(G_apagon, arista[0], arista[1], evento)
            evento["ciudades_potencialmente_afectadas"] = ciudades_dependientes

    completar_ciudades_potenciales(evento, estado_normal)
    return G_apagon, evento


def crear_estado_impacto_inicial(estado_normal, evento):
    estado_impacto = copy.deepcopy(estado_normal)

    lineas_cortadas = set(evento["lineas_cortadas"])
    generadores_afectados = {
        dato["generador"]: dato["reduccion_pct"]
        for dato in evento["generadores_afectados"]
    }

    for ciudad, datos in estado_impacto["ciudades"].items():
        ruta = datos.get("ruta", [])
        demanda = datos["demanda_min_mw"]
        gen_asignado = datos.get("generador_asignado")

        usa_linea_cortada = len(aristas_de_ruta(ruta).intersection(lineas_cortadas)) > 0
        usa_generador_afectado = gen_asignado in generadores_afectados

        if usa_linea_cortada:
            datos["energia_recibida_mw"] = 0
            datos["suministrada"] = False
            datos["ruta"] = []
            datos["perdida_pct"] = 0
            datos["motivo"] = "su ruta original usaba una linea cortada"

        elif usa_generador_afectado:
            reduccion = generadores_afectados[gen_asignado]
            energia_original = datos["energia_recibida_mw"]
            nueva_energia = energia_original * (1 - reduccion / 100)

            datos["energia_recibida_mw"] = round(nueva_energia, 1)
            datos["suministrada"] = nueva_energia >= demanda * 0.98
            datos["motivo"] = "su generador original ha reducido la produccion"

            if not datos["suministrada"]:
                datos["ruta"] = []
                datos["perdida_pct"] = 0
                
            if gen_asignado in estado_impacto["generadores"]:
                energia_actual = estado_impacto["generadores"][gen_asignado]["energia_disponible_mw"]
                estado_impacto["generadores"][gen_asignado]["energia_disponible_mw"] = round(
                    energia_actual * (1 - reduccion / 100), 1
                )
    return estado_impacto
