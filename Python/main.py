import requests
import json
import time
import random
import pickle
from tqdm import tqdm
from collections import Counter, defaultdict
from typing import List, Dict
from itertools import combinations

requests.packages.urllib3.disable_warnings()

with open('jogos.json', 'w') as f:
    f.write('')

concurso_atual = 2681
concurso_antigo = 1
total = concurso_atual - concurso_antigo + 1
qtdeJogos = 10
qtdeDezenas = 7
simulation_count = 2000

number_frequency_map = Counter()
trio_frequency_map = Counter()  # Changed from quad_frequency_map
trio_trend_map = defaultdict(list)  # Changed from quad_trend_map

def save_state(state, filename):
    with open(filename, 'wb') as f:
        pickle.dump(state, f)

def load_state(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
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


def update_trio_frequencies(numbers: List[int]):  # Changed from update_quad_frequencies
    for trio in combinations(numbers, 3):  # Changed from 4 to 3
        sorted_trio = tuple(sorted(trio))  # Changed from quad to trio
        trio_frequency_map.update([sorted_trio])  # Changed from quad_frequency_map
        trio_trend_map[sorted_trio].append(trio_frequency_map[sorted_trio])  # Changed from quad_trend_map

def calculate_trends():
    trio_trends = {}  # Changed from quad_trends
    for trio, frequencies in trio_trend_map.items():  # Changed from quad_trend_map
        trend = frequencies[-1] - frequencies[0]  # change in frequency
        trio_trends[trio] = trend  # Changed from quad_trends
    return trio_trends  # Changed from quad_trends

def generate_game(trio_trends: Dict[tuple, int]) -> List[int]:  # Changed from quad_trends
    game = []
    sorted_trios = sorted(trio_trends.items(), key=lambda x: x[1], reverse=True)  # Changed from quad_trends
    while len(game) < qtdeDezenas and sorted_trios:
        trio, _ = sorted_trios.pop(0)  # Changed from quad to trio
        for number in trio:  # Changed from quad to trio
            if number not in game:
                game.append(number)
    return sorted(game)

def generate_games(trio_trends: Dict[tuple, int]) -> List[List[int]]:  # Changed from quad_trends
    games = set()
    pbar = tqdm(total=qtdeJogos, desc="Generating games", ncols=100)  # Create a progress bar
    while len(games) < qtdeJogos:
        game = tuple(sorted(generate_game(trio_trends)))  # Changed from quad_trends
        games.add(game)
        pbar.update(len(games) - pbar.n)  # Update the progress bar
    pbar.close()
    return [list(game) for game in games]

def simulate_draw(trio_trends: Dict[tuple, int]) -> List[int]:  # Changed from quad_trends
    return generate_game(trio_trends)  # Changed from quad_trends

def simulate_draws(trio_trends: Dict[tuple, int], games: List[List[int]]) -> float:  # Changed from quad_trends
    success_count = 0
    for _ in range(simulation_count):
        draw = set(simulate_draw(trio_trends))  # Changed from quad_trends
        for game in games:
            if set(game).issubset(draw):
                success_count += 1
                break
    return success_count / simulation_count

def main():
    print("Iniciando a coleta de dados...")
    for concurso in tqdm(range(concurso_antigo, concurso_atual + 1)):
        dezenas = get_concurso_data(concurso)
        number_frequency_map.update(dezenas)
        update_trio_frequencies(dezenas)  # Changed from update_quad_frequencies
        time.sleep(1)

    print("Dados coletados. Calculando tendências...")
    trio_trends = calculate_trends()  # Changed from quad_trends

    print("Tendências calculadas. Gerando jogos...")
    games = generate_games(trio_trends)  # Changed from quad_trends

    print("Jogos gerados. Simulando sorteios...")
    success_rate = simulate_draws(trio_trends, games)  # Changed from quad_trends

    print(f'Taxa de sucesso: {success_rate * 100}%')

    with open('jogos.json', 'w') as f:
        json.dump(games, f, indent=2)

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()