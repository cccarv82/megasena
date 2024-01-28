import requests
import json
import time
import random
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
quad_frequency_map = Counter()  # Changed from pair_frequency_map
quad_trend_map = defaultdict(list)  # Changed from pair_trend_map

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

def update_quad_frequencies(numbers: List[int]):  # Changed from update_pair_frequencies
    for quad in combinations(numbers, 4):  # Changed from 2 to 4
        sorted_quad = tuple(sorted(quad))  # Changed from pair to quad
        quad_frequency_map.update([sorted_quad])  # Changed from pair_frequency_map
        quad_trend_map[sorted_quad].append(quad_frequency_map[sorted_quad])  # Changed from pair_trend_map

def calculate_trends():
    quad_trends = {}  # Changed from pair_trends
    for quad, frequencies in quad_trend_map.items():  # Changed from pair_trend_map
        trend = frequencies[-1] - frequencies[0]  # change in frequency
        quad_trends[quad] = trend  # Changed from pair_trends
    return quad_trends  # Changed from pair_trends

def generate_game(quad_trends: Dict[tuple, int]) -> List[int]:  # Changed from pair_trends
    game = []
    sorted_quads = sorted(quad_trends.items(), key=lambda x: x[1], reverse=True)  # Changed from pair_trends
    while len(game) < qtdeDezenas and sorted_quads:
        quad, _ = sorted_quads.pop(0)  # Changed from pair to quad
        for number in quad:  # Changed from pair to quad
            if number not in game:
                game.append(number)
    return sorted(game)

def generate_games(quad_trends: Dict[tuple, int]) -> List[List[int]]:  # Changed from pair_trends
    games = []
    while len(games) < qtdeJogos:
        game = generate_game(quad_trends)  # Changed from pair_trends
        if game not in games:
            games.append(game)
    return games

def simulate_draw(quad_trends: Dict[tuple, int]) -> List[int]:  # Changed from pair_trends
    return generate_game(quad_trends)  # Changed from pair_trends

def simulate_draws(quad_trends: Dict[tuple, int], games: List[List[int]]) -> float:  # Changed from pair_trends
    success_count = 0
    for _ in range(simulation_count):
        draw = set(simulate_draw(quad_trends))  # Changed from pair_trends
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
        update_quad_frequencies(dezenas)  # Changed from update_pair_frequencies
        time.sleep(1)

    print("Dados coletados. Calculando tendências...")
    quad_trends = calculate_trends()  # Changed from pair_trends

    print("Tendências calculadas. Gerando jogos...")
    games = generate_games(quad_trends)  # Changed from pair_trends

    print("Jogos gerados. Simulando sorteios...")
    success_rate = simulate_draws(quad_trends, games)  # Changed from pair_trends

    print(f'Taxa de sucesso: {success_rate * 100}%')

    with open('jogos.json', 'w') as f:
        json.dump(games, f, indent=2)

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()