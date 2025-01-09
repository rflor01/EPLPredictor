import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from collections import defaultdict
import re
import json
import numpy as np
import scipy.io

seasons = ["23/24", "22/23", "21/22", "20/21", "19/20","18/19","17/18","16/17","15/16","14/15"]

meanage = defaultdict(lambda: defaultdict(float))
market_values = defaultdict(lambda: defaultdict(float))
possession = defaultdict(lambda: defaultdict(float))
recoveries = defaultdict(lambda: defaultdict(float))
xgoalsbyseason = defaultdict(lambda: defaultdict(float))
goalsbyseason = defaultdict(lambda: defaultdict(float))
goalsagainstbyseason = defaultdict(lambda: defaultdict(float))
xgoalsagainstbyseason = defaultdict(lambda: defaultdict(float))
pointsbyseason = defaultdict(lambda: defaultdict(float))
cleansheets = defaultdict(lambda: defaultdict(float))
streaks = defaultdict(lambda: defaultdict(float))
results_by_season = {}

team_replacements = {
    "man": "manchester",
    "utd": "united",
    "luton": "lutontown",
    "nott'hamforest": "nottinghamforest",
    "wolves": "wolverhamptonwanderers",
    "leicester": "leicestercity",
    "leeds": "leedsunited",
    "brighton": "brighton&hovealbion",
    "westham": "westhamunited",
    "newcastle": "newcastleunited",
    "norwich": "norwichcity",
    "tottenham": "tottenhamhotspur",
    "huddersfield": "huddersfieldtown",
    "chelse": "chelsea",
    "westbrom": "westbromwichalbion",
    "stoke": "stokecity",
    "swansea": "swanseacity",
    "qpr": "queensparkrangers",
    "hull": "hullcity",
    "cardiff": "cardiffcity"
}


def decode_hex_string(hex_string):
    return bytes(hex_string, "utf-8").decode("unicode_escape")


