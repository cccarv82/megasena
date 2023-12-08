// ##############################################################
// ## @Author: Carlos Carvalho                                 ##
// ##                                                          ##
// ##       Código meramente para fins educacionais            ##
// ##   Não utilizar para jogar na Mega-Sena, você perderá     ##
// ##                                                          ##
// ##############################################################

package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"sort"
	"strconv"
	"time"

	"github.com/spf13/cobra"
	"github.com/vbauerster/mpb/v7"
	"github.com/vbauerster/mpb/v7/decor"
)

type Response struct {
    DezenasSorteadasOrdemSorteio []string `json:"dezenasSorteadasOrdemSorteio"`
}

type NumberFrequency struct {
    Number    int
    Frequency int
}

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

var rootCmd = &cobra.Command{
    Use:   "megasena",
    Short: "Capturando Informações para ganhar na Mega-Sena",
    Run: func(cmd *cobra.Command, args []string) {
        numberFrequencyMap := make(map[int]int)

        http.DefaultTransport.(*http.Transport).TLSClientConfig = &tls.Config{InsecureSkipVerify: true}

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

        for i := concursoAtual; i >= concursoAntigo; i-- {
            url := fmt.Sprintf("https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/%d", i)
            resp, err := http.Get(url)
            if err != nil {
                fmt.Println("Falha na captura das informações. Erro:", err)
                continue
            }
            body, _ := ioutil.ReadAll(resp.Body)
            resp.Body.Close()

            var response Response
            err = json.Unmarshal(body, &response)
            if err != nil {
                fmt.Println("Falha na captura das informações. Erro:", err)
                continue
            }

            for _, numberStr := range response.DezenasSorteadasOrdemSorteio {
                number, err := strconv.Atoi(numberStr)
                if err != nil {
                    fmt.Println("Falha na captura das informações. Erro:", err)
                    continue
                }
                numberFrequencyMap[number]++
            }

            bar.Increment()
        }

        p.Wait()

        numberFrequencies := make([]NumberFrequency, 0, len(numberFrequencyMap))
        for number, frequency := range numberFrequencyMap {
            numberFrequencies = append(numberFrequencies, NumberFrequency{Number: number, Frequency: frequency})
        }

        sort.Slice(numberFrequencies, func(i, j int) bool {
            return numberFrequencies[i].Frequency > numberFrequencies[j].Frequency
        })

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

        qtdeDezenas := 7
        qtdeJogos := 10

        rand.Seed(time.Now().UnixNano())
        var games [][]int
        for i := 0; i < qtdeJogos; {
            perm := rand.Perm(15)
            var game []int
            for _, v := range perm[:qtdeDezenas] {
                game = append(game, top15[v])
            }
            if !contains(games, game) {
                games = append(games, game)
                i++
            }
        }

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