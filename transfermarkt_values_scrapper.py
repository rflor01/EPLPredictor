import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from collections import defaultdict
import re

seasons = ["23/24", "22/23", "21/22", "20/21", "19/20","18/19","17/18","16/17","15/16"]


market_values = defaultdict(lambda: defaultdict(float))

def scrap_matrix_results(season):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    url_base = "https://www.transfermarkt.es/premier-league/kreuztabelle/wettbewerb/GB1/saison_id/"
    last_year_url = url_base + last_year
    response = requests.get(last_year_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table", {"class": "kreuztabelle"})  # Ajusta la clase según el HTML de la página
    if table is None:
        print("No se encontró la tabla de resultados.")
        return None

    # Extraer los nombres de los equipos
    first_row = table.find("tr")  # Seleccionamos la primera fila que contiene los nombres de equipos
    teams = [team['title'] for team in first_row.find_all("a", href=True) if team.find("img")]

    # Extraer los resultados de la tabla
    results_vector = []
    rows = table.find_all("tr")[1:]  # Saltar la primera fila que contiene los encabezados
    for i, row in enumerate(rows):
        # Buscar todos los enlaces <a> que contengan resultados (tienen la clase "ergebnis-link")
        result_links = row.find_all("a", {"class": "ergebnis-link"})

        # Iterar sobre cada resultado encontrado en la fila actual
        for j, link in enumerate(result_links):
            # Obtener el texto del marcador dentro del <span>
            result_span = link.find("span")
            if result_span:
                # Evitar procesar la diagonal principal de la matriz (cuando i == j)
                if i == j:
                    continue

                home_team = teams[i]  # Equipo de la fila actual
                away_team = teams[j]  # Equipo de la columna correspondiente
                result_text = result_span.get_text(strip=True)  # Resultado (por ejemplo, 3:2)
                title_text = link.get('title')  # Obtiene algo como "19. Jornada, mar 26.12.2023"
                match_day = re.search(r"\d+", title_text).group() if title_text else "Unknown"  # Extrae "19. Jornada"

                # Guardar como "home_team_away_team", resultado y jornada
                results_vector.append(
                    [f"{home_team.lower().replace(' ', '-')}_{away_team.lower().replace(' ', '-')}", result_text,
                     match_day])
    return results_vector

def scrapp_season_teams_value(season,clubs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    url_base = "https://www.transfermarkt.es/premier-league/startseite/wettbewerb/GB1/plus/?saison_id="
    last_year_url = url_base + last_year
    response = requests.get(last_year_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    tabla_equipos = soup.find("table", class_="items")
    this_season_clubs = []
    this_season_values = []
    if not tabla_equipos:
        return {}

    filas = tabla_equipos.find_all("tr", class_=["odd", "even"])
    for fila in filas:
        nombre_equipo = fila.find("td", class_="hauptlink").text.strip()
        this_season_clubs.append(nombre_equipo)
        valor = fila.find_all("td", class_="rechts")[1].text.strip()

        # Limpieza de valor de mercado (remover símbolos y convertir a float)
        valor = valor.replace("mill","").replace(".","").replace("€","").replace(" ","")


        if 'mil' in valor:
            valor_float = float(valor.replace('mil', '').strip().replace(",",".")) * 1000  # Convertir a número
        else:
            valor_float = float(valor.replace(",","."))
        this_season_values.append(valor_float)
        clubs[season][nombre_equipo] = valor_float

    return market_values

for season in seasons:
    market_values = scrapp_season_teams_value(season=season,clubs=market_values)
    print(market_values)
    print(scrap_matrix_results(season=season))
