"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
// Importações
var fs = require("fs");
var axios_1 = require("axios");
var ProgressBar = require('progress');
// Desativando a verificação de certificado SSL
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = "0";
// Limpando o arquivo jogos.json
fs.writeFileSync('jogos.json', '');
// Função principal
function main() {
    return __awaiter(this, void 0, void 0, function () {
        // Função para verificar se um jogo já existe na lista de jogos
        function contains(game, list) {
            for (var i = 0; i < list.length; i++) {
                if (list[i].length === game.length && list[i].every(function (value, index) { return value === game[index]; })) {
                    return true;
                }
            }
            return false;
        }
        // Função para gerar um jogo
        function generateGame(numberFrequencies) {
            var game = [];
            while (game.length < 6) {
                var randomNumber = Math.floor(Math.random() * numberFrequencies.length);
                var number = numberFrequencies[randomNumber].number;
                if (!game.includes(number)) {
                    game.push(number);
                }
            }
            return game.sort(function (a, b) { return a - b; });
        }
        // Função para gerar jogos
        function generateGames(numberFrequencies, numberOfGames) {
            var games = [];
            while (games.length < numberOfGames) {
                var game = generateGame(numberFrequencies);
                if (!contains(game, games)) {
                    games.push(game);
                }
            }
            return games;
        }
        var numberFrequencyMap, concursoAtual, concursoAntigo, total, bar, i, url, response, _i, _a, numberStr, number, err_1, numberFrequencies, games;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    numberFrequencyMap = {};
                    concursoAtual = 2664;
                    concursoAntigo = 2600;
                    total = concursoAtual - concursoAntigo + 1;
                    bar = new ProgressBar(':bar :current/:total (:percent)', { total: total });
                    i = concursoAtual;
                    _b.label = 1;
                case 1:
                    if (!(i >= concursoAntigo)) return [3 /*break*/, 7];
                    url = "https://apiloterias.com.br/app/resultado?loteria=megasena&token=apiloterias.com.br&concurso=".concat(i);
                    _b.label = 2;
                case 2:
                    _b.trys.push([2, 4, , 5]);
                    return [4 /*yield*/, axios_1["default"].get(url)];
                case 3:
                    response = _b.sent();
                    // Loop para contar a frequência de cada número
                    for (_i = 0, _a = response.data.dezenasSorteadasOrdemSorteio; _i < _a.length; _i++) {
                        numberStr = _a[_i];
                        number = parseInt(numberStr, 10);
                        if (numberFrequencyMap[number]) {
                            numberFrequencyMap[number]++;
                        }
                        else {
                            numberFrequencyMap[number] = 1;
                        }
                    }
                    return [3 /*break*/, 5];
                case 4:
                    err_1 = _b.sent();
                    console.error("Falha na requisi\u00E7\u00E3o HTTP. Erro: ".concat(err_1));
                    return [3 /*break*/, 5];
                case 5:
                    // Atualizando a barra de progresso
                    bar.tick();
                    _b.label = 6;
                case 6:
                    i--;
                    return [3 /*break*/, 1];
                case 7:
                    numberFrequencies = Object.entries(numberFrequencyMap).map(function (_a) {
                        var number = _a[0], frequency = _a[1];
                        return ({
                            number: parseInt(number, 10),
                            frequency: frequency
                        });
                    });
                    // Ordenando o array de objetos por frequência (decrescente) e número (crescente)
                    numberFrequencies.sort(function (a, b) { return b.frequency - a.frequency || a.number - b.number; });
                    games = generateGames(numberFrequencies, 10);
                    // Escrevendo os jogos no arquivo jogos.json
                    fs.writeFileSync('jogos.json', JSON.stringify(games, null, 2));
                    console.log('Jogos criados com sucesso!');
                    return [2 /*return*/];
            }
        });
    });
}
// Chamando a função principal
main();
