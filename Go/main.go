// Importando os pacotes necessários
package main

import (
	"crypto/tls"    // Pacote para lidar com segurança TLS
	"encoding/json" // Pacote para lidar com JSON
	"fmt"           // Pacote para formatação de I/O
	"io/ioutil"     // Pacote para lidar com I/O
	"math/rand"     // Pacote para gerar números aleatórios
	"net/http"      // Pacote para lidar com requisições HTTP
	"os"            // Pacote para lidar com sistema operacional
	"sort"          // Pacote para ordenação
	"strconv"       // Pacote para conversão de string
	"time"          // Pacote para lidar com tempo

	"github.com/spf13/cobra" // Pacote externo para criar linha de comando
	"github.com/vbauerster/mpb"
	"github.com/vbauerster/mpb/decor"
)

// Estrutura para armazenar a resposta da API
type Response struct {
    DezenasSorteadasOrdemSorteio []string `json:"dezenasSorteadasOrdemSorteio"`
}

// Estrutura para armazenar a frequência de cada número
type NumberFrequency struct {
    Number    int
    Frequency int
}
// Função para verificar se um jogo já existe na lista de jogos
func contains(s [][]int, e []int) bool {
    for _, a := range s {
        if len(a) != len(e) {
            continue
        }
        match := true
        for i, v := range a {
            if v != e[i] {
                match = false
                break
            }
        }
        if match {
            return true
        }
    }
    return false
}
// Definindo o comando principal do programa
var rootCmd = &cobra.Command{
    Use:   "megasena",
    Short: "Capturando Informações para ganhar na Mega-Sena",
    Run: func(cmd *cobra.Command, args []string) {
        // Mapa para armazenar a frequência de cada número
        numberFrequencyMap := make(map[int]int)

        // Configurando o cliente HTTP para ignorar a verificação de certificado SSL
        http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}
        // Definindo o concurso atual e o concurso antigo
        concursoAtual := 2664
        concursoAntigo := 1
        total := concursoAtual - concursoAntigo + 1

        p := mpb.New(mpb.WithWidth(64))
        bar := p.AddBar(int64(total),
            mpb.PrependDecorators(
                decor.Name("Progresso: "),
                decor.CountersNoUnit("%d / %d", decor.WCSyncWidth),
            ),
            mpb.AppendDecorators(
                decor.Percentage(decor.WCSyncWidth),
            ),
        )

        // Loop para buscar os resultados de cada concurso
        for i := concursoAtual; i >= concursoAntigo; i-- {
            // Construindo a URL da API
            url := fmt.Sprintf("https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/%d", i)
            // Fazendo a requisição HTTP
            resp, err := http.Get(url)
            if err != nil {
                fmt.Println("Falha na requisição HTTP. Erro:", err)
                continue
            }

            // Lendo o corpo da resposta
            body, _ := ioutil.ReadAll(resp.Body)
            resp.Body.Close()

            // Decodificando o corpo da resposta
            var response Response
            err = json.Unmarshal(body, &response)
            if err != nil {
                fmt.Println("Falha na decodificação das informações. Erro:", err)
                continue
            }
            // Loop para contar a frequência de cada número
            for _, numberStr := range response.DezenasSorteadasOrdemSorteio {
                number, err := strconv.Atoi(numberStr)
                if err != nil {
                    fmt.Println("Falha na conversão do número. Erro:", err)
                    continue
                }
                numberFrequencyMap[number]++
            }
            bar.Increment()
        }
        p.Wait()
        // Criando uma lista para armazenar a frequência de cada número
        numberFrequencies := make([]NumberFrequency, 0, len(numberFrequencyMap))
        for number, frequency := range numberFrequencyMap {
            numberFrequencies = append(numberFrequencies, NumberFrequency{Number: number, Frequency: frequency})
        }

        // Ordenando a lista de frequências em ordem decrescente
        sort.Slice(numberFrequencies, func(i, j int) bool {
            return numberFrequencies[i].Frequency > numberFrequencies[j].Frequency
        })
        // Criando uma lista para armazenar os 15 números mais frequentes
        var top15 []int
        if len(numberFrequencies) >= 15 {
            for _, nf := range numberFrequencies[:15] {
                top15 = append(top15, nf.Number)
            }
        } else {
            for _, nf := range numberFrequencies {
                top15 = append(top15, nf.Number)
            }
        }
        // Definindo a quantidade de dezenas por jogo e a quantidade de jogos
        qtdeDezenas := 7
        qtdeJogos := 10

        // Inicializando o gerador de números aleatórios
        rand.Seed(time.Now().UnixNano())
                // Criando uma lista para armazenar os jogos
                var games [][]int
                for i := 0; i < qtdeJogos; {
                    // Gerando uma permutação aleatória dos 15 números mais frequentes
                    perm := rand.Perm(15)
                    var game []int
                    // Selecionando as primeiras 'qtdeDezenas' dezenas da permutação
                    for _, v := range perm[:qtdeDezenas] {
                        game = append(game, top15[v])
                    }
                    // Verificando se o jogo já existe na lista de jogos
                    if !contains(games, game) {
                        // Adicionando o jogo à lista de jogos
                        games = append(games, game)
                        i++
                    }
                }
        
            // Criando o arquivo JSON com os jogos
            file, _ := json.MarshalIndent(games, "", " ")
            err := ioutil.WriteFile("jogos.json", file, 0644)
            if err != nil {
                fmt.Println("Falha na criação dos jogos. Erro:", err)
            } else {
                fmt.Println("Jogos criados com sucesso!")
            }
    },
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Println(err)
        os.Exit(1)
    }
}

func main() {
    err := os.Truncate("jogos.json", 0)
    if err != nil {
        fmt.Println("Erro ao limpar o arquivo jogos.json:", err)
    }

    Execute()
}