import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from collections import defaultdict
import re
import json

seasons = ["23/24", "22/23", "21/22", "20/21", "19/20","18/19","17/18","16/17","15/16","14/15"]


market_values = defaultdict(lambda: defaultdict(float))
xgoalsbyseason = defaultdict(lambda: defaultdict(float))
goalsbyseason = defaultdict(lambda: defaultdict(float))



def scrap_goals(season,goalsbyseason):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    url_base = "https://understat.com/league/EPL/"
    last_year_url = url_base + last_year
    response = requests.get(last_year_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Buscar el script que contiene los datos JSON
    script = soup.find('script', string=lambda t: t and 'datesData' in t)
    json_data = None

    if script:
        # Extraer el contenido JSON
        json_text = script.string
        start_index = json_text.index('=') + 14
        end_index = json_text.rindex(';') - 34  # Busca el último punto y coma
        json_text = json_text[start_index:end_index].strip()  # Limpia el text
        # Decodificar caracteres de escape hexadecimales
        json_text = decode_hex_string(json_text)
        try:
            matches = json.loads(json_text)  # Convertir a objeto de Python
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return None

        goalsbyseason[season] = {}

        # Sumar xG para cada equipo
        for match in matches:
            home_team = match['h']['title']
            away_team = match['a']['title']
            home_xg = float(match['goals']['h'])
            away_xg = float(match['goals']['a'])

            # Sumar para el equipo local
            if home_team not in goalsbyseason[season]:
                goalsbyseason[season][home_team] = []


            if away_team not in goalsbyseason[season]:
                goalsbyseason[season][away_team] = []

            # Agregar los xG a la lista correspondiente
            goalsbyseason[season][home_team].append(home_xg)
            goalsbyseason[season][away_team].append(away_xg)
        # Calcular los xG acumulados
        if season in goalsbyseason:
            for team, xg_list in goalsbyseason[season].items():
                # Crear una lista acumulativa
                accumulated_xg = []
                total_xg = 0

                for xg in xg_list:
                    total_xg += xg
                    accumulated_xg.append(total_xg)

                # Reemplazar la lista original con la lista acumulada
                goalsbyseason[season][team] = accumulated_xg
    return goalsbyseason
def decode_hex_string(hex_string):
    # Decodifica los caracteres de escape hexadecimales
    return bytes(hex_string, "utf-8").decode("unicode_escape")
def scrap_xgoals(season,xg_by_season_club):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    url_base = "https://understat.com/league/EPL/"
    last_year_url = url_base + last_year
    response = requests.get(last_year_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Buscar el script que contiene los datos JSON
    script = soup.find('script', string=lambda t: t and 'datesData' in t)
    json_data = None

    if script:
        # Extraer el contenido JSON
        json_text = script.string
        start_index = json_text.index('=') + 14
        end_index = json_text.rindex(';') - 34  # Busca el último punto y coma
        json_text = json_text[start_index:end_index].strip()  # Limpia el text
        # Decodificar caracteres de escape hexadecimales
        json_text = decode_hex_string(json_text)
        try:
            matches = json.loads(json_text)  # Convertir a objeto de Python
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return None

        xg_by_season_club[season] = {}

        # Sumar xG para cada equipo
        for match in matches:
            home_team = match['h']['title']
            away_team = match['a']['title']
            home_xg = float(match['xG']['h'])
            away_xg = float(match['xG']['a'])

            # Sumar para el equipo local
            if home_team not in xg_by_season_club[season]:
                xg_by_season_club[season][home_team] = []


            if away_team not in xg_by_season_club[season]:
                xg_by_season_club[season][away_team] = []

            # Agregar los xG a la lista correspondiente
            xg_by_season_club[season][home_team].append(home_xg)
            xg_by_season_club[season][away_team].append(away_xg)
        # Calcular los xG acumulados
        if season in xg_by_season_club:
            for team, xg_list in xg_by_season_club[season].items():
                # Crear una lista acumulativa
                accumulated_xg = []
                total_xg = 0

                for xg in xg_list:
                    total_xg += xg
                    accumulated_xg.append(total_xg)

                # Reemplazar la lista original con la lista acumulada
                xg_by_season_club[season][team] = accumulated_xg
    return xg_by_season_club
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
    # market_values = scrapp_season_teams_value(season=season,clubs=market_values)
    # print(market_values)
    # print(scrap_matrix_results(season=season))
    #xgoalsbyseason = scrap_xgoals(season=season,xg_by_season_club=xgoalsbyseason)
    goalsbyseason= scrap_goals(season=season, goalsbyseason=goalsbyseason)
    print(goalsbyseason)