def scrap_streak(season, pointsbyseason):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    url_base = "https://understat.com/league/EPL/"
    last_year_url = url_base + last_year
    response = requests.get(last_year_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.find('script', string=lambda t: t and 'datesData' in t)
    json_data = None

    if script:
        json_text = script.string
        start_index = json_text.index('=') + 14
        end_index = json_text.rindex(';') - 34
        json_text = json_text[start_index:end_index].strip()
        json_text = decode_hex_string(json_text)
        try:
            matches = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

        pointsbyseason[season] = {}

        # Inicializar puntos por equipo
        for match in matches:
            home_team = match['h']['title']
            away_team = match['a']['title']
            if home_team not in pointsbyseason[season]:
                pointsbyseason[season][home_team] = []
            if away_team not in pointsbyseason[season]:
                pointsbyseason[season][away_team] = []

        # Agregar puntos por partido
        for match in matches:
            home_team = match['h']['title']
            away_team = match['a']['title']
            home_goals = int(match['goals']['h'])
            away_goals = int(match['goals']['a'])

            if home_goals > away_goals:
                home_points = 3
                away_points = 0
            elif home_goals < away_goals:
                home_points = 0
                away_points = 3
            else:
                home_points = 1
                away_points = 1

            pointsbyseason[season][home_team].append(home_points)
            pointsbyseason[season][away_team].append(away_points)

        # Calcular puntos de los últimos 5 partidos
        if season in pointsbyseason:
            for team, points_list in pointsbyseason[season].items():
                last_5_points = [sum(points_list[max(0, i - 4):i + 1]) for i in range(len(points_list))]
                pointsbyseason[season][team] = last_5_points

    return pointsbyseason




def scrap_points(season, pointsbyseason):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    url_base = "https://understat.com/league/EPL/"
    last_year_url = url_base + last_year
    response = requests.get(last_year_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.find('script', string=lambda t: t and 'datesData' in t)
    json_data = None

    if script:
        json_text = script.string
        start_index = json_text.index('=') + 14
        end_index = json_text.rindex(';') - 34
        json_text = json_text[start_index:end_index].strip()
        json_text = decode_hex_string(json_text)
        try:
            matches = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

        pointsbyseason[season] = {}

        for match in matches:
            home_team = match['h']['title']
            away_team = match['a']['title']
            if home_team not in pointsbyseason[season]:
                pointsbyseason[season][home_team] = []
            if away_team not in pointsbyseason[season]:
                pointsbyseason[season][away_team] = []

        for match in matches:
            home_team = match['h']['title']
            away_team = match['a']['title']
            home_goals = int(match['goals']['h'])
            away_goals = int(match['goals']['a'])

            if home_goals > away_goals:
                home_points = 3
                away_points = 0
            elif home_goals < away_goals:
                home_points = 0
                away_points = 3
            else:
                home_points = 1
                away_points = 1

            pointsbyseason[season][home_team].append(home_points)
            pointsbyseason[season][away_team].append(away_points)

        if season in pointsbyseason:
            for team, points_list in pointsbyseason[season].items():
                accumulated_points = [0]  # Start with 0
                total_points = 0

                for points in points_list[:-1]:  # Exclude the last value
                    total_points += points
                    accumulated_points.append(total_points)

                pointsbyseason[season][team] = accumulated_points

    return pointsbyseason





def create_mat_file_with_V(enriched_results_by_season):
    design_results = []
    test_results = []
    all_seasons = list(enriched_results_by_season.keys())

    # Dividir las temporadas entre Design y Test
    for season in all_seasons:
        if season == all_seasons[0]:  # Última temporada para Test
            test_results.extend(enriched_results_by_season[season])
        else:
            design_results.extend(enriched_results_by_season[season])

    # Inicializar matrices para Design
    design_C = np.array([match[-1] for match in design_results])  # 0, 1, 2 resultados
    design_P = np.array([
        [match[2], match[3], match[4], match[5], match[6], match[7], match[8], match[9], match[10], match[11], match[12], match[13], match[14], match[15], match[16]]
        for match in design_results
    ]).T

    # Crear estructuras para MATLAB
    Design = {'T': design_C, 'P': design_P}
    Test = {
        'T': np.array([match[-1] for match in test_results]),  # total_goals guardado en match[-1]
        'P': np.array([
            [match[2],match[3], match[4], match[5], match[6], match[7], match[8], match[9], match[10], match[11], match[12], match[13], match[14], match[15], match[16]]
            for match in test_results
        ]).T
    }

    # Guardar en archivo .mat
    scipy.io.savemat('PremierLeague_with_V.mat', {'Design': Design, 'Test': Test})

def create_mat_file(enriched_results_by_season):
    design_results = []
    test_results = []
    all_seasons = list(enriched_results_by_season.keys())

    # Iterar sobre cada temporada para construir la estructura
    for season in all_seasons:
        if season == all_seasons[0]:  # Si es la última temporada, la guardamos en Test
            test_results.extend(enriched_results_by_season[season])
        else:  # Otras temporadas van a Design
            design_results.extend(enriched_results_by_season[season])

    # Inicializar listas para las columnas de Design
    design_C = []  # Para 0, 1 o 2
    design_P = []  # Para posesión, goles, etc.

    # Crear un array de ceros para almacenar los resultados y estadísticas
    num_matches = len(design_results)

    design_C = np.zeros(num_matches)  # Inicializar design_C con ceros
    design_P = np.zeros((15, num_matches))  # 12 estadísticas por partido

    for idx, match in enumerate(design_results):
        # El resultado del partido
        design_C[idx] = match[-2]  # El indicador de resultado (0, 1, 2)

        # Llenar el array design_P con los datos correspondientes
        design_P[0, idx] = match[2]  # Jornada
        design_P[1, idx] = match[3]  # Puntoslocal
        design_P[2, idx] = match[4]  # Puntos visitante
        design_P[3, idx] = match[5]  # Valor del equipo local
        design_P[4, idx] = match[6]  # Valor del equipo visitante
        design_P[5, idx] = match[7]  # Posesión local
        design_P[6, idx] = match[8]  # Posesión visitante
        design_P[7, idx] = match[9]  # Goles a favor local
        design_P[8, idx] = match[10]  # Goles a favor visitante
        design_P[9, idx] = match[11]  # Goles en contra local
        design_P[10, idx] = match[12]  # Goles en contra visitante
        design_P[11, idx] = match[13]  # Expected goals local
        design_P[12, idx] = match[14]  # Expected goals visitante
        design_P[13, idx] = match[15]  # xGoals en contra local
        design_P[14, idx] = match[16]  # xGoals en contra visitante

    # Crear las estructuras para MATLAB
    Design = {
        'C': design_C,
        'P': design_P
    }

    # Estructura Test similar a Design, pero solo para la última temporada
    num_test_matches = len(test_results)
    test_C = np.zeros(num_test_matches)
    test_P = np.zeros((15, num_test_matches))  # 12 estadísticas por partido

    for idx, match in enumerate(test_results):
        test_C[idx] = match[-2]  # El indicador de resultado (0, 1, 2)
        test_P[0, idx] = match[2]  # Jornada
        design_P[1, idx] = match[3]  # Puntoslocal
        design_P[2, idx] = match[4]  # Puntos visitante
        test_P[3, idx] = match[5]  # Valor del equipo local
        test_P[4, idx] = match[6]  # Valor del equipo visitante
        test_P[5, idx] = match[7]  # Posesión local
        test_P[6, idx] = match[8]  # Posesión visitante
        test_P[7, idx] = match[9]  # Goles a favor local
        test_P[8, idx] = match[10]  # Goles a favor visitante
        test_P[9, idx] = match[11]  # Goles en contra local
        test_P[10, idx] = match[12]  # Goles en contra visitante
        test_P[11, idx] = match[13]  # Expected goals local
        test_P[12, idx] = match[14]  # Expected goals visitante
        test_P[13, idx] = match[15]  # xGoals en contra local
        test_P[14, idx] = match[16]  # xGoals en contra visitante

    Test = {
        'C': test_C,
        'P': test_P
    }

    # Guardar en archivo .mat
    scipy.io.savemat('PremierLeague.mat', {'Design': Design, 'Test': Test})





def enrich_results_with_stats(results_by_season, market_values, possession, goalsbyseason, goalsagainstbyseason, xgoalsbyseason, xgoalsagainstbyseason, pointsbyseason):
    enriched_results_by_season = {}

    for season, matches in results_by_season.items():
        enriched_results = []
        for match in matches:
            teams, score, jornada = match

            # Obtener los nombres de los equipos
            team1, team2 = teams.split("_")

            # Obtener estadísticas para cada equipo
            try:
                team1_market_value = market_values[season][team1]
                team2_market_value = market_values[season][team2]
            except KeyError:
                team1_market_value = 0  # Valor por defecto si no se encuentra
                team2_market_value = 0  # Valor por defecto si no se encuentra

            try:
                team1_possession = possession[season][team1]
                team2_possession = possession[season][team2]
            except KeyError:
                team1_possession = 0  # Valor por defecto si no se encuentra
                team2_possession = 0  # Valor por defecto si no se encuentra

            # Obtener goles a favor previo a la jornada en disputa (jornada - 1)
            jornada_index = int(jornada) - 1  # Convertir jornada a índice
            try:
                team1_goals = goalsbyseason[season][team1][jornada_index]
                team2_goals = goalsbyseason[season][team2][jornada_index]
            except KeyError:
                team1_goals = 0  # Valor por defecto si no se encuentra
                team2_goals = 0  # Valor por defecto si no se encuentra
            except IndexError:
                team1_goals = 0  # Valor por defecto si el índice está fuera de rango
                team2_goals = 0  # Valor por defecto si el índice está fuera de rango

            try:
                team1_xgoalsagainst = xgoalsagainstbyseason[season][team1][jornada_index]
                team2_xgoalsagainst = xgoalsagainstbyseason[season][team2][jornada_index]
            except KeyError:
                team1_xgoalsagainst = 0  # Valor por defecto si no se encuentra
                team2_xgoalsagainst = 0  # Valor por defecto si no se encuentra
            except IndexError:
                team1_xgoalsagainst = 0  # Valor por defecto si el índice está fuera de rango
                team2_xgoalsagainst = 0  # Valor por defecto si el índice está fuera de rango
            try:
                team1_points = pointsbyseason[season][team1][jornada_index]
                team2_points = pointsbyseason[season][team2][jornada_index]
            except KeyError:
                team1_points = 0  # Valor por defecto si no se encuentra
                team2_points = 0  # Valor por defecto si no se encuentra
            except IndexError:
                team1_points = 0  # Valor por defecto si el índice está fuera de rango
                team2_points = 0  # Valor por defecto si el índice está fuera de rango
            try:
                team1_xgoals = xgoalsbyseason[season][team1][jornada_index]
                team2_xgoals = xgoalsbyseason[season][team2][jornada_index]
            except KeyError:
                team1_xgoals = 0  # Valor por defecto si no se encuentra
                team2_xgoals = 0  # Valor por defecto si no se encuentra
            except IndexError:
                team1_xgoals = 0  # Valor por defecto si el índice está fuera de rango
                team2_xgoals = 0  # Valor por defecto si el índice está fuera de rango

            try:
                team1_goalsagainst = goalsagainstbyseason[season][team1][jornada_index]
                team2_goalsagainst = goalsagainstbyseason[season][team2][jornada_index]
            except KeyError:
                team1_goalsagainst = 0  # Valor por defecto si no se encuentra
                team2_goalsagainst = 0  # Valor por defecto si no se encuentra
            except IndexError:
                team1_goalsagainst = 0  # Valor por defecto si el índice está fuera de rango
                team2_goalsagainst = 0  # Valor por defecto si el índice está fuera de rango

            # Determinar el resultado del partido
            local_goals, visitor_goals = map(int, score.split(':'))
            if local_goals > visitor_goals:
                result_indicator = 0  # Victoria del equipo local
            elif local_goals < visitor_goals:
                result_indicator = 2  # Victoria del equipo visitante
            else:
                result_indicator = 1  # Empate

            # Calcular el número total de goles
            total_goals = local_goals + visitor_goals

            # Agregar la información de estadísticas al resultado del partido
            enriched_results.append([
                teams,  # 'manchestercity_arsenal'
                score,  # '1:1'
                jornada,  # '13'
                team1_points,
                team2_points,
                team1_market_value,  # Valor plantilla manchester city
                team2_market_value,  # Valor plantilla arsenal
                team1_possession,  # Posesión manchester city
                team2_possession,  # Posesión arsenal
                team1_goals,  # Goles a favor manchester city antes de la jornada 13
                team2_goals,  # Goles a favor arsenal antes de la jornada 13
                team1_goalsagainst,  # Goles en contra manchester city
                team2_goalsagainst,  # Goles en contra arsenal
                team1_xgoals,  # Expected goals manchester city
                team2_xgoals,  # Expected goals arsenal
                team1_xgoalsagainst,  # Expected goals en contra manchester city
                team2_xgoalsagainst,  # Expected goals en contra arsenal
                result_indicator,  # Indicador de resultado del partido
                total_goals  # Total de goles marcados en el partido
            ])

        # Guardar los resultados enriquecidos en el nuevo diccionario
        enriched_results_by_season[season] = enriched_results

    return enriched_results_by_season
def unify_team_keys(dictionaries, seasons):
    for dictionary in dictionaries:
        for season in seasons:
            keys_to_modify = list(dictionary[season].keys())
            for team in keys_to_modify:
                # Convertir a minúsculas y eliminar espacios y puntos
                clean_team = re.sub(r"[ .]", "", team.lower())

                # Aplicar reemplazos específicos si el nombre limpio no contiene ya el reemplazo completo
                for abbrev, full_name in team_replacements.items():
                    if abbrev in clean_team and full_name not in clean_team:
                        clean_team = clean_team.replace(abbrev, full_name)

                clean_team = re.sub(r"^(fc|afc)|(?:fc|afc)$", "", clean_team)
                for abbrev, full_name in team_replacements.items():
                    if abbrev in clean_team and full_name not in clean_team:
                        clean_team = clean_team.replace(abbrev, full_name)
                # Asignar el valor a la clave limpia y eliminar la clave original
                dictionary[season][clean_team] = dictionary[season].pop(team)


def check_unique_teams(dicts_to_clean):
    unique_teams = set()
    # Recorrer cada diccionario y cada temporada para obtener los nombres de equipos
    for dictionary in dicts_to_clean:
        for season, teams in dictionary.items():
            unique_teams.update(teams.keys())  # Añadir equipos únicos

    # Imprimir nombres de equipos sin duplicados
    for team in sorted(unique_teams):
        print(team)


def clean_team_name(team_name):
    # Convertir a minúsculas y eliminar espacios y puntos
    clean_team = re.sub(r"[ .-]", "", team_name.lower())
    # Eliminar 'fc' y 'afc' si están al principio o al final
    clean_team = re.sub(r"^(fc|afc)|(?:fc|afc)$", "", clean_team)
    # Aplicar reemplazos específicos
    for abbrev, full_name in team_replacements.items():
        if abbrev in clean_team and full_name not in clean_team:
            clean_team = clean_team.replace(abbrev, full_name)
    return clean_team

def store_results_by_season(season, results_by_season):

    # Scrapear resultados de la temporada
    results = scrap_matrix_results(season=season)

    # Limpiar los nombres de los equipos en los resultados
    cleaned_results = []
    for match in results:
        teams, score, jornada = match
        team1, team2 = teams.split("_")
        cleaned_team1 = clean_team_name(team1)
        cleaned_team2 = clean_team_name(team2)
        cleaned_results.append([f"{cleaned_team1}_{cleaned_team2}", score, jornada])

    # Guardar los resultados limpios en el diccionario
    results_by_season[season] = cleaned_results
    return results_by_season



def scrap_clean_sheets(season, clubs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    next_year = str(int(season.split("/")[0]) + 2001)
    middle = last_year + "-" + next_year
    url_base = f"https://fbref.com/en/comps/9/{middle}/misc/{middle}-Premier-League-Stats"
    response = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra la tabla que contiene la información deseada
    tabla_equipos = soup.find("table", {"class": "stats_table"})

    if not tabla_equipos:
        return {}

    # Procesa las filas para extraer los equipos y su posesión
    filas = tabla_equipos.find_all("tr")
    for fila in filas[2:]:  # Salta la primera fila que contiene los encabezados %RECOVERIES
        columnas = fila.find_all("td")
        if len(columnas) < 3:  # Asegúrate de que hay suficientes columnas
            continue

        nombre_equipo = fila.find("th", {"data-stat": "team"}).text.strip()  # Accede al nombre del equipo
        posesion = columnas[15].text.strip()  # La columna de posesión suele ser la tercera

        # Convertir la posesión a float después de limpiar el texto
        posesion = float(posesion.replace("%", "").strip())

        # Guardar en el diccionario clubs
        if season not in clubs:
            clubs[season] = {}
        clubs[season][nombre_equipo] = posesion

    return clubs

def scrapp_recoveries_per_team(season, clubs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    next_year = str(int(season.split("/")[0]) + 2001)
    middle = last_year + "-" + next_year
    url_base = f"https://fbref.com/en/comps/9/{middle}/misc/{middle}-Premier-League-Stats"
    response = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra la tabla que contiene la información deseada
    tabla_equipos = soup.find("table", {"class": "stats_table"})

    if not tabla_equipos:
        return {}

    # Procesa las filas para extraer los equipos y su posesión
    filas = tabla_equipos.find_all("tr")
    for fila in filas[2:]:  # Salta la primera fila que contiene los encabezados %RECOVERIES
        columnas = fila.find_all("td")
        if len(columnas) < 3:  # Asegúrate de que hay suficientes columnas
            continue

        nombre_equipo = fila.find("th", {"data-stat": "team"}).text.strip()  # Accede al nombre del equipo
        posesion = columnas[14].text.strip()  # La columna de posesión suele ser la tercera

        # Convertir la posesión a float después de limpiar el texto
        posesion = float(posesion.replace("%", "").strip())

        # Guardar en el diccionario clubs
        if season not in clubs:
            clubs[season] = {}
        clubs[season][nombre_equipo] = posesion

    return clubs

def scrap_meanage(season, clubs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    next_year = str(int(season.split("/")[0]) + 2001)
    middle = last_year + "-" + next_year
    url_base = f"https://fbref.com/en/comps/9/{middle}/stats/{middle}-Premier-League-Stats"
    response = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra la tabla que contiene la información deseada
    tabla_equipos = soup.find("table", {"class": "stats_table"})

    if not tabla_equipos:
        return {}

    # Procesa las filas para extraer los equipos y su posesión
    filas = tabla_equipos.find_all("tr")
    for fila in filas[2:]:  # Salta la primera fila que contiene los encabezados
        columnas = fila.find_all("td")
        if len(columnas) < 3:  # Asegúrate de que hay suficientes columnas
            continue

        nombre_equipo = fila.find("th", {"data-stat": "team"}).text.strip()  # Accede al nombre del equipo
        posesion = columnas[1].text.strip()  # La columna de posesión suele ser la tercera

        # Convertir la posesión a float después de limpiar el texto
        posesion = float(posesion.replace("%", "").strip())

        # Guardar en el diccionario clubs
        if season not in clubs:
            clubs[season] = {}
        clubs[season][nombre_equipo] = posesion

    return clubs


def scrapp_possession_per_team(season, clubs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    last_year = str(int(season.split("/")[0]) + 2000)
    next_year = str(int(season.split("/")[0]) + 2001)
    middle = last_year + "-" + next_year
    url_base = f"https://fbref.com/en/comps/9/{middle}/possession/{middle}-Premier-League-Stats"
    response = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra la tabla que contiene la información deseada
    tabla_equipos = soup.find("table", {"class": "stats_table"})

    if not tabla_equipos:
        return {}

    # Procesa las filas para extraer los equipos y su posesión
    filas = tabla_equipos.find_all("tr")
    for fila in filas[2:]:  # Salta la primera fila que contiene los encabezados
        columnas = fila.find_all("td")
        if len(columnas) < 3:  # Asegúrate de que hay suficientes columnas
            continue

        nombre_equipo = fila.find("th", {"data-stat": "team"}).text.strip()  # Accede al nombre del equipo
        posesion = columnas[1].text.strip()  # La columna de posesión suele ser la tercera

        # Convertir la posesión a float después de limpiar el texto
        posesion = float(posesion.replace("%", "").strip())

        # Guardar en el diccionario clubs
        if season not in clubs:
            clubs[season] = {}
        clubs[season][nombre_equipo] = posesion

    return clubs

def scrap_xgoalsagainst(season,xg_by_season_club):
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
            xg_by_season_club[season][home_team].append(away_xg)
            xg_by_season_club[season][away_team].append(home_xg)
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
def scrap_goalsagainst(season,goalsbyseason):

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
            goalsbyseason[season][home_team].append(away_xg)
            goalsbyseason[season][away_team].append(home_xg)
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

    return clubs

for season in seasons:
    market_values = scrapp_season_teams_value(season=season,clubs=market_values)
    #print(market_values)
    results = scrap_matrix_results(season=season)
    results_by_season = store_results_by_season(season=season, results_by_season=results_by_season)
    xgoalsbyseason = scrap_xgoals(season=season,xg_by_season_club=xgoalsbyseason)
    goalsbyseason= scrap_goals(season=season, goalsbyseason=goalsbyseason)
    goalsagainstbyseason = scrap_goalsagainst(season=season, goalsbyseason=goalsagainstbyseason)
    xgoalsagainstbyseason = scrap_xgoalsagainst(season=season, xg_by_season_club= xgoalsagainstbyseason)
    possession = scrapp_possession_per_team(season=season, clubs=possession)
    recoveries = scrapp_recoveries_per_team(season= season, clubs=recoveries)
    pointsbyseason = scrap_points(season=season, pointsbyseason=pointsbyseason)
    cleansheets = scrap_clean_sheets(season=season, pointsbyseason=cleansheets)
    streaks = scrap_streak(season=season, pointsbyseason=streaks)
    meanage = scrap_meanage(season=season, pointsbyseason=meanage)

#print(results_by_season)
dictionaries = [market_values, xgoalsbyseason, goalsbyseason, goalsagainstbyseason, xgoalsagainstbyseason, possession, pointsbyseason]
unify_team_keys(dictionaries=dictionaries, seasons=seasons)
check_unique_teams(dicts_to_clean=dictionaries)
enriched_results = enrich_results_with_stats(results_by_season=results_by_season,market_values=market_values, possession= possession, goalsbyseason=goalsbyseason, goalsagainstbyseason=goalsagainstbyseason, xgoalsbyseason=xgoalsbyseason, xgoalsagainstbyseason=xgoalsagainstbyseason, pointsbyseason= pointsbyseason)
create_mat_file(enriched_results_by_season=enriched_results)
create_mat_file_with_V(enriched_results_by_season=enriched_results)
