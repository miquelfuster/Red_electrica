"""
Funciones auxiliares generales del simulador.

Este modulo contiene funciones pequenas reutilizadas por varias partes del proyecto.
"""

def nombre_corto(nombre):
    return (
        nombre
        .replace("G_Nuclear_Almaraz", "Nuclear")
        .replace("G_Eolica_Galicia", "Eolica Galicia")
        .replace("G_Solar_Sevilla", "Solar Sevilla")
        .replace("G_Gas_Barcelona", "Gas BCN")
        .replace("G_Hidro_Pirineos", "Hidro Pirineos")
        .replace("G_Solar_Murcia", "Solar Murcia")
        .replace("G_Eolica_Cantabrico", "Eolica Cantabrico")
        .replace("G_Hidro_Duero", "Hidro Duero")
        .replace("_", " ")
    )


def ruta_corta(ruta):
    if not ruta:
        return "Sin ruta"

    return " -> ".join(nombre_corto(nodo) for nodo in ruta)


def arista_ordenada(nodo_a, nodo_b):
    return tuple(sorted([nodo_a, nodo_b]))


def aristas_de_ruta(ruta):
    aristas = set()

    for i in range(len(ruta) - 1):
        aristas.add(arista_ordenada(ruta[i], ruta[i + 1]))

    return aristas


def calcular_distancia_ruta(G, ruta):
    distancia_total = 0

    for i in range(len(ruta) - 1):
        nodo_a = ruta[i]
        nodo_b = ruta[i + 1]
        distancia_total += G[nodo_a][nodo_b]["distancia_km"]

    return distancia_total


def resumen_lista(elementos):
    if not elementos:
        return "ninguno"

    return ", ".join(str(elemento) for elemento in elementos)


def calcular_aristas_nuevas(estado_antes, estado_despues):
    """
    Compara dos estados y devuelve las aristas que aparecen en las rutas
    finales pero no estaban activas en el estado anterior.
    """
    aristas_antes = set()
    aristas_despues = set()

    for datos in estado_antes["ciudades"].values():
        aristas_antes.update(aristas_de_ruta(datos.get("ruta", [])))

    for datos in estado_despues["ciudades"].values():
        aristas_despues.update(aristas_de_ruta(datos.get("ruta", [])))

    return aristas_despues - aristas_antes


def generadores_con_mas_sobrante(estado, cantidad=3):
    """
    Devuelve los generadores con mas energia disponible.
    """
    generadores = sorted(
        estado["generadores"].items(),
        key=lambda item: item[1]["energia_disponible_mw"],
        reverse=True
    )

    return generadores[:cantidad]

def pos_mapa(lon, lat):
    """
    Convierte coordenadas geograficas aproximadas de España
    al sistema de coordenadas usado por el grafico.
    """

    lon_min, lon_max = -9.6, 3.4
    lat_min, lat_max = 35.8, 43.9

    x_min, x_max = 0.05, 0.96
    y_min, y_max = 0.08, 0.82

    x = x_min + (lon - lon_min) / (lon_max - lon_min) * (x_max - x_min)
    y = y_min + (lat - lat_min) / (lat_max - lat_min) * (y_max - y_min)

    return x, y