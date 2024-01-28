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

concurso_atual = 2600
concurso_antigo = 1
total = concurso_atual - concurso_antigo + 1
qtdeJogos = 10
qtdeDezenas = 7
simulation_count = 2000

number_frequency_map = Counter()
trio_frequency_map = Counter()
trio_trend_map = defaultdict(list)

def get_concurso_data(concurso: int) -> List[int]:
    for _ in range(5):  # Try up to 5 times
        try:
            response = requests.get(f'https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{concurso}', verify=False)
            if response.status_code == 200 and response.text.strip():
                data = response.json()
                return data.get('dezenasSorteadasOrdemSorteio', [])
            else:
                return []
        except requests.exceptions.RequestException:
            time.sleep(5)  # Wait for 5 seconds before trying again
    return []  # Return empty list if all attempts fail

def update_trio_frequencies(numbers: List[int]):
    for trio in combinations(numbers, 3):
        sorted_trio = tuple(sorted(trio))
        trio_frequency_map.update([sorted_trio])
        trio_trend_map[sorted_trio].append(trio_frequency_map[sorted_trio])

def calculate_trends():
    trio_trends = {}
    for trio, frequencies in trio_trend_map.items():
        trend = frequencies[-1] - frequencies[0]  # change in frequency
        trio_trends[trio] = trend
    return trio_trends

def generate_game(trio_trends: Dict[tuple, int]) -> List[int]:
    game = []
    sorted_trios = sorted(trio_trends.items(), key=lambda x: x[1], reverse=True)
    while len(game) < qtdeDezenas and sorted_trios:
        trio, _ = sorted_trios.pop(0)
        for number in trio:
            if number not in game:
                game.append(number)
    return sorted(game)

def generate_games(trio_trends: Dict[tuple, int]) -> List[List[int]]:
    games = set()
    pbar = tqdm(total=qtdeJogos, desc="Generating games", ncols=100)  # Create a progress bar
    while len(games) < qtdeJogos:
        game = tuple(sorted(generate_game(trio_trends)))
        games.add(game)
        pbar.update(len(games) - pbar.n)  # Update the progress bar
    pbar.close()
    return [list(game) for game in games]

def simulate_draw(trio_trends: Dict[tuple, int]) -> List[int]:
    return generate_game(trio_trends)

def simulate_draws(trio_trends: Dict[tuple, int], games: List[List[int]]) -> float:
    success_count = 0
    games_set = [set(game) for game in games]  # Convert games to sets
    for _ in range(simulation_count):
        draw = set(simulate_draw(trio_trends))  # Convert draw to set
        for game_set in games_set:
            if game_set.issubset(draw):
                success_count += 1
                break
    return success_count / simulation_count

def main():
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

    concursos = range(concurso_antigo, concurso_atual + 1)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_concurso_data, concurso): concurso for concurso in concursos}
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

    # Print the number of unique numbers
    unique_numbers = set(number for trio in trio_trends for number in trio)
    print(f'Quantidade de números únicos para gerar os jogos: {len(unique_numbers)}')

    print("Tendências calculadas. Gerando jogos...")
    games = generate_games(trio_trends)

    print("Jogos gerados. Simulando sorteios...")
    success_rate = simulate_draws(trio_trends, games)

    print(f'Taxa de sucesso: {success_rate * 100}%')

    # Save games to the database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogo TEXT
        )
    ''')
    for game in games:
        cursor.execute('INSERT INTO jogos (jogo) VALUES (?)', (json.dumps(game),))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()