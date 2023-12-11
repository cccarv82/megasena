# Mega Sena Number Generator

Este repositório contém três programas que geram números para a Mega Sena com base na frequência de números sorteados em concursos anteriores. Os programas estão escritos em Go, TypeScript e Python.

## Pré-requisitos

Para executar os programas, você precisa ter Go, Node.js e Python instalados em seu sistema.

- Para instalar Go, siga as instruções na [página oficial de download do Go](https://golang.org/dl/).
- Para instalar Node.js, siga as instruções na [página oficial de download do Node.js](https://nodejs.org/en/download/).
- Para instalar Python, siga as instruções na [página oficial de download do Python](https://www.python.org/downloads/).

### Instalando as bibliotecas

#### Python

No diretório do programa Python, crie um ambiente virtual e instale as dependências com os seguintes comandos:

```bash
python3 -m venv env
source env/bin/activate
pip install requests tqdm
```

#### Go

No diretório do programa Go, instale as dependências com o seguinte comando:

```bash
go get
```

#### TypeScript

No diretório do programa TypeScript, instale as dependências com o seguinte comando:

```bash
npm install
```

### Usando um ambiente virtual

Para criar um ambiente virtual, use o seguinte comando:

```bash
python3 -m venv env
```

Para ativar o ambiente virtual, use o seguinte comando:

```bash
source env/bin/activate
```

Para desativar o ambiente virtual, use o seguinte comando:

```bash
deactivate
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

### Python

No diretório do programa Python, execute o seguinte comando:

```bash
python main.py
```

Os programas irão gerar 10 jogos únicos e escrevê-los no arquivo `jogos.json`. Cada jogo é um array de 6 números, e os números são escolhidos com base em suas frequências nos resultados dos concursos da Mega Sena.

## Aviso

Este programa é apenas para fins educacionais. Jogos da Mega Sena são jogos de azar e este programa não deve ser usado para jogar, pois as chances de perder são maiores do que as chances de ganhar. O autor deste código não tem qualquer responsabilidade se alguém usar este programa para criar jogos reais da Mega Sena.