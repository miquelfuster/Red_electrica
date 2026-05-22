"""
Construccion de la red electrica y creacion del estado inicial.
"""

import networkx as nx
from utilidades import pos_mapa


def construir_red():
    """
    Crea el grafo de la red electrica simplificada.

    Nodos:
    - tipo generador: produce energia.
    - tipo ciudad: necesita una demanda minima de energia.

    Aristas:
    - distancia_km: longitud de la linea.
    - tipo: alta_tension o normal.
    - capacidad_max_mw: energia maxima que puede transportar la linea.

    El peso de cada arista representa la perdida energetica:
        perdida = distancia_km * coeficiente_tipo

    Dijkstra usa ese peso para buscar la ruta con menor perdida.
    """

    G = nx.Graph()

    # Generadores
    generadores = [
        ("G_Nuclear_Almaraz", {
            "tipo": "generador",
            "energia_mw": 2100,
            "pos": pos_mapa(-5.70, 39.80),
            "region": "Extremadura"
        }),

        ("G_Eolica_Galicia", {
            "tipo": "generador",
            "energia_mw": 1400,
            "pos": pos_mapa(-8.75, 43.00),
            "region": "Galicia"
        }),

        ("G_Solar_Sevilla", {
            "tipo": "generador",
            "energia_mw": 1100,
            "pos": pos_mapa(-6.25, 37.20),
            "region": "Andalucia"
        }),

        ("G_Gas_Barcelona", {
            "tipo": "generador",
            "energia_mw": 1600,
            "pos": pos_mapa(2.45, 41.60),
            "region": "Cataluña"
        }),

        ("G_Hidro_Pirineos", {
            "tipo": "generador",
            "energia_mw": 800,
            "pos": pos_mapa(0.55, 42.75),
            "region": "Aragon"
        }),

        ("G_Solar_Murcia", {
            "tipo": "generador",
            "energia_mw": 850,
            "pos": pos_mapa(-1.35, 37.75),
            "region": "Sureste"
        }),

        ("G_Eolica_Cantabrico", {
            "tipo": "generador",
            "energia_mw": 700,
            "pos": pos_mapa(-4.70, 43.50),
            "region": "Cantabrico"
        }),

        ("G_Hidro_Duero", {
            "tipo": "generador",
            "energia_mw": 500,
            "pos": pos_mapa(-5.75, 41.70),
            "region": "Centro-oeste"
        }),
    ]

        # Ciudades
    ciudades = [
            ("Madrid", {
                "tipo": "ciudad",
                "demanda_min_mw": 900,
                "pos": pos_mapa(-3.70, 40.42),
                "region": "Centro"
            }),

            ("Barcelona", {
                "tipo": "ciudad",
                "demanda_min_mw": 750,
                "pos": pos_mapa(2.17, 41.38),
                "region": "Cataluña"
            }),

            ("Valencia", {
                "tipo": "ciudad",
                "demanda_min_mw": 480,
                "pos": pos_mapa(-0.38, 39.47),
                "region": "Levante"
            }),

            ("Sevilla", {
                "tipo": "ciudad",
                "demanda_min_mw": 420,
                "pos": pos_mapa(-5.99, 37.39),
                "region": "Andalucia"
            }),

            ("Zaragoza", {
                "tipo": "ciudad",
                "demanda_min_mw": 310,
                "pos": pos_mapa(-0.88, 41.65),
                "region": "Aragon"
            }),

            ("Bilbao", {
                "tipo": "ciudad",
                "demanda_min_mw": 280,
                "pos": pos_mapa(-2.94, 43.26),
                "region": "Pais Vasco"
            }),

            ("Malaga", {
                "tipo": "ciudad",
                "demanda_min_mw": 260,
                "pos": pos_mapa(-4.42, 36.72),
                "region": "Andalucia"
            }),

            ("Valladolid", {
                "tipo": "ciudad",
                "demanda_min_mw": 190,
                "pos": pos_mapa(-4.72, 41.65),
                "region": "Castilla"
            }),

            ("Murcia", {
                "tipo": "ciudad",
                "demanda_min_mw": 340,
                "pos": pos_mapa(-1.13, 37.99),
                "region": "Sureste"
            }),

            ("Alicante", {
                "tipo": "ciudad",
                "demanda_min_mw": 300,
                "pos": pos_mapa(-0.49, 38.35),
                "region": "Levante"
            }),

            ("Granada", {
                "tipo": "ciudad",
                "demanda_min_mw": 230,
                "pos": pos_mapa(-3.60, 37.18),
                "region": "Andalucia oriental"
            }),

            ("Oviedo", {
                "tipo": "ciudad",
                "demanda_min_mw": 210,
                "pos": pos_mapa(-5.85, 43.36),
                "region": "Asturias"
            }),

            ("Salamanca", {
                "tipo": "ciudad",
                "demanda_min_mw": 160,
                "pos": pos_mapa(-5.66, 40.97),
                "region": "Castilla y Leon"
            }),
        ]

    for nombre, atributos in generadores + ciudades:
        G.add_node(nombre, **atributos)

    # Lineas de transmision:
    lineas = [
        ("G_Nuclear_Almaraz", "Madrid", 220, "alta_tension", 1500),
        ("Madrid", "Barcelona", 620, "alta_tension", 1200),
        ("Madrid", "Zaragoza", 320, "alta_tension", 900),
        ("G_Gas_Barcelona", "Barcelona", 30, "alta_tension", 1800),
        ("G_Hidro_Pirineos", "Zaragoza", 150, "alta_tension", 700),
        ("G_Eolica_Galicia", "Valladolid", 280, "alta_tension", 1000),
        ("G_Solar_Sevilla", "Sevilla", 20, "alta_tension", 1000),
        ("G_Nuclear_Almaraz", "Valladolid", 190, "normal", 800),
        ("G_Nuclear_Almaraz", "Sevilla", 340, "normal", 600),
        ("G_Solar_Sevilla", "Malaga", 90, "normal", 400),
        ("Sevilla", "Malaga", 210, "normal", 350),
        ("Madrid", "Valladolid", 190, "normal", 700),
        ("Madrid", "Valencia", 360, "normal", 800),
        ("Valladolid", "Bilbao", 280, "normal", 500),
        ("Zaragoza", "Barcelona", 310, "normal", 600),
        ("Zaragoza", "Bilbao", 310, "normal", 450),
        ("Zaragoza", "Valencia", 310, "normal", 500),
        ("G_Hidro_Pirineos", "Barcelona", 200, "normal", 600),
        ("G_Eolica_Galicia", "Bilbao", 310, "normal", 500),
        ("G_Solar_Murcia", "Murcia", 40, "alta_tension", 900),
        ("G_Solar_Murcia", "Alicante", 110, "alta_tension", 650),
        ("Murcia", "Alicante", 80, "normal", 450),
        ("Murcia", "Valencia", 230, "normal", 600),
        ("Alicante", "Valencia", 170, "normal", 450),
        ("Murcia", "Granada", 280, "normal", 400),
        ("G_Solar_Sevilla", "Granada", 220, "normal", 450),
        ("Granada", "Malaga", 130, "normal", 350),
        ("Granada", "Sevilla", 250, "normal", 400),
        ("G_Eolica_Cantabrico", "Oviedo", 50, "alta_tension", 800),
        ("Oviedo", "Bilbao", 300, "normal", 450),
        ("Oviedo", "Valladolid", 260, "normal", 450),
        ("G_Eolica_Galicia", "Oviedo", 280, "normal", 500),
        ("G_Hidro_Duero", "Salamanca", 40, "alta_tension", 650),
        ("Salamanca", "Madrid", 220, "normal", 500),
        ("Salamanca", "Valladolid", 120, "normal", 500),
        ("G_Nuclear_Almaraz", "Salamanca", 160, "normal", 500),
    ]

    # Coeficientes de perdida.
    coeficientes = {
        "alta_tension": 0.00002,
        "normal": 0.00008
    }

    for nodo_a, nodo_b, distancia, tipo, capacidad in lineas:
        coeficiente = coeficientes[tipo]
        peso = distancia * coeficiente

        G.add_edge(
            nodo_a,
            nodo_b,
            distancia_km=distancia,
            tipo=tipo,
            capacidad_max_mw=capacidad,
            peso=peso,
            coeficiente=coeficiente
        )

    return G


def inicializar_estado(G):
    estado = {
        "generadores": {},
        "ciudades": {}
    }

    for nodo, datos in G.nodes(data=True):

        if datos["tipo"] == "generador":
            estado["generadores"][nodo] = {
                "energia_disponible_mw": datos["energia_mw"],
                "energia_usada_mw": 0
            }

        elif datos["tipo"] == "ciudad":
            estado["ciudades"][nodo] = {
                "demanda_min_mw": datos["demanda_min_mw"],
                "energia_recibida_mw": 0,
                "suministrada": False,
                "generador_asignado": None,
                "ruta": [],
                "perdida_pct": 0,
                "motivo": ""
            }

    return estado
