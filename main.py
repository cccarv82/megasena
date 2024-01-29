import requests
import json
import time
import random
import pickle
import sqlite3
from tqdm import tqdm
from collections import Counter, defaultdict
from typing import List, Dict
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import logging

requests.packages.urllib3.disable_warnings()

# Configura o logging
logging.basicConfig(filename='execution.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


number_frequency_map = Counter()
trio_frequency_map = Counter()
trio_trend_map = defaultdict(list)

price_per_game_map = {
    6: 5,
    7: 35,
    8: 140,
    9: 420,
    10: 1050,
    11: 2310,
    12: 4620,
    13: 8580,
    14: 15015,
    15: 25025,
    16: 40040,
    17: 61880,
    18: 92820,
    19: 135660,
    20: 193800
}

def get_latest_concurso():
    """
    This function sends a GET request to the MegaSena API to retrieve the latest 'concurso' (lottery draw).
    It returns the number of the next 'concurso'.
    """
    ...

    try:
        url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/"
        response = requests.get(url, verify=False)
        response.raise_for_status()  # This will raise an exception if the response is not OK
        logging.info('Starting get_latest_concurso\n' 
             f"Request URL: {url}\n"
             f"Response status: {response.status_code}\n"
             f"Response: {response}\n"
             f"Response text: {response.text}\n"
             f"Response json: {response.json()}\n"
             f"Response headers: {response.headers}\n"
             f"Response cookies: {response.cookies}\n"
             f"Response elapsed: {response.elapsed}\n"
             )
    except requests.exceptions.RequestException as e:
        print(f"Failed to get latest concurso: {e}")
        logging.error(f"Failed to get latest concurso: {e}")
        raise
    else:
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError(f"Unexpected response format: {data}")
        latest_concurso = data.get('numeroConcursoAnterior', 0) + 1
        logging.info(f"Latest concurso found: {latest_concurso}\n\n")
        logging.info('Finished get_latest_concurso\n\n')
        return latest_concurso

def get_concurso_data(concurso_atual: int, concurso: int) -> List[int]:
    """
    This function sends a GET request to the MegaSena API to retrieve the data for a specific 'concurso'.
    It returns a list of the 'dezenas' (numbers) drawn in the 'concurso'.
    """
    ...
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for attempt in range(5):  # Try up to 5 times
        try:
            url = f'https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{concurso}'
            response = requests.get(url, headers=headers, verify=False)
            logging.info(f'Starting get_concurso_data for concurso {concurso}\n'
                         f'Request URL: {url}\n'
                         f'Response status: {response.status_code}\n'
                         f'Response: {response}\n'
                         f'Response text: {response.text}\n'
                         f'Response json: {response.json()}\n'
                         f'Response headers: {response.headers}\n'
                         f'Response cookies: {response.cookies}\n'
                         f'Response elapsed: {response.elapsed}\n'
                         )
            if response.status_code == 200 and response.text.strip():
                data = response.json()
                dezenas = data.get('dezenasSorteadasOrdemSorteio', [])
                logging.info(f'Dezenas found for concurso {concurso}: {dezenas}\n\n')
                return dezenas
            elif response.status_code == 500:
                time.sleep(5)  # Wait for 5 seconds before trying again
            else:
                print(f"Attempt {attempt + 1} failed with status code {response.status_code}")
                logging.error(f"Attempt {attempt + 1} failed with status code {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            time.sleep(5)  # Wait for 5 seconds before trying again
            logging.error(f"Attempt {attempt + 1} failed with exception: {e}")
    logging.info('Finished get_concurso_data\n\n')
    return []  # Return empty list if all attempts fail

def update_trio_frequencies(numbers: List[int]):
    """
    This function updates the frequency maps for 'trios' (combinations of 3 numbers).
    It takes a list of numbers as input.
    """
    logging.info('Starting update_trio_frequencies\n'
                 f'Input numbers: {numbers}\n')
    ...
    for trio in combinations(numbers, 3):
        sorted_trio = tuple(sorted(trio))
        trio_frequency_map.update([sorted_trio])
        trio_trend_map[sorted_trio].append(trio_frequency_map[sorted_trio])
        logging.info(f'Updated trio: {sorted_trio}\n'
                     f'Current frequency: {trio_frequency_map[sorted_trio]}\n'
                     f'Current trend: {trio_trend_map[sorted_trio]}\n')
    logging.info('Finished update_trio_frequencies\n\n')

def calculate_trends():
    """
    This function calculates the trends for each 'trio' based on their frequencies.
    It returns a dictionary mapping each 'trio' to its trend.
    """
    logging.info('Starting calculate_trends\n')
    ...
    trio_trends = {}
    for trio, frequencies in trio_trend_map.items():
        trend = frequencies[-1] - frequencies[0]  # change in frequency
        trio_trends[trio] = trend
        logging.info(f'Calculated trend for trio {trio}: {trend}\n')
    logging.info('Finished calculate_trends\n\n')
    return trio_trends

def get_amount():
    """
    This function prompts the user to input the amount of money they want to use to play.
    It returns the amount as a float.
    """
    logging.info('Starting get_amount\n')
    ...
    amount = float(input("Informe quantos Reais utilizará para jogar: R$ "))
    while amount < 5:
        print("O valor mínimo para jogar é R$ 5.00")
        amount = float(input("Informe quantos Reais utilizará para jogar: R$ "))
    logging.info(f'Amount received: R$ {amount}\n')
    logging.info('Finished get_amount\n\n')
    return amount

def get_dezenas():
    """
    This function prompts the user to input the number of 'dezenas' (numbers) each game should have.
    It returns the number of 'dezenas' as an integer.
    """
    logging.info('Starting get_dezenas\n')
    ...
    dezenas = int(input("Quantas dezenas cada jogo deve ter ? "))
    while dezenas < 6 or dezenas > 20:
        print("A quantidade de dezenas deve ser entre 6 e 20.")
        dezenas = int(input("Quantas dezenas cada jogo deve ter ? "))
    logging.info(f'Number of dezenas received: {dezenas}\n')
    logging.info('Finished get_dezenas\n\n')
    return dezenas

def calculate_qtdeJogos(amount: float, dezenas: int) -> int:
    """
    This function calculates the number of games the user can play based on the amount of money they have and the number of 'dezenas' each game should have.
    It returns the number of games as an integer.
    """
    logging.info('Starting calculate_qtdeJogos\n'
                 f'Input amount: R$ {amount}\n'
                 f'Input dezenas: {dezenas}\n')
    ...
    price_per_game = price_per_game_map.get(dezenas)
    if price_per_game is None:
        logging.error('Invalid number of dezenas\n')
        raise ValueError("Número de dezenas inválido")
    qtdeJogos = int(amount // price_per_game)
    logging.info(f'Number of games calculated: {qtdeJogos}\n')
    logging.info('Finished calculate_qtdeJogos\n\n')
    return qtdeJogos

def generate_game(trio_trends: Dict[tuple, int]) -> List[int]:
    """
    This function generates a single game based on the trends of the 'trios'.
    It returns the game as a list of numbers.
    """
    logging.info('Starting generate_game\n'
                 f'Input trio_trends: {trio_trends}\n')
    ...
    game = []
    sorted_trios = sorted(trio_trends.items(), key=lambda x: x[1], reverse=True)
    while len(game) < sorted_trios:
        trio, _ = random.choice(sorted_trios)  # Select a random trio
        sorted_trios.remove((trio, _))  # Remove the selected trio from the list
        for number in trio:
            if number not in game:
                game.append(number)
        logging.info(f'Current game: {game}\n')
    logging.info(f'Final game: {sorted(game)}\n')
    logging.info('Finished generate_game\n\n')
    return sorted(game)

def generate_games(trio_trends, qtdeJogos, qtdeDezenas):
    """
    This function generates multiple games based on the trends of the 'trios'.
    It returns the games as a list of lists of numbers.
    """
    logging.info('Starting generate_games\n'
                 f'Input trio_trends: {trio_trends}\n'
                 f'Input qtdeJogos: {qtdeJogos}\n'
                 f'Input qtdeDezenas: {qtdeDezenas}\n')
    ...
    games = set()
    while len(games) < qtdeJogos:
        game = set()
        while len(game) < qtdeDezenas:
            trio = random.choice(list(trio_trends.keys()))
            game.update(trio)
            if len(game) > qtdeDezenas:
                game = set(list(game)[:qtdeDezenas])  # If the game has more than qtdeDezenas, trim it down
        games.add(tuple(sorted(list(game))))  # Add the game to the set of games
        logging.info(f'Current games: {games}\n')
    logging.info(f'Final games: {[list(game) for game in games]}\n')
    logging.info('Finished generate_games\n\n')
    return [list(game) for game in games]  # Convert the set of games back to a list of games

def simulate_draw(trio_trends: Dict[tuple, int]) -> List[int]:
    """
    This function simulates a single draw based on the trends of the 'trios'.
    It returns the draw as a list of numbers.
    """
    logging.info('Starting simulate_draw\n'
                 f'Input trio_trends: {trio_trends}\n')
    ...
    draw = generate_game(trio_trends)
    logging.info(f'Simulated draw: {draw}\n')
    logging.info('Finished simulate_draw\n\n')
    return draw

def simulate_draws(trio_trends: Dict[tuple, int], games: List[List[int]], cursor) -> (float, float):
    """
    This function simulates multiple draws based on the trends of the 'trios' and calculates the success rates for 6, 5, and 4 numbers.
    It returns the success rates as floats.
    """
    logging.info('Starting simulate_draws\n'
                 f'Input trio_trends: {trio_trends}\n'
                 f'Input games: {games}\n')
    ...
    success_count_6 = 0
    success_count_5 = 0
    success_count_4 = 0
    games_set = [set(game) for game in games]  # Convert games to sets

    # Get all the draws from the database
    cursor.execute('SELECT dezenas FROM concursos')
    all_draws = [set(json.loads(row[0])) for row in cursor.fetchall()]

    for draw in all_draws:
        for game_set in games_set:
            if game_set.issubset(draw):
                success_count_6 += 1
            if len(game_set.intersection(draw)) == 5:
                success_count_5 += 1
            if len(game_set.intersection(draw)) == 4:
                success_count_4 += 1

    total_draws = len(all_draws)
    logging.info(f'Success counts: 6 numbers - {success_count_6}, 5 numbers - {success_count_5}, 4 numbers - {success_count_4}\n')
    logging.info(f'Total draws: {total_draws}\n')
    logging.info('Finished simulate_draws\n\n')
    return success_count_6 / total_draws, success_count_5 / total_draws, success_count_4 / total_draws

def load_concurso_data(cursor):
    """
    This function loads the 'concurso' data from the SQLite database and updates the frequency maps.
    """
    logging.info('Starting load_concurso_data\n')
    ...
    cursor.execute('SELECT * FROM concursos')
    for row in cursor.fetchall():
        concurso, dezenas = row
        dezenas = json.loads(dezenas)
        number_frequency_map.update(dezenas)
        update_trio_frequencies(dezenas)
        logging.info(f'Loaded concurso {concurso} with dezenas {dezenas}\n')
    logging.info('Finished load_concurso_data\n\n')

def main():
    """
    This is the main function of the program. It orchestrates the entire process of collecting data, calculating trends, generating games, simulating draws, and saving the games to the database.
    """
    logging.info('Starting main\n')
    ...
    concurso_atual = get_latest_concurso()
    concurso_antigo = 1
    total = concurso_atual - concurso_antigo + 1
    amount = get_amount()
    dezenas = get_dezenas()
    qtdeJogos = calculate_qtdeJogos(amount, dezenas)

    logging.info(f'concurso_atual: {concurso_atual}, concurso_antigo: {concurso_antigo}, total: {total}, amount: {amount}, dezenas: {dezenas}, qtdeJogos: {qtdeJogos}\n')

    print("Iniciando a coleta de dados...")

    # Create a connection to the SQLite database
    conn = sqlite3.connect('lottery.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concursos (
            concurso INTEGER PRIMARY KEY,
            dezenas TEXT
        )
    ''')

    # Load the concurso data from the database
    load_concurso_data(cursor)

    # Get the list of concursos that are already in the database
    cursor.execute('SELECT concurso FROM concursos')
    existing_concursos = {row[0] for row in cursor.fetchall()}

    # Only download the concursos that are not already in the database
    concursos = [concurso for concurso in range(concurso_antigo, concurso_atual + 1) if concurso not in existing_concursos]

    logging.info(f'concursos to download: {concursos}\n')

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_concurso_data, concurso_atual, concurso): concurso for concurso in concursos}
        pbar = tqdm(total=len(concursos), desc="Coletando dados", ncols=100)  # Create a progress bar
        for future in as_completed(futures):
            concurso = futures[future]
            try:
                dezenas = future.result()
            except Exception as exc:
                logging.error(f'Concurso {concurso} generated an exception: {exc}\n')
            else:
                if dezenas:
                    cursor.execute('INSERT INTO concursos (concurso, dezenas) VALUES (?, ?)', (concurso, json.dumps(dezenas)))
                    number_frequency_map.update(dezenas)
                    update_trio_frequencies(dezenas)
            pbar.update(1)  # Update the progress bar
        pbar.close()

    print("Dados coletados. Calculando tendências...")
    trio_trends = calculate_trends()

    logging.info(f'trio_trends: {trio_trends}\n')

    print(f"Tendências calculadas. Gerando {qtdeJogos} jogos...")
    games = generate_games(trio_trends, qtdeJogos, dezenas)

    logging.info(f'games: {games}\n')

    print(f"{qtdeJogos} Jogos gerados. Simulando sorteios...")
    success_rate_6, success_rate_5, success_rate_4 = simulate_draws(trio_trends, games, cursor)

    logging.info(f'success_rate_6: {success_rate_6}, success_rate_5: {success_rate_5}, success_rate_4: {success_rate_4}\n')

    print(f'Taxa de sucesso para 6 números: {format(success_rate_6 * 100, ".2f")}%')
    print(f'Taxa de sucesso para 5 números: {format(success_rate_5 * 100, ".2f")}%')
    print(f'Taxa de sucesso para 4 números: {format(success_rate_4 * 100, ".2f")}%')

    # Save games to the database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogo TEXT
        )
    ''')

    # Clear the jogos table
    cursor.execute('DELETE FROM jogos')

    for game in games:
        cursor.execute('INSERT INTO jogos (jogo) VALUES (?)', (json.dumps(game),))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    logging.info('Finished main\n\n')

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()