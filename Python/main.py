import requests
import json
import time
from tqdm import tqdm
from collections import Counter
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

number_frequency_map = Counter()
pair_frequency_map = Counter()

def get_concurso_data(concurso: int) -> List[int]:
    response = requests.get(f'https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{concurso}', verify=False)
    if response.status_code == 200 and response.text.strip():
        data = response.json()
        return data.get('dezenasSorteadasOrdemSorteio', [])
    else:
        return []

def update_pair_frequencies(numbers: List[int]):
    for pair in combinations(numbers, 2):
        pair_frequency_map.update([tuple(sorted(pair))])

def generate_game(pair_frequencies: List[Dict[str, int]]) -> List[int]:
    game = []
    while len(game) < qtdeDezenas:
        if not pair_frequencies:  # check if pair_frequencies is empty
            break
        random_pair = pair_frequencies.pop(0)['pair']
        for number in random_pair:
            if number not in game:
                game.append(number)
    return sorted(game)

def generate_games(pair_frequencies: List[Dict[str, int]]) -> List[List[int]]:
    games = []
    while len(games) < qtdeJogos:
        game = generate_game(pair_frequencies)
        if game not in games:
            games.append(game)
    return games

def main():
    print("Iniciando a coleta de dados...")
    for concurso in tqdm(range(concurso_antigo, concurso_atual + 1)):
        dezenas = get_concurso_data(concurso)
        number_frequency_map.update(dezenas)
        update_pair_frequencies(dezenas)
        time.sleep(1)

    print("Dados coletados. Gerando jogos...")
    pair_frequencies = [{'pair': k, 'frequency': v} for k, v in pair_frequency_map.items()]
    pair_frequencies.sort(key=lambda x: x['frequency'], reverse=True)

    games = generate_games(pair_frequencies)

    with open('jogos.json', 'w') as f:
        json.dump(games, f, indent=2)

    print('Jogos criados com sucesso!')

if __name__ == "__main__":
    main()