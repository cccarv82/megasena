// Importações
import * as fs from 'fs';
import axios from 'axios';
const ProgressBar = require('progress');

// Desativando a verificação de certificado SSL
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0";

// Limpando o arquivo jogos.json
fs.writeFileSync('jogos.json', '');

// Definindo as interfaces
interface Response {
    dezenasSorteadasOrdemSorteio: string[];
}

interface NumberFrequency {
    number: number;
    frequency: number;
}
// Função principal
async function main() {
    // Mapa para armazenar a frequência de cada número
    const numberFrequencyMap: { [key: number]: number } = {};

    // Definindo o concurso atual e o concurso antigo
    const concursoAtual = 2664;
    const concursoAntigo = 2600;
    const total = concursoAtual - concursoAntigo + 1;

    // Criando a barra de progresso
    const bar = new ProgressBar(':bar :current/:total (:percent)', { total });
    // Loop para buscar os resultados de cada concurso
    for (let i = concursoAtual; i >= concursoAntigo; i--) {
        // Construindo a URL da API
        const url = `https://apiloterias.com.br/app/resultado?loteria=megasena&token=apiloterias.com.br&concurso=${i}`;

        // Fazendo a requisição HTTP
        try {
            const response = await axios.get<Response>(url);

            // Loop para contar a frequência de cada número
            for (const numberStr of response.data.dezenasSorteadasOrdemSorteio) {
                const number = parseInt(numberStr, 10);
                if (numberFrequencyMap[number]) {
                    numberFrequencyMap[number]++;
                } else {
                    numberFrequencyMap[number] = 1;
                }
            }
        } catch (err) {
            console.error(`Falha na requisição HTTP. Erro: ${err}`);
        }

        // Atualizando a barra de progresso
        bar.tick();
    }
        // Convertendo o mapa de frequência de números em um array de objetos
        const numberFrequencies: NumberFrequency[] = Object.entries(numberFrequencyMap).map(([number, frequency]) => ({
            number: parseInt(number, 10),
            frequency,
        }));
    
        // Ordenando o array de objetos por frequência (decrescente) e número (crescente)
        numberFrequencies.sort((a, b) => b.frequency - a.frequency || a.number - b.number);
    
        // Função para verificar se um jogo já existe na lista de jogos
        function contains(game: number[], list: number[][]): boolean {
            for (let i = 0; i < list.length; i++) {
                if (list[i].length === game.length && list[i].every((value, index) => value === game[index])) {
                    return true;
                }
            }
            return false;
        }
        // Definindo a quantidade de jogos e a quantidade de dezenas de cada jogo
        const qtdeJogos = 10;
        const qtdeDezenas = 7;

        // Função para gerar um jogo
        function generateGame(numberFrequencies: NumberFrequency[]): number[] {
            const game: number[] = [];
            while (game.length < qtdeDezenas) {
                const randomNumber = Math.floor(Math.random() * numberFrequencies.length);
                const number = numberFrequencies[randomNumber].number;
                if (!game.includes(number)) {
                    game.push(number);
                }
            }
            return game.sort((a, b) => a - b);
        }

        // Função para gerar jogos
        function generateGames(numberFrequencies: NumberFrequency[]): number[][] {
            const games: number[][] = [];
            while (games.length < qtdeJogos) {
                const game = generateGame(numberFrequencies);
                if (!contains(game, games)) {
                    games.push(game);
                }
            }
            return games;
        }

        // Gerando jogos
        const games = generateGames(numberFrequencies);

        // Escrevendo os jogos no arquivo jogos.json
        fs.writeFileSync('jogos.json', JSON.stringify(games, null, 2));

        console.log('Jogos criados com sucesso!');
    
    // Chamando a função principal
    main();