# Mega Sena Number Generator

Este repositório contém dois programas que geram números para a Mega Sena com base na frequência de números sorteados em concursos anteriores. Os programas estão escritos em Go e TypeScript.

## Pré-requisitos

Para executar os programas, você precisa ter Go e Node.js instalados em seu sistema.

- Para instalar Go, siga as instruções na [página oficial de download do Go](https://golang.org/dl/).
- Para instalar Node.js, siga as instruções na [página oficial de download do Node.js](https://nodejs.org/en/download/).

Além disso, você precisa instalar as dependências do programa TypeScript. No diretório do programa TypeScript, execute o seguinte comando:

```bash
npm install
```

## Executando os programas

### Go

No diretório do programa Go, execute o seguinte comando:

```bash
go run main.go
```

### TypeScript

Primeiro, compile o programa TypeScript com o seguinte comando:

```bash
tsc main.ts
```

Em seguida, execute o programa com o seguinte comando:

```bash
node main.js
```

Os programas irão gerar 10 jogos únicos e escrevê-los no arquivo `jogos.json`. Cada jogo é um array de 6 números, e os números são escolhidos com base em suas frequências nos resultados dos concursos da Mega Sena.

## Aviso

Este programa é apenas para fins educacionais. Jogos da Mega Sena são jogos de azar e este programa não deve ser usado para jogar, pois as chances de perder são maiores do que as chances de ganhar. O autor deste código não tem qualquer responsabilidade se alguém usar este programa para criar jogos reais da Mega Sena.