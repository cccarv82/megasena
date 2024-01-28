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
concurso_antigo = 2000
total = concurso_atual - concurso_antigo + 1
qtdeJogos = 10
qtdeDezenas = 7
simulation_count = 1000

number_frequency_map = Counter()
pair_frequency_map = Counter()
pair_trend_map = defaultdict(list)

def get_concurso_data(concurso: int) -> List[int]:
    response = requests.get(f'https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{concurso}', verify=False)
    if response.status_code == 200 and response.text.strip():
        data = response.json()
        return data.get('dezenasSorteadasOrdemSorteio', [])
    else:
        return []

def update_pair_frequencies(numbers: List[int]):
    for pair in combinations(numbers, 2):
        sorted_pair = tuple(sorted(pair))
        pair_frequency_map.update([sorted_pair])
        pair_trend_map[sorted_pair].append(pair_frequency_map[sorted_pair])

def calculate_trends():
    pair_trends = {}
    for pair, frequencies in pair_trend_map.items():
        trend = frequencies[-1] - frequencies[0]  # change in frequency
        pair_trends[pair] = trend
    return pair_trends

def generate_game(pair_trends: Dict[tuple, int]) -> List[int]:
    game = []
    sorted_pairs = sorted(pair_trends.items(), key=lambda x: x[1], reverse=True)
    while len(game) < qtdeDezenas and sorted_pairs:
        pair, _ = sorted_pairs.pop(0)
        for number in pair:
            if number not in game:
                game.append(number)
    return sorted(game)

def generate_games(pair_trends: Dict[tuple, int]) -> List[List[int]]:
    games = []
    while len(games) < qtdeJogos:
        game = generate_game(pair_trends)
        if game not in games:
            games.append(game)
    return games

def simulate_draw(pair_trends: Dict[tuple, int]) -> List[int]:
    return generate_game(pair_trends)

def simulate_draws(pair_trends: Dict[tuple, int], games: List[List[int]]) -> float:
    success_count = 0
    for _ in range(simulation_count):
        draw = set(simulate_draw(pair_trends))
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
        update_pair_frequencies(dezenas)
        time.sleep(1)

    print("Dados coletados. Calculando tendências...")
    pair_trends = calculate_trends()

    print("Tendências calculadas. Gerando jogos...")
    games = generate_games(pair_trends)

    print("Jogos gerados. Simulando sorteios...")
    success_rate = simulate_draws(pair_trends, games)

    print(f'Taxa de sucesso: {success_rate * 100}%')

    with open('jogos.json', 'w') as f:
        json.dump(games, f, indent=2)

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()