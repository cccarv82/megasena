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

requests.packages.urllib3.disable_warnings()

# concurso_atual = 2681
# concurso_antigo = 1
# total = concurso_atual - concurso_antigo + 1
# qtdeJogos = 70 # 1 jogo de 6 = 5 reais | 1 jogo de 7 = 35 reais
# qtdeDezenas = 6

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
    response = requests.get("https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/", verify=False)
    data = json.loads(response.text)
    return data['numeroConcursoAnterior'] + 1

def get_concurso_data(concurso_atual: int, concurso: int) -> List[int]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for attempt in range(5):  # Try up to 5 times
        try:
            response = requests.get(f'https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{concurso}', headers=headers, verify=False)
            if response.status_code == 200 and response.text.strip():
                data = response.json()
                return data.get('dezenasSorteadasOrdemSorteio', [])
            elif response.status_code == 500:
                time.sleep(5)  # Wait for 5 seconds before trying again
            else:
                print(f"Attempt {attempt + 1} failed with status code {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            time.sleep(5)  # Wait for 5 seconds before trying again
    return []  # Return empty list if all attempts fail

def update_trio_frequencies(numbers: List[int]):
    for trio in combinations(numbers, 6):
        sorted_trio = tuple(sorted(trio))
        trio_frequency_map.update([sorted_trio])
        trio_trend_map[sorted_trio].append(trio_frequency_map[sorted_trio])

def calculate_trends():
    trio_trends = {}
    for trio, frequencies in trio_trend_map.items():
        trend = frequencies[-1] - frequencies[0]  # change in frequency
        trio_trends[trio] = trend
    return trio_trends

def get_user_input():
    amount = float(input("Informe quantos Reais utilizará para jogar: R$ "))
    dezenas = int(input("Quantas dezenas cada jogo deve ter ? "))
    while dezenas < 6 or dezenas > 20 or amount < price_per_game_map[dezenas]:
        if dezenas < 6 or dezenas > 20:
            print("A quantidade de dezenas deve ser entre 6 e 20.")
        else:
            print(f"O valor mínimo para jogar com {dezenas} dezenas é R$ {price_per_game_map[dezenas]:.2f}")
        amount = float(input("Informe quantos Reais utilizará para jogar: R$ "))
        dezenas = int(input("Quantas dezenas cada jogo deve ter ? "))
    return amount, dezenas

def calculate_qtdeJogos(amount: float, dezenas: int) -> int:
    price_per_game = price_per_game_map.get(dezenas)
    if price_per_game is None:
        raise ValueError("Número de dezenas inválido")
    return int(amount // price_per_game)

def generate_game(trio_trends: Dict[tuple, int]) -> List[int]:
    game = []
    sorted_trios = sorted(trio_trends.items(), key=lambda x: x[1], reverse=True)
    while len(game) < qtdeDezenas and sorted_trios:
        trio, _ = random.choice(sorted_trios)  # Select a random trio
        sorted_trios.remove((trio, _))  # Remove the selected trio from the list
        for number in trio:
            if number not in game:
                game.append(number)
    return sorted(game)

def generate_games(trio_trends, qtdeJogos, qtdeDezenas):
    games = set()
    while len(games) < qtdeJogos:
        game = set()
        while len(game) < qtdeDezenas:
            trio = random.choice(list(trio_trends.keys()))
            game.update(trio)
            if len(game) > qtdeDezenas:
                game = set(list(game)[:qtdeDezenas])  # If the game has more than qtdeDezenas, trim it down
        games.add(tuple(sorted(list(game))))  # Add the game to the set of games
    return [list(game) for game in games]  # Convert the set of games back to a list of games

def simulate_draw(trio_trends: Dict[tuple, int]) -> List[int]:
    return generate_game(trio_trends)

def simulate_draws(trio_trends: Dict[tuple, int], games: List[List[int]], cursor) -> (float, float):
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
    return success_count_6 / total_draws, success_count_5 / total_draws, success_count_4 / total_draws

def load_concurso_data(cursor):
    cursor.execute('SELECT * FROM concursos')
    for row in cursor.fetchall():
        concurso, dezenas = row
        dezenas = json.loads(dezenas)
        number_frequency_map.update(dezenas)
        update_trio_frequencies(dezenas)

def main():
    concurso_atual = get_latest_concurso()
    concurso_antigo = 1
    total = concurso_atual - concurso_antigo + 1
    amount, dezenas = get_user_input()
    qtdeJogos = calculate_qtdeJogos(amount, dezenas)

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

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_concurso_data, concurso_atual, concurso): concurso for concurso in concursos}
        pbar = tqdm(total=len(concursos), desc="Coletando dados", ncols=100)  # Create a progress bar
        for future in as_completed(futures):
            concurso = futures[future]
            try:
                dezenas = future.result()
            except Exception as exc:
                print(f'Concurso {concurso} generated an exception: {exc}')
            else:
                if dezenas:
                    cursor.execute('INSERT INTO concursos (concurso, dezenas) VALUES (?, ?)', (concurso, json.dumps(dezenas)))
                    number_frequency_map.update(dezenas)
                    update_trio_frequencies(dezenas)
            pbar.update(1)  # Update the progress bar
        pbar.close()

    print("Dados coletados. Calculando tendências...")
    trio_trends = calculate_trends()


    print(f"Tendências calculadas. Gerando {qtdeJogos} jogos...")
    games = generate_games(trio_trends, qtdeJogos, dezenas)

    print(f"{qtdeJogos} Jogos gerados. Simulando sorteios...")
    success_rate_6, success_rate_5, success_rate_4 = simulate_draws(trio_trends, games, cursor)

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

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()